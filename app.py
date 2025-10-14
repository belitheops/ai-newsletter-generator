import streamlit as st
import pandas as pd
import threading
from datetime import datetime, timezone
import os
from scraper import NewsScraper
from deduplicator import StoryDeduplicator
from summarizer import ArticleSummarizer
from newsletter import NewsletterGenerator
from sendfox_client import SendFoxClient
from scheduler import NewsletterScheduler
from database import NewsletterDatabase
from feed_manager import FeedManager
from category_manager import CategoryManager
import json

# Initialize components
@st.cache_resource
def initialize_components():
    scraper = NewsScraper()
    deduplicator = StoryDeduplicator(similarity_threshold=0.6)
    summarizer = ArticleSummarizer()
    newsletter_gen = NewsletterGenerator()
    sendfox = SendFoxClient()
    db = NewsletterDatabase()
    scheduler = NewsletterScheduler(scraper, deduplicator, summarizer, newsletter_gen, sendfox, db)
    return scraper, deduplicator, summarizer, newsletter_gen, sendfox, db, scheduler

def main():
    st.title("🤖 AI Daily Newsletter Generator")
    st.markdown("Automated daily AI newsletter with intelligent story curation and email distribution")
    
    # Initialize components
    scraper, deduplicator, summarizer, newsletter_gen, sendfox, db, scheduler = initialize_components()
    
    # Start scheduler in background thread if not already running
    if 'scheduler_started' not in st.session_state:
        scheduler_thread = threading.Thread(target=scheduler.start, daemon=True)
        scheduler_thread.start()
        st.session_state.scheduler_started = True
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", [
        "Dashboard", 
        "Generate Newsletter", 
        "Newsletter Archive",
        "RSS Feed Management",
        "Category Management",
        "Configuration"
    ])
    
    if page == "Dashboard":
        show_dashboard(db)
    elif page == "Generate Newsletter":
        show_generate_newsletter(scraper, deduplicator, summarizer, newsletter_gen, sendfox, db)
    elif page == "Newsletter Archive":
        show_newsletter_archive(db)
    elif page == "RSS Feed Management":
        show_feed_management(scraper)
    elif page == "Category Management":
        show_category_management(summarizer)
    elif page == "Configuration":
        show_configuration()

def show_dashboard(db):
    st.header("📊 Dashboard")
    
    # Status indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("API Status", "✅ Connected" if os.getenv("OPENAI_API_KEY") else "❌ No API Key")
    
    with col2:
        st.metric("SendFox Status", "✅ Connected" if os.getenv("SENDFOX_API_TOKEN") else "❌ No Token")
    
    with col3:
        newsletters = db.get_all_newsletters()
        st.metric("Total Newsletters", len(newsletters))
    
    with col4:
        today_newsletters = [n for n in db.get_all_newsletters() 
                           if n['created_at'].startswith(datetime.now().strftime('%Y-%m-%d'))]
        st.metric("Today's Newsletters", len(today_newsletters))
    
    # Recent activity
    st.subheader("Recent Activity")
    recent_newsletters = db.get_recent_newsletters(5)
    if recent_newsletters:
        df = pd.DataFrame(recent_newsletters)
        df['created_at'] = pd.to_datetime(df['created_at'])
        st.dataframe(df[['title', 'created_at', 'story_count', 'email_sent']])
    else:
        st.info("No newsletters generated yet.")
    
    # Next scheduled run
    st.subheader("⏰ Scheduling")
    st.info("Next newsletter will be generated at 7:00 AM daily")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.text(f"Current time: {current_time}")

def show_generate_newsletter(scraper, deduplicator, summarizer, newsletter_gen, sendfox, db):
    st.header("🔧 Generate Newsletter")
    
    if st.button("🚀 Generate Newsletter Now", type="primary"):
        generate_newsletter_workflow(scraper, deduplicator, summarizer, newsletter_gen, sendfox, db)

