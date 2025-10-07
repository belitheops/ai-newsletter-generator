#!/usr/bin/env python3
"""
Manual newsletter generation script
Runs the complete newsletter workflow
"""

from scraper import NewsScraper
from deduplicator import StoryDeduplicator
from summarizer import ArticleSummarizer
from newsletter import NewsletterGenerator
from sendfox_client import SendFoxClient
from database import NewsletterDatabase
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("="*60)
    logger.info("STARTING MANUAL NEWSLETTER GENERATION")
    logger.info("="*60)
    
    # Initialize components
    logger.info("Initializing components...")
    scraper = NewsScraper()
    deduplicator = StoryDeduplicator()
    summarizer = ArticleSummarizer()
    newsletter_gen = NewsletterGenerator()
    sendfox = SendFoxClient()
    db = NewsletterDatabase()
    
    try:
        # Step 1: Scrape articles
        logger.info("\n" + "="*60)
        logger.info("STEP 1: Scraping articles from 10 AI/tech news sources...")
        logger.info("="*60)
        articles = scraper.scrape_all_sources()
        logger.info(f"✅ Successfully scraped {len(articles)} articles")
        
        if not articles:
            logger.warning("No articles found. Exiting.")
            return
        
        # Step 2: Deduplicate stories
        logger.info("\n" + "="*60)
        logger.info("STEP 2: Deduplicating and consolidating stories...")
        logger.info("="*60)
        unique_stories = deduplicator.deduplicate_stories(articles)
        logger.info(f"✅ Consolidated to {len(unique_stories)} unique stories")
        
        # Show deduplication stats
        stats = deduplicator.get_duplicate_statistics(articles, unique_stories)
        logger.info(f"   - Duplicates removed: {stats['duplicates_removed']}")
        logger.info(f"   - Consolidated stories: {stats['consolidated_stories']}")
        logger.info(f"   - Consolidation rate: {stats['consolidation_rate']:.1%}")
        
        # Step 3: Summarize articles
        logger.info("\n" + "="*60)
        logger.info("STEP 3: Generating AI summaries with OpenAI...")
        logger.info("="*60)
        summaries = []
        for i, story in enumerate(unique_stories, 1):
            logger.info(f"Summarizing story {i}/{len(unique_stories)}: {story.get('title', 'Unknown')[:60]}...")
            summary = summarizer.summarize_story(story)
            summaries.append(summary)
        
        logger.info(f"✅ Generated {len(summaries)} summaries")
        
        # Show summary stats
        summary_stats = summarizer.get_summary_statistics(summaries)
        logger.info(f"   - Successful summaries: {summary_stats['successful_summaries']}")
        logger.info(f"   - Average impact score: {summary_stats['average_impact_score']}/10")
        logger.info(f"   - High impact stories: {summary_stats['high_impact_stories']}")
        
        # Step 4: Generate newsletter
        logger.info("\n" + "="*60)
        logger.info("STEP 4: Generating newsletter HTML...")
        logger.info("="*60)
        newsletter_html = newsletter_gen.generate_newsletter(summaries)
        logger.info("✅ Newsletter HTML generated successfully")
        
        # Step 5: Save to database
        logger.info("\n" + "="*60)
        logger.info("STEP 5: Saving newsletter to database...")
        logger.info("="*60)
        newsletter_data = {
            'title': f"AI Daily Newsletter - {datetime.now().strftime('%B %d, %Y')}",
            'html_content': newsletter_html,
            'story_count': len(summaries),
            'created_at': datetime.now().isoformat(),
            'generation_method': 'manual'
        }
        newsletter_id = db.save_newsletter(newsletter_data)
        logger.info(f"✅ Newsletter saved with ID: {newsletter_id}")
        
        # Step 6: Send email (if configured)
        logger.info("\n" + "="*60)
        logger.info("STEP 6: Sending newsletter via SendFox...")
        logger.info("="*60)
        email_sent = sendfox.send_newsletter(newsletter_html, newsletter_data['title'])
        
        if email_sent:
            db.mark_newsletter_sent(newsletter_id)
            logger.info("✅ Newsletter sent successfully via email!")
        else:
            logger.warning("⚠️  Newsletter generated but email not sent (SendFox not configured or failed)")
        
        # Final summary
        logger.info("\n" + "="*60)
        logger.info("NEWSLETTER GENERATION COMPLETE!")
        logger.info("="*60)
        logger.info(f"Title: {newsletter_data['title']}")
        logger.info(f"Unique Stories: {len(summaries)}")
        logger.info(f"Newsletter ID: {newsletter_id}")
        logger.info(f"Email Sent: {'Yes' if email_sent else 'No'}")
        logger.info(f"View in archive or at newsletter ID: {newsletter_id}")
        logger.info("="*60)
        
        # Save plain text version for preview
        text_version = newsletter_gen.generate_text_version(summaries)
        with open('latest_newsletter.txt', 'w', encoding='utf-8') as f:
            f.write(text_version)
        logger.info("📄 Plain text version saved to: latest_newsletter.txt")
        
        # Save HTML version
        with open('latest_newsletter.html', 'w', encoding='utf-8') as f:
            f.write(newsletter_html)
        logger.info("📄 HTML version saved to: latest_newsletter.html")
        
    except Exception as e:
        logger.error(f"❌ Error during newsletter generation: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
