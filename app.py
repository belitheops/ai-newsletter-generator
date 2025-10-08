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
        "Configuration"
    ])
    
    if page == "Dashboard":
        show_dashboard(db)
    elif page == "Generate Newsletter":
        show_generate_newsletter(scraper, deduplicator, summarizer, newsletter_gen, sendfox, db)
    elif page == "Newsletter Archive":
        show_newsletter_archive(db)
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
        
        # Step 3: Summarize articles
        status_text.text("📝 Summarizing articles with OpenAI...")
        progress_bar.progress(0.50)
        summaries = []
        for i, story in enumerate(unique_stories):
            summary = summarizer.summarize_story(story)
            summaries.append(summary)
            progress_bar.progress(0.50 + (i + 1) / len(unique_stories) * 0.25)
        
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
        status_text.text("📄 Generating newsletter HTML...")
        progress_bar.progress(0.85)
        newsletter_html = newsletter_gen.generate_newsletter(top_summaries)
        
        # Step 5: Save to database
        newsletter_data = {
            'title': f"AI Newsletter - {datetime.now().strftime('%B %d, %Y')}",
            'html_content': newsletter_html,
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
        
        # Add export button
        col1, col2 = st.columns([1, 4])
        with col1:
            st.download_button(
                label="📥 Export HTML",
                data=newsletter_html,
                file_name=f"newsletter_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                help="Download the newsletter as a standalone HTML file"
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
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button(f"👁️ View", key=f"view_{newsletter['id']}"):
                    st.components.v1.html(newsletter['html_content'], height=600, scrolling=True)
            with col_b:
                st.download_button(
                    label="📥 Export HTML",
                    data=newsletter['html_content'],
                    file_name=f"newsletter_{newsletter['created_at'][:10]}.html",
                    mime="text/html",
                    key=f"download_{newsletter['id']}",
                    help="Download this newsletter as HTML"
                )

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