def generate_newsletter_workflow(scraper, deduplicator, summarizer, newsletter_gen, sendfox, db):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Scrape articles
        status_text.text("🔍 Scraping articles from 10 AI/tech news sources...")
        progress_bar.progress(0.10)
        articles = scraper.scrape_all_sources()
        st.success(f"✅ Scraped {len(articles)} articles")
        
        # Step 2: Deduplicate stories
        status_text.text("🔄 Deduplicating and consolidating stories...")
        progress_bar.progress(0.30)
        unique_stories = deduplicator.deduplicate_stories(articles)
        st.success(f"✅ Consolidated to {len(unique_stories)} unique stories")
        
        # Step 2.5: Limit stories to process (optimize performance)
        MAX_STORIES_TO_SUMMARIZE = 15  # Only summarize top candidates to save time
        stories_to_process = unique_stories[:MAX_STORIES_TO_SUMMARIZE]
        if len(unique_stories) > MAX_STORIES_TO_SUMMARIZE:
            st.info(f"📊 Processing {MAX_STORIES_TO_SUMMARIZE} most recent stories from {len(unique_stories)} total")
        
        # Step 3: Summarize articles
        status_text.text("📝 Summarizing articles with OpenAI...")
        progress_bar.progress(0.50)
        summaries = []
        for i, story in enumerate(stories_to_process):
            summary = summarizer.summarize_story(story)
            summaries.append(summary)
            progress_bar.progress(0.50 + (i + 1) / len(stories_to_process) * 0.25)
        
        st.success(f"✅ Generated {len(summaries)} summaries")
        
        # Step 3.5: Select top 12 stories by impact score
        status_text.text("🎯 Selecting top stories by impact...")
        progress_bar.progress(0.80)
        MAX_STORIES = 12
        if len(summaries) > MAX_STORIES:
            sorted_summaries = sorted(summaries, key=lambda x: x.get('impact_score', 0), reverse=True)
            top_summaries = sorted_summaries[:MAX_STORIES]
            st.info(f"📊 Selected top {MAX_STORIES} stories from {len(summaries)} (by impact score)")
        else:
            top_summaries = summaries
        
        # Step 4: Generate newsletter
        status_text.text("📄 Generating newsletter HTML and Markdown...")
        progress_bar.progress(0.85)
        newsletter_html = newsletter_gen.generate_newsletter(top_summaries)
        newsletter_markdown = newsletter_gen.generate_markdown(top_summaries)
        
        # Step 5: Save to database
        newsletter_data = {
            'title': f"AI Newsletter - {datetime.now().strftime('%B %d, %Y')}",
            'html_content': newsletter_html,
            'markdown_content': newsletter_markdown,
            'story_count': len(top_summaries),
            'created_at': datetime.now().isoformat()
        }
        newsletter_id = db.save_newsletter(newsletter_data)
        
        # Step 6: Send email
        status_text.text("📧 Sending email via SendFox...")
        progress_bar.progress(0.95)
        email_sent = sendfox.send_newsletter(newsletter_html, newsletter_data['title'])
        
        if email_sent:
            db.mark_newsletter_sent(newsletter_id)
            st.success("✅ Newsletter sent successfully!")
        else:
            st.warning("⚠️ Newsletter generated but email sending failed")
        
        progress_bar.progress(1.0)
        status_text.text("✅ Newsletter generation complete!")
        
        # Display the newsletter
        st.subheader("📰 Generated Newsletter")
        
        # Add export buttons
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            st.download_button(
                label="📥 Export HTML",
                data=newsletter_html,
                file_name=f"newsletter_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                help="Download the newsletter as a standalone HTML file"
            )
        with col2:
            st.download_button(
                label="📝 Export Markdown",
                data=newsletter_markdown,
                file_name=f"newsletter_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                help="Download the newsletter as a Markdown file"
            )
        
        st.components.v1.html(newsletter_html, height=600, scrolling=True)
        
    except Exception as e:
        st.error(f"❌ Error generating newsletter: {str(e)}")
        progress_bar.progress(0)
        status_text.text("❌ Generation failed")

