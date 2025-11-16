import streamlit as st
import pandas as pd
import threading
from datetime import datetime, timezone
import os
from scraper import NewsScraper
from deduplicator import StoryDeduplicator
from summarizer import ArticleSummarizer
from newsletter import NewsletterGenerator
from resend_client import ResendClient
from scheduler import NewsletterScheduler
from database import NewsletterDatabase
from feed_manager import FeedManager
from category_manager import CategoryManager
from newsletter_config import NewsletterConfigManager
from shared_resources import newsletter_generation_lock
from auth import AuthManager
import json

# Initialize components
@st.cache_resource
def initialize_components():
    scraper = NewsScraper()
    deduplicator = StoryDeduplicator(similarity_threshold=0.6)
    summarizer = ArticleSummarizer()
    newsletter_gen = NewsletterGenerator()
    resend = ResendClient()
    db = NewsletterDatabase()
    scheduler = NewsletterScheduler(scraper, deduplicator, summarizer, newsletter_gen, resend, db)
    return scraper, deduplicator, summarizer, newsletter_gen, resend, db, scheduler

@st.cache_resource
def get_auth_manager():
    return AuthManager()

def show_login_page():
    st.title("🔐 Login")
    st.markdown("Welcome to the AI Newsletter Generator")
    
    st.subheader("Login to your account")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                auth = get_auth_manager()
                verified, user_info = auth.verify_user(username, password)
                
                if verified:
                    st.session_state.authenticated = True
                    st.session_state.user = user_info
                    st.success(f"Welcome back, {user_info['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

def show_user_profile():
    st.header("👤 User Profile")
    
    if 'user' not in st.session_state:
        st.error("Not logged in")
        return
    
    user = st.session_state.user
    auth = get_auth_manager()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Profile Info")
        st.write(f"**Username:** {user['username']}")
        st.write(f"**Email:** {user.get('email', 'Not set')}")
        st.write(f"**Full Name:** {user.get('full_name', 'Not set')}")
        st.write(f"**Member Since:** {user.get('created_at', 'Unknown')[:10]}")
        st.write(f"**Last Login:** {user.get('last_login', 'Unknown')[:10]}")
    
    with col2:
        st.subheader("Update Profile")
        with st.form("update_profile_form"):
            new_email = st.text_input("Email", value=user.get('email', ''))
            new_full_name = st.text_input("Full Name", value=user.get('full_name', ''))
            update_submit = st.form_submit_button("Update Profile")
            
            if update_submit:
                success, message = auth.update_user(
                    user['username'],
                    email=new_email,
                    full_name=new_full_name
                )
                if success:
                    st.success(message)
                    updated_user = auth.get_user(user['username'])
                    if updated_user:
                        st.session_state.user = updated_user
                        st.rerun()
                else:
                    st.error(message)
        
        st.subheader("Change Password")
        with st.form("change_password_form"):
            old_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")
            password_submit = st.form_submit_button("Change Password")
            
            if password_submit:
                if not old_password or not new_password:
                    st.error("Please fill in all fields")
                elif new_password != confirm_new_password:
                    st.error("New passwords do not match")
                else:
                    success, message = auth.change_password(
                        user['username'],
                        old_password,
                        new_password
                    )
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Show login page if not authenticated
    if not st.session_state.authenticated:
        show_login_page()
        return
    
    # Authenticated user content
    st.title("🤖 AI Daily Newsletter Generator")
    st.markdown("Automated daily AI newsletter with intelligent story curation and email distribution")
    
    # Initialize components
    scraper, deduplicator, summarizer, newsletter_gen, resend, db, scheduler = initialize_components()
    
    # Start scheduler in background thread if not already running
    if 'scheduler_started' not in st.session_state:
        scheduler_thread = threading.Thread(target=scheduler.start, daemon=True)
        scheduler_thread.start()
        st.session_state.scheduler_started = True
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # User info and logout button
    if st.session_state.user:
        st.sidebar.markdown(f"**Logged in as:** {st.session_state.user['username']}")
        if st.sidebar.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox("Choose a page", [
        "Dashboard", 
        "Generate Newsletter", 
        "Newsletter Archive",
        "Newsletter Management",
        "RSS Feed Management",
        "Category Management",
        "User Profile",
        "Configuration"
    ])
    
    if page == "Dashboard":
        show_dashboard(db)
    elif page == "Generate Newsletter":
        show_generate_newsletter(scraper, deduplicator, summarizer, newsletter_gen, resend, db)
    elif page == "Newsletter Archive":
        show_newsletter_archive(db)
    elif page == "Newsletter Management":
        show_newsletter_management(scraper, summarizer)
    elif page == "RSS Feed Management":
        show_feed_management(scraper)
    elif page == "Category Management":
        show_category_management(summarizer)
    elif page == "User Profile":
        show_user_profile()
    elif page == "Configuration":
        show_configuration()

def show_dashboard(db):
    st.header("📊 Dashboard")
    
    # Status indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("API Status", "✅ Connected" if os.getenv("OPENAI_API_KEY") else "❌ No API Key")
    
    with col2:
        resend_client = ResendClient()
        resend_status = resend_client.get_status()
        st.metric("Resend Status", "✅ Connected" if resend_status['ready'] else "❌ Not Configured")
    
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

def show_generate_newsletter(scraper, deduplicator, summarizer, newsletter_gen, resend, db):
    st.header("🔧 Generate Newsletter")
    
    # Newsletter selection
    config_manager = NewsletterConfigManager()
    configs = config_manager.get_all_configs()
    
    config_options = {c['id']: c['name'] for c in configs}
    selected_config_id = st.selectbox(
        "📰 Select Newsletter",
        options=list(config_options.keys()),
        format_func=lambda x: config_options[x],
        help="Choose which newsletter configuration to generate"
    )
    
    # Show config details
    selected_config = config_manager.get_config_by_id(selected_config_id)
    if selected_config:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Max Stories", selected_config.get('max_stories', 12))
        with col2:
            feed_count = len(selected_config.get('feed_ids', [])) or "All"
            st.metric("RSS Feeds", feed_count)
        with col3:
            cat_count = len(selected_config.get('category_ids', [])) or "All"
            st.metric("Categories", cat_count)
        
        if selected_config.get('description'):
            st.info(f"ℹ️ {selected_config['description']}")
    
    if st.button("🚀 Generate Newsletter Now", type="primary"):
        generate_newsletter_workflow(scraper, deduplicator, summarizer, newsletter_gen, resend, db, selected_config_id)

def generate_newsletter_workflow(scraper, deduplicator, summarizer, newsletter_gen, resend, db, config_id=None):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Acquire lock to prevent concurrent newsletter generation
    # This ensures thread-safety for database writes and SendFox sends
    lock_acquired = newsletter_generation_lock.acquire(blocking=False)
    
    if not lock_acquired:
        st.warning("⚠️ Another newsletter generation is in progress. Please wait...")
        return
    
    try:
        # Load configuration
        config_manager = NewsletterConfigManager()
        feed_manager = FeedManager()
        category_manager = CategoryManager()
        
        config = config_manager.get_config_by_id(config_id) if config_id else config_manager.get_all_configs()[0]
        # Get feeds for this newsletter
        all_feeds = feed_manager.get_all_feeds()
        config_feeds = config_manager.get_config_feeds(config['id'], all_feeds)
        
        # Step 1: Scrape articles from selected feeds
        status_text.text(f"🔍 Scraping articles from {len(config_feeds)} selected sources...")
        progress_bar.progress(0.10)
        
        # Build custom sources dict for this newsletter (thread-safe - no mutation)
        custom_sources = {
            f['name']: {
                'type': f.get('type', 'rss'),
                'url': f['url'],
                'category': f.get('category', 'Other')
            }
            for f in config_feeds
        }
        articles = scraper.scrape_all_sources(custom_sources=custom_sources)
        
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
        
        # Get categories for this newsletter
        all_categories = category_manager.get_all_categories()
        config_category_names = config_manager.get_config_categories(config['id'], all_categories)
        
        # Step 3: Summarize articles with config-specific categories (thread-safe - no mutation)
        status_text.text("📝 Summarizing articles with OpenAI...")
        progress_bar.progress(0.50)
        
        custom_categories = config_category_names + ['Other']
        
        summaries = []
        for i, story in enumerate(stories_to_process):
            summary = summarizer.summarize_story(story, custom_categories=custom_categories)
            summaries.append(summary)
            progress_bar.progress(0.50 + (i + 1) / len(stories_to_process) * 0.25)
        
        st.success(f"✅ Generated {len(summaries)} summaries")
        
        # Step 3.5: Select top stories by impact score
        status_text.text("🎯 Selecting top stories by impact...")
        progress_bar.progress(0.80)
        MAX_STORIES = config.get('max_stories', 12)
        if len(summaries) > MAX_STORIES:
            sorted_summaries = sorted(summaries, key=lambda x: x.get('impact_score', 0), reverse=True)
            top_summaries = sorted_summaries[:MAX_STORIES]
            st.info(f"📊 Selected top {MAX_STORIES} stories from {len(summaries)} (by impact score)")
        else:
            top_summaries = summaries
        
        # Step 4: Generate newsletter
        status_text.text("📄 Generating newsletter HTML and Markdown...")
        progress_bar.progress(0.85)
        
        # Create newsletter title
        newsletter_title = f"{config['name']} - {datetime.now().strftime('%B %d, %Y')}"
        
        # Get branding settings and CTA buttons from config
        branding = config.get('branding', {})
        cta_buttons = config.get('cta_buttons', [])
        
        newsletter_html = newsletter_gen.generate_newsletter(top_summaries, title=newsletter_title, branding=branding, cta_buttons=cta_buttons)
        newsletter_markdown = newsletter_gen.generate_markdown(top_summaries, title=newsletter_title, cta_buttons=cta_buttons)
        
        # Step 5: Save to database
        newsletter_data = {
            'title': newsletter_title,
            'html_content': newsletter_html,
            'markdown_content': newsletter_markdown,
            'story_count': len(top_summaries),
            'created_at': datetime.now().isoformat(),
            'config_id': config['id'],
            'config_name': config['name']
        }
        newsletter_id = db.save_newsletter(newsletter_data)
        
        # Step 6: Send email
        status_text.text("📧 Sending email via Resend...")
        progress_bar.progress(0.95)
        # Note: Resend requires a list of recipients. Add your email addresses here.
        # For now, using a test mode that won't actually send
        email_sent = False  # Set to True when you configure recipient emails
        # email_sent = resend.send_newsletter(newsletter_html, newsletter_data['title'], to_emails=['your@email.com'])
        
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
    finally:
        # Always release the lock
        newsletter_generation_lock.release()

def show_newsletter_archive(db):
    st.header("📚 Newsletter Archive")
    
    newsletters = db.get_all_newsletters()
    
    if not newsletters:
        st.info("No newsletters in archive yet.")
        return
    
    # Display newsletters
    for newsletter in newsletters:
        # Show config name if available
        config_info = f" | {newsletter['config_name']}" if newsletter.get('config_name') else ""
        with st.expander(f"📅 {newsletter['title']} ({newsletter['created_at'][:10]}){config_info}"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Stories", newsletter['story_count'])
            with col2:
                st.metric("Email Sent", "✅ Yes" if newsletter.get('email_sent') else "❌ No")
            with col3:
                st.metric("Created", newsletter['created_at'][:16])
            with col4:
                if newsletter.get('config_name'):
                    st.metric("Newsletter", newsletter['config_name'])
                else:
                    st.caption("Legacy")
            
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
            
            # Get categories from Category Management system
            category_manager = CategoryManager()
            all_categories_data = category_manager.get_all_categories()
            
            # Extract category names and add existing feed categories for backward compatibility
            category_names = [cat['name'] for cat in all_categories_data if cat.get('enabled', True)]
            existing_feed_categories = feed_manager.get_categories()
            
            # Combine and deduplicate
            all_categories = sorted(list(set(category_names + existing_feed_categories)))
            
            if not all_categories:
                st.warning("⚠️ No categories available. Please add categories in the Category Management page first.")
                all_categories = ["Other"]  # Fallback
            
            new_category = st.selectbox(
                "Category", 
                all_categories,
                index=0,
                help="Categories are managed in the Category Management page"
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

def show_newsletter_management(scraper, summarizer):
    st.header("📰 Newsletter Management")
    st.markdown("Create and manage multiple newsletter configurations with different sources and categories")
    
    config_manager = NewsletterConfigManager()
    feed_manager = FeedManager()
    category_manager = CategoryManager()
    
    # Tabs for different operations
    tab1, tab2 = st.tabs(["📋 All Newsletters", "➕ Create Newsletter"])
    
    with tab1:
        st.subheader("Current Newsletter Configurations")
        configs = config_manager.get_all_configs()
        
        if not configs:
            st.info("No newsletter configurations. Create your first newsletter in the 'Create Newsletter' tab.")
        else:
            # Display stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Newsletters", len(configs))
            with col2:
                enabled_count = len([c for c in configs if c.get('enabled', True)])
                st.metric("Enabled Newsletters", enabled_count)
            with col3:
                scheduled_count = len([c for c in configs if c.get('schedule_enabled', False)])
                st.metric("Scheduled", scheduled_count)
            
            st.markdown("---")
            
            # Display newsletters
            for config in configs:
                with st.expander(f"{'✅' if config.get('enabled') else '❌'} {config['name']}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Description:** {config.get('description', 'No description')}")
                        st.text(f"ID: {config['id']}")
                        st.text(f"Max Stories: {config.get('max_stories', 12)}")
                        
                        # Show feeds
                        feed_ids = config.get('feed_ids', [])
                        if not feed_ids:
                            st.caption("📡 Feeds: All enabled feeds")
                        else:
                            all_feeds = feed_manager.get_all_feeds()
                            feed_names = [f['name'] for f in all_feeds if f['id'] in feed_ids]
                            st.caption(f"📡 Feeds: {', '.join(feed_names)}")
                        
                        # Show categories
                        cat_ids = config.get('category_ids', [])
                        if not cat_ids:
                            st.caption("🏷️ Categories: All enabled categories")
                        else:
                            all_cats = category_manager.get_all_categories()
                            cat_names = [c['name'] for c in all_cats if c['id'] in cat_ids]
                            st.caption(f"🏷️ Categories: {', '.join(cat_names)}")
                        
                        if config.get('schedule_enabled'):
                            st.caption(f"⏰ Schedule: Daily at {config.get('schedule_time', '07:00')}")
                        else:
                            st.caption("⏰ Schedule: Manual only")
                        
                        if 'created_at' in config:
                            st.caption(f"Created: {config['created_at'][:10]}")
                    
                    with col2:
                        # Toggle enable/disable
                        if st.button("🔄 Toggle", key=f"toggle_nl_{config['id']}"):
                            if config_manager.toggle_config(config['id']):
                                st.success(f"{'Disabled' if config.get('enabled') else 'Enabled'} {config['name']}")
                                st.rerun()
                        
                        # Delete button (protect if only one)
                        if len(configs) > 1:
                            if st.button("🗑️ Delete", key=f"delete_nl_{config['id']}", type="secondary"):
                                if config_manager.delete_config(config['id']):
                                    st.success(f"Deleted {config['name']}")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete newsletter")
                        else:
                            st.caption("Cannot delete only config")
                    
                    # Edit section
                    st.markdown("---")
                    st.markdown("**Edit Newsletter:**")
                    with st.form(f"edit_nl_{config['id']}"):
                        new_name = st.text_input("Name", value=config['name'], key=f"nl_name_{config['id']}")
                        new_desc = st.text_input("Description", value=config.get('description', ''), key=f"nl_desc_{config['id']}")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            new_max = st.number_input("Max Stories", value=config.get('max_stories', 12), min_value=1, max_value=50, key=f"nl_max_{config['id']}")
                        with col_b:
                            new_time = st.text_input("Schedule Time", value=config.get('schedule_time', '07:00'), key=f"nl_time_{config['id']}")
                        
                        # Feed selection
                        all_feeds = feed_manager.get_all_feeds()
                        feed_options = {f['id']: f['name'] for f in all_feeds}
                        current_feed_ids = config.get('feed_ids', [])
                        selected_feeds = st.multiselect(
                            "RSS Feeds (empty = all)",
                            options=list(feed_options.keys()),
                            default=current_feed_ids,
                            format_func=lambda x: feed_options[x],
                            key=f"nl_feeds_{config['id']}"
                        )
                        
                        # Category selection
                        all_cats = category_manager.get_all_categories()
                        cat_options = {c['id']: c['name'] for c in all_cats}
                        current_cat_ids = config.get('category_ids', [])
                        selected_cats = st.multiselect(
                            "Categories (empty = all)",
                            options=list(cat_options.keys()),
                            default=current_cat_ids,
                            format_func=lambda x: cat_options[x],
                            key=f"nl_cats_{config['id']}"
                        )
                        
                        # Branding customization
                        st.markdown("**🎨 Branding Options:**")
                        branding = config.get('branding', {})
                        
                        col_brand1, col_brand2 = st.columns(2)
                        with col_brand1:
                            header_color = st.color_picker(
                                "Header Background Color",
                                value=branding.get('header_color', '#000000'),
                                key=f"nl_header_color_{config['id']}"
                            )
                            header_font = st.selectbox(
                                "Header Font",
                                options=['Arial, sans-serif', 'Georgia, serif', 'Courier New, monospace', 'Verdana, sans-serif', 'Times New Roman, serif'],
                                index=0 if branding.get('header_font', 'Arial, sans-serif') == 'Arial, sans-serif' else 1,
                                key=f"nl_header_font_{config['id']}"
                            )
                        with col_brand2:
                            header_text_color = st.color_picker(
                                "Header Text Color",
                                value=branding.get('header_text_color', '#cda600'),
                                key=f"nl_header_text_color_{config['id']}"
                            )
                            logo_enabled = st.checkbox(
                                "Show Logo",
                                value=branding.get('logo_enabled', True),
                                key=f"nl_logo_enabled_{config['id']}"
                            )
                        
                        # Logo upload
                        logo_file = st.file_uploader(
                            "Upload Custom Logo (PNG/JPG)",
                            type=['png', 'jpg', 'jpeg'],
                            key=f"nl_logo_{config['id']}",
                            help="Upload a custom logo for your newsletter header"
                        )
                        
                        logo_path = branding.get('logo_path', 'attached_assets/Innopower Logo white background_1760182832027.png')
                        
                        # Save uploaded logo if provided
                        if logo_file:
                            import os
                            os.makedirs('attached_assets', exist_ok=True)
                            logo_path = f"attached_assets/{logo_file.name}"
                            with open(logo_path, 'wb') as f:
                                f.write(logo_file.getbuffer())
                            st.success(f"✅ Logo uploaded: {logo_file.name}")
                        
                        # CTA Buttons customization
                        st.markdown("**🔘 Call-to-Action Buttons:**")
                        cta_buttons = config.get('cta_buttons', [
                            {'text': 'Visit Our Website', 'link': 'https://example.com'},
                            {'text': 'Subscribe for More', 'link': 'https://example.com/subscribe'},
                            {'text': 'Contact Us', 'link': 'https://example.com/contact'}
                        ])
                        
                        # Ensure we have exactly 3 buttons
                        while len(cta_buttons) < 3:
                            cta_buttons.append({'text': '', 'link': ''})
                        
                        cta1_text = st.text_input("Button 1 Text", value=cta_buttons[0].get('text', ''), key=f"nl_cta1_text_{config['id']}")
                        cta1_link = st.text_input("Button 1 Link", value=cta_buttons[0].get('link', ''), key=f"nl_cta1_link_{config['id']}")
                        
                        cta2_text = st.text_input("Button 2 Text", value=cta_buttons[1].get('text', ''), key=f"nl_cta2_text_{config['id']}")
                        cta2_link = st.text_input("Button 2 Link", value=cta_buttons[1].get('link', ''), key=f"nl_cta2_link_{config['id']}")
                        
                        cta3_text = st.text_input("Button 3 Text", value=cta_buttons[2].get('text', ''), key=f"nl_cta3_text_{config['id']}")
                        cta3_link = st.text_input("Button 3 Link", value=cta_buttons[2].get('link', ''), key=f"nl_cta3_link_{config['id']}")
                        
                        if st.form_submit_button("💾 Update"):
                            # Create updated branding object
                            updated_branding = {
                                'logo_enabled': logo_enabled,
                                'logo_path': logo_path,
                                'header_color': header_color,
                                'header_text_color': header_text_color,
                                'header_font': header_font
                            }
                            
                            # Create updated CTA buttons array
                            updated_cta_buttons = [
                                {'text': cta1_text, 'link': cta1_link},
                                {'text': cta2_text, 'link': cta2_link},
                                {'text': cta3_text, 'link': cta3_link}
                            ]
                            
                            if config_manager.update_config(
                                config['id'],
                                name=new_name,
                                description=new_desc,
                                max_stories=new_max,
                                schedule_time=new_time,
                                feed_ids=selected_feeds,
                                category_ids=selected_cats,
                                branding=updated_branding,
                                cta_buttons=updated_cta_buttons
                            ):
                                st.success(f"✅ Updated {new_name}")
                                st.rerun()
                            else:
                                st.error("Failed to update newsletter")
    
    with tab2:
        st.subheader("Create New Newsletter")
        
        with st.form("add_newsletter_form"):
            new_name = st.text_input("Newsletter Name", placeholder="e.g., AI Research Weekly")
            new_desc = st.text_input("Description", placeholder="e.g., Weekly digest of AI research papers")
            
            col1, col2 = st.columns(2)
            with col1:
                new_max = st.number_input("Max Stories", value=12, min_value=1, max_value=50)
            with col2:
                new_time = st.text_input("Schedule Time (HH:MM)", value="07:00")
            
            # Feed selection
            all_feeds = feed_manager.get_all_feeds()
            feed_options = {f['id']: f['name'] for f in all_feeds}
            selected_feeds = st.multiselect(
                "RSS Feeds (leave empty to use all enabled feeds)",
                options=list(feed_options.keys()),
                format_func=lambda x: feed_options[x]
            )
            
            # Category selection
            all_cats = category_manager.get_all_categories()
            cat_options = {c['id']: c['name'] for c in all_cats}
            selected_cats = st.multiselect(
                "Categories (leave empty to use all enabled categories)",
                options=list(cat_options.keys()),
                format_func=lambda x: cat_options[x]
            )
            
            st.info("💡 Empty feeds/categories means 'use all enabled'. This gives you flexibility to manage sources centrally.")
            
            submitted = st.form_submit_button("➕ Create Newsletter")
            
            if submitted:
                if not new_name:
                    st.error("Please provide a newsletter name")
                else:
                    if config_manager.add_config(new_name, new_desc, selected_feeds, selected_cats, new_max):
                        st.success(f"✅ Created {new_name} successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Failed to create newsletter. A newsletter with this name may already exist.")

def show_configuration():
    st.header("⚙️ Configuration")
    
    st.subheader("API Keys")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    # Check Resend status via the connector
    resend_client = ResendClient()
    resend_status = resend_client.get_status()
    
    st.text_input("OpenAI API Key", value="***" if openai_key else "", 
                 help="Set via OPENAI_API_KEY environment variable", disabled=True)
    
    st.markdown("**Resend Email Service**")
    if resend_status['ready']:
        st.success(f"✅ Connected - From: {resend_status['from_email']}")
    else:
        st.warning("⚠️ Not configured - Set up via Replit integrations")
    
    st.info("💡 **To send newsletters**: Uncomment the email sending code in app.py and scheduler.py, then add your recipient email addresses.")
    
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
