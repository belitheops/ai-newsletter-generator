import schedule
import time
import threading
from datetime import datetime
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the newsletter generation lock to prevent concurrent runs
from shared_resources import newsletter_generation_lock

class NewsletterScheduler:
    def __init__(self, scraper, deduplicator, summarizer, newsletter_gen, resend, db):
        self.scraper = scraper
        self.deduplicator = deduplicator
        self.summarizer = summarizer
        self.newsletter_gen = newsletter_gen
        self.resend = resend
        self.db = db
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def start(self):
        """Start the scheduler"""
        if self.running:
            logger.info("Scheduler is already running")
            return
        
        self.running = True
        logger.info("Starting newsletter scheduler...")
        
        # Schedule daily newsletter generation at 7 AM
        schedule.every().day.at("07:00").do(self._generate_daily_newsletter)
        
        # Log the next scheduled run
        next_run = schedule.next_run()
        logger.info(f"Next newsletter generation scheduled for: {next_run}")
        
        # Start the scheduler loop
        self._run_scheduler()

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        logger.info("Newsletter scheduler stopped")

    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Continue running even if there's an error

    def _generate_daily_newsletter(self):
        """Generate and send the daily newsletter"""
        logger.info("Starting daily newsletter generation...")
        
        # Acquire lock to prevent concurrent newsletter generation
        lock_acquired = newsletter_generation_lock.acquire(blocking=False)
        
        if not lock_acquired:
            logger.warning("⚠️ Newsletter generation already in progress (manual trigger). Skipping scheduled run.")
            return
        
        try:
            # Load newsletter configuration
            from newsletter_config import NewsletterConfigManager
            config_manager = NewsletterConfigManager()
            configs = config_manager.get_all_configs()
            
            # Use first enabled config or default
            config = next((c for c in configs if c.get('enabled', True)), configs[0] if configs else None)
            if not config:
                logger.error("No newsletter configuration found. Cannot generate newsletter.")
                return
            
            logger.info(f"Using newsletter config: {config['name']}")
            
            # Step 1: Scrape articles
            logger.info("Scraping articles from news sources...")
            articles = self.scraper.scrape_all_sources()
            logger.info(f"Scraped {len(articles)} articles")
            
            if not articles:
                logger.warning("No articles scraped. Skipping newsletter generation.")
                self._save_empty_newsletter("No articles found during scraping", config['name'])
                return
            
            # Step 2: Deduplicate stories
            logger.info("Deduplicating stories...")
            unique_stories = self.deduplicator.deduplicate_stories(articles)
            logger.info(f"Deduplicated to {len(unique_stories)} unique stories")
            
            if not unique_stories:
                logger.warning("No unique stories after deduplication. Skipping newsletter generation.")
                self._save_empty_newsletter("No unique stories after deduplication", config['name'])
                return
            
            # Step 3: Summarize articles
            logger.info("Summarizing articles...")
            summaries = []
            for i, story in enumerate(unique_stories):
                try:
                    summary = self.summarizer.summarize_story(story)
                    summaries.append(summary)
                    logger.info(f"Summarized story {i+1}/{len(unique_stories)}")
                except Exception as e:
                    logger.error(f"Error summarizing story {i+1}: {e}")
                    # Add the story without summary as fallback
                    story['summary'] = f"Summary generation failed: {str(e)}"
                    story['key_points'] = []
                    story['impact_score'] = 5
                    story['category'] = 'Other'
                    summaries.append(story)
            
            logger.info(f"Generated {len(summaries)} summaries")
            
            # Step 3.5: Select top stories by impact score (using config max_stories)
            MAX_STORIES = config.get('max_stories', 12)
            if len(summaries) > MAX_STORIES:
                sorted_summaries = sorted(summaries, key=lambda x: x.get('impact_score', 0), reverse=True)
                top_summaries = sorted_summaries[:MAX_STORIES]
                logger.info(f"Selected top {MAX_STORIES} stories from {len(summaries)} by impact score")
            else:
                top_summaries = summaries
            
            # Step 4: Generate newsletter
            logger.info("Generating newsletter HTML...")
            newsletter_title = f"{config['name']} - {datetime.now().strftime('%B %d, %Y')}"
            branding = config.get('branding', {})
            cta_buttons = config.get('cta_buttons', [])
            newsletter_html = self.newsletter_gen.generate_newsletter(top_summaries, title=newsletter_title, branding=branding, cta_buttons=cta_buttons)
            
            # Step 5: Save to database
            newsletter_data = {
                'title': newsletter_title,
                'html_content': newsletter_html,
                'story_count': len(top_summaries),
                'created_at': datetime.now().isoformat(),
                'generation_method': 'scheduled'
            }
            newsletter_id = self.db.save_newsletter(newsletter_data)
            logger.info(f"Newsletter saved to database with ID: {newsletter_id}")
            
            # Step 6: Send email
            logger.info("Sending newsletter via Resend...")
            # Note: Email sending is disabled until recipient list is configured
            email_sent = False
            # email_sent = self.resend.send_newsletter(newsletter_html, newsletter_data['title'], to_emails=['your@email.com'])
            
            if email_sent:
                self.db.mark_newsletter_sent(newsletter_id)
                logger.info("Daily newsletter sent successfully!")
            else:
                logger.warning("Newsletter generated but email sending failed")
            
            # Log completion
            logger.info(f"Daily newsletter generation completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"Error during daily newsletter generation: {e}")
            self._save_error_newsletter(str(e))
        finally:
            # Always release the lock
            newsletter_generation_lock.release()

    def _save_empty_newsletter(self, reason: str, config_name: str = "AI Daily Newsletter"):
        """Save a record when no newsletter could be generated"""
        try:
            newsletter_data = {
                'title': f"{config_name} - {datetime.now().strftime('%B %d, %Y')} (Empty)",
                'html_content': self.newsletter_gen._generate_empty_newsletter(),
                'story_count': 0,
                'created_at': datetime.now().isoformat(),
                'generation_method': 'scheduled',
                'error_reason': reason
            }
            self.db.save_newsletter(newsletter_data)
            logger.info(f"Empty newsletter record saved: {reason}")
        except Exception as e:
            logger.error(f"Error saving empty newsletter record: {e}")

    def _save_error_newsletter(self, error_message: str):
        """Save a record when newsletter generation fails"""
        try:
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Newsletter Generation Error</title>
            </head>
            <body>
                <h1>Newsletter Generation Failed</h1>
                <p>The daily newsletter could not be generated due to an error:</p>
                <p><strong>{error_message}</strong></p>
                <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </body>
            </html>
            """
            
            newsletter_data = {
                'title': f"AI Daily Newsletter - {datetime.now().strftime('%B %d, %Y')} (Error)",
                'html_content': error_html,
                'story_count': 0,
                'created_at': datetime.now().isoformat(),
                'generation_method': 'scheduled',
                'error_reason': error_message
            }
            self.db.save_newsletter(newsletter_data)
            logger.info(f"Error newsletter record saved: {error_message}")
        except Exception as e:
            logger.error(f"Error saving error newsletter record: {e}")

    def get_next_run_time(self) -> Optional[datetime]:
        """Get the next scheduled run time"""
        next_run = schedule.next_run()
        return next_run

    def force_run(self):
        """Force run the newsletter generation immediately"""
        logger.info("Forcing newsletter generation...")
        threading.Thread(target=self._generate_daily_newsletter, daemon=True).start()

    def get_schedule_info(self) -> dict:
        """Get information about the current schedule"""
        jobs = schedule.jobs
        next_run = schedule.next_run()
        
        return {
            'total_jobs': len(jobs),
            'next_run': next_run.isoformat() if next_run else None,
            'scheduler_running': self.running,
            'jobs': [
                {
                    'job': str(job),
                    'next_run': job.next_run.isoformat() if job.next_run else None
                }
                for job in jobs
            ]
        }