def show_newsletter_archive(db):
    st.header("📚 Newsletter Archive")
    
    newsletters = db.get_all_newsletters()
    
    if not newsletters:
        st.info("No newsletters in archive yet.")
        return
    
    # Display newsletters
    for newsletter in newsletters:
        with st.expander(f"📅 {newsletter['title']} ({newsletter['created_at'][:10]})"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Stories", newsletter['story_count'])
            with col2:
                st.metric("Email Sent", "✅ Yes" if newsletter.get('email_sent') else "❌ No")
            with col3:
                st.metric("Created", newsletter['created_at'][:16])
            
            # Action buttons
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button(f"👁️ View", key=f"view_{newsletter['id']}"):
                    st.components.v1.html(newsletter['html_content'], height=600, scrolling=True)
            with col_b:
                st.download_button(
                    label="📥 Export HTML",
                    data=newsletter['html_content'],
                    file_name=f"newsletter_{newsletter['created_at'][:10]}.html",
                    mime="text/html",
                    key=f"download_html_{newsletter['id']}",
                    help="Download this newsletter as HTML"
                )
            with col_c:
                # Check if markdown content exists (backward compatibility)
                if 'markdown_content' in newsletter and newsletter['markdown_content']:
                    st.download_button(
                        label="📝 Export Markdown",
                        data=newsletter['markdown_content'],
                        file_name=f"newsletter_{newsletter['created_at'][:10]}.md",
                        mime="text/markdown",
                        key=f"download_md_{newsletter['id']}",
                        help="Download this newsletter as Markdown"
                    )
                else:
                    st.caption("Markdown not available")

def show_feed_management(scraper):
    st.header("📡 RSS Feed Management")
    st.markdown("Manage your news sources - add, edit, delete, or disable RSS feeds")
    
    feed_manager = FeedManager()
    
    # Tabs for different operations
    tab1, tab2 = st.tabs(["📋 All Feeds", "➕ Add New Feed"])
    
    with tab1:
        st.subheader("Current RSS Feeds")
        feeds = feed_manager.get_all_feeds()
        
        if not feeds:
            st.info("No RSS feeds configured. Add your first feed in the 'Add New Feed' tab.")
        else:
            # Display stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Feeds", len(feeds))
            with col2:
                enabled_count = len([f for f in feeds if f.get('enabled', True)])
                st.metric("Enabled Feeds", enabled_count)
            with col3:
                categories = feed_manager.get_categories()
                st.metric("Categories", len(categories))
            
            st.markdown("---")
            
            # Display feeds by category
            categories = feed_manager.get_categories()
            
            for category in categories:
                st.subheader(f"📂 {category}")
                category_feeds = feed_manager.get_feeds_by_category(category)
                
                for feed in category_feeds:
                    with st.expander(f"{'✅' if feed.get('enabled') else '❌'} {feed['name']}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.text(f"URL: {feed['url']}")
                            st.text(f"ID: {feed['id']}")
                            if 'added_at' in feed:
                                st.caption(f"Added: {feed['added_at'][:10]}")
                        
                        with col2:
                            # Toggle enable/disable
                            if st.button(
                                "🔄 Toggle" if feed.get('enabled') else "🔄 Enable",
                                key=f"toggle_{feed['id']}"
                            ):
                                if feed_manager.toggle_feed(feed['id']):
                                    scraper.reload_feeds()
                                    st.success(f"{'Disabled' if feed.get('enabled') else 'Enabled'} {feed['name']}")
                                    st.rerun()
                            
                            # Delete button
                            if st.button("🗑️ Delete", key=f"delete_{feed['id']}", type="secondary"):
                                if feed_manager.delete_feed(feed['id']):
                                    scraper.reload_feeds()
                                    st.success(f"Deleted {feed['name']}")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete feed")
    
    with tab2:
        st.subheader("Add New RSS Feed")
        
        with st.form("add_feed_form"):
            new_name = st.text_input("Feed Name", placeholder="e.g., AI Weekly News")
            new_url = st.text_input("RSS Feed URL", placeholder="https://example.com/feed.xml")
            new_category = st.selectbox(
                "Category", 
                ["Tech News", "Research", "AI Industry", "Business", "Other"] + feed_manager.get_categories(),
                index=0
            )
            new_enabled = st.checkbox("Enabled", value=True)
            
            submitted = st.form_submit_button("➕ Add Feed")
            
            if submitted:
                if not new_name or not new_url:
                    st.error("Please provide both name and URL")
                elif not new_url.startswith(('http://', 'https://')):
                    st.error("URL must start with http:// or https://")
                else:
                    if feed_manager.add_feed(new_name, new_url, new_category, new_enabled):
                        scraper.reload_feeds()
                        st.success(f"✅ Added {new_name} successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Failed to add feed. A feed with this name may already exist.")

def show_category_management(summarizer):
    st.header("🏷️ Category Management")
    st.markdown("Manage newsletter categories - add, edit, reorder, or delete categories for story organization")
    
    category_manager = CategoryManager()
    
    # Tabs for different operations
    tab1, tab2 = st.tabs(["📋 All Categories", "➕ Add New Category"])
    
    with tab1:
        st.subheader("Current Categories")
        categories = category_manager.get_all_categories()
        
        if not categories:
            st.info("No categories configured. Add your first category in the 'Add New Category' tab.")
        else:
            # Display stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Categories", len(categories))
            with col2:
                enabled_count = len([c for c in categories if c.get('enabled', True)])
                st.metric("Enabled Categories", enabled_count)
            with col3:
                st.metric("Priority Range", f"1 - {max([c.get('priority', 1) for c in categories])}")
            
            st.markdown("---")
            
            # Display categories in priority order
            st.subheader("📂 Categories (in priority order)")
            
            for category in categories:
                with st.expander(f"{category['emoji']} {'✅' if category.get('enabled') else '❌'} {category['name']} (Priority: {category.get('priority', 999)})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.text(f"ID: {category['id']}")
                        st.text(f"Emoji: {category['emoji']}")
                        st.text(f"Priority: {category.get('priority', 999)}")
                        if 'added_at' in category:
                            st.caption(f"Added: {category['added_at'][:10]}")
                    
                    with col2:
                        # Toggle enable/disable
                        if st.button(
                            "🔄 Toggle",
                            key=f"toggle_cat_{category['id']}"
                        ):
                            if category_manager.toggle_category(category['id']):
                                summarizer.reload_categories()
                                st.success(f"{'Disabled' if category.get('enabled') else 'Enabled'} {category['name']}")
                                st.rerun()
                        
                        # Delete button (protect "Other" category)
                        if category['id'] != 'other':
                            if st.button("🗑️ Delete", key=f"delete_cat_{category['id']}", type="secondary"):
                                if category_manager.delete_category(category['id']):
                                    summarizer.reload_categories()
                                    st.success(f"Deleted {category['name']}")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete category")
                        else:
                            st.caption("Cannot delete 'Other'")
                    
                    # Edit section
                    st.markdown("---")
                    st.markdown("**Edit Category:**")
                    with st.form(f"edit_cat_{category['id']}"):
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            new_name = st.text_input("Name", value=category['name'], key=f"name_{category['id']}")
                        with col_b:
                            new_emoji = st.text_input("Emoji", value=category['emoji'], key=f"emoji_{category['id']}")
                        with col_c:
                            new_priority = st.number_input("Priority", value=category.get('priority', 999), min_value=1, max_value=999, key=f"priority_{category['id']}")
                        
                        if st.form_submit_button("💾 Update"):
                            if category_manager.update_category(category['id'], name=new_name, emoji=new_emoji, priority=new_priority):
                                summarizer.reload_categories()
                                st.success(f"✅ Updated {new_name}")
                                st.rerun()
                            else:
                                st.error("Failed to update category")
    
    with tab2:
        st.subheader("Add New Category")
        
        with st.form("add_category_form"):
            new_name = st.text_input("Category Name", placeholder="e.g., Data Science")
            
            col1, col2 = st.columns(2)
            with col1:
                new_emoji = st.text_input("Emoji", value="📁", placeholder="e.g., 📊")
            with col2:
                # Get max priority excluding "Other" category (which should always be 999)
                non_other_categories = [c for c in categories if c.get('id') != 'other']
                max_priority = max([c.get('priority', 0) for c in non_other_categories], default=0)
                new_priority = st.number_input("Priority", value=min(max_priority + 1, 998), min_value=1, max_value=998)
            
            st.info("Lower priority numbers appear first in newsletters. 'Other' category always appears last.")
            
            submitted = st.form_submit_button("➕ Add Category")
            
            if submitted:
                if not new_name:
                    st.error("Please provide a category name")
                else:
                    if category_manager.add_category(new_name, new_emoji, new_priority):
                        summarizer.reload_categories()
                        st.success(f"✅ Added {new_emoji} {new_name} successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Failed to add category. A category with this name may already exist.")

def show_configuration():
    st.header("⚙️ Configuration")
    
    st.subheader("API Keys")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    sendfox_token = os.getenv("SENDFOX_API_TOKEN", "")
    
    st.text_input("OpenAI API Key", value="***" if openai_key else "", 
                 help="Set via OPENAI_API_KEY environment variable", disabled=True)
    st.text_input("SendFox API Token", value="***" if sendfox_token else "", 
                 help="Set via SENDFOX_API_TOKEN environment variable", disabled=True)
    
    st.subheader("News Sources")
    sources = [
        "TechCrunch AI", "MIT News AI/ML", "AI News", "MIT Tech Review",
        "VentureBeat AI", "Wired AI", "Forbes AI", "OpenAI Blog",
        "ScienceDaily AI", "The Verge AI"
    ]
    
    for source in sources:
        st.checkbox(source, value=True, disabled=True, 
                   help="Source configuration is handled in scraper.py")
    
    st.subheader("Schedule Settings")
    st.info("Newsletter is automatically generated daily at 7:00 AM")
    st.text("To modify schedule, update scheduler.py")

if __name__ == "__main__":
    main()
