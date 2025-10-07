# AI Daily Newsletter Generator

An automated daily newsletter system that collects the latest AI and technology news from 10 trusted sources, intelligently consolidates duplicate stories, generates AI-powered summaries, and distributes via web and email.

## Overview

This application automatically:
- Scrapes 10 leading AI/tech news sources daily
- Identifies and consolidates duplicate stories across sources
- Generates intelligent summaries using OpenAI
- Creates beautifully formatted HTML newsletters
- Publishes newsletters on a web interface
- Sends newsletters via SendFox email at 7 AM daily

## News Sources

The system monitors these 10 AI/technology news sources:

1. **TechCrunch AI** - AI startups, industry developments, investment news
2. **MIT News AI/ML** - Research-driven academic coverage
3. **AI News** - Dedicated AI news, insights, and trends
4. **MIT Technology Review** - In-depth tech analysis and commentary
5. **VentureBeat AI** - Business reporting, AI product launches, enterprise AI
6. **Wired AI** - Narrative and cultural takes on AI
7. **Forbes AI** - Business, leadership, and market perspectives
8. **OpenAI Blog** - First-party updates and research announcements
9. **ScienceDaily AI** - Scientific research breakthroughs
10. **The Verge AI** - Tech media coverage and critical analysis

## Features

### Core Functionality
- **Automated Scraping**: Collects latest articles from all 10 sources
- **Smart Deduplication**: Uses TF-IDF and cosine similarity to identify duplicate stories
- **Story Consolidation**: Merges similar stories from multiple sources into single entries
- **AI Summarization**: Generates concise summaries with key points using OpenAI GPT
- **Impact Scoring**: Rates each story's significance (1-10 scale)
- **Category Classification**: Automatically categorizes stories
- **Scheduled Generation**: Automatically generates and sends at 7 AM daily
- **Newsletter Archive**: Stores and displays historical newsletters
- **Manual Triggers**: Generate newsletters on-demand

### Web Interface
- **Dashboard**: Real-time status, metrics, and activity
- **Newsletter Generation**: Manual trigger with live progress tracking
- **Archive Browser**: View all past newsletters
- **Configuration Panel**: View API status and settings

## System Architecture

### Components

1. **app.py** - Main Streamlit web application
   - Dashboard and user interface
   - Newsletter generation workflow
   - Archive viewing

2. **scraper.py** - Web scraping module
   - Fetches articles from 10 news sources
   - Extracts full content using trafilatura
   - Filters recent articles (last 24 hours)

3. **deduplicator.py** - Story consolidation module
   - TF-IDF vectorization
   - Cosine similarity analysis (70% threshold)
   - Groups and consolidates duplicate stories

4. **summarizer.py** - AI summarization module
   - OpenAI GPT integration
   - Generates summaries, key points, impact scores
   - Category classification
   - Fallback handling for API failures

5. **newsletter.py** - Newsletter generation module
   - HTML template rendering
   - Responsive email design
   - Statistics generation
   - Plain text version support

6. **sendfox_client.py** - Email distribution module
   - SendFox API integration
   - Campaign creation and sending
   - Subscriber management
   - Connection testing

7. **scheduler.py** - Automated scheduling module
   - Daily 7 AM execution
   - Background thread management
   - Error handling and logging

8. **database.py** - Data persistence module
   - JSON-based storage
   - Newsletter archiving
   - Statistics and queries
   - Backup management

## Setup Instructions

### Prerequisites
- Python 3.11+
- OpenAI API key (required)
- SendFox API token (optional, for email distribution)

### Installation

1. **Clone or access the repository**

2. **Install dependencies** (already configured):
   - streamlit
   - openai
   - beautifulsoup4
   - trafilatura
   - requests
   - schedule
   - scikit-learn
   - numpy
   - pandas

3. **Configure API Keys**
   
   You need to set up two environment secrets:
   
   - `OPENAI_API_KEY`: Required for article summarization
     - Get from: https://platform.openai.com/api-keys
   
   - `SENDFOX_API_TOKEN`: Optional for email distribution
     - Get from: https://sendfox.com (API settings)

4. **Run the application**
   ```bash
   streamlit run app.py --server.port 5000
   ```

## Usage Guide

### Web Interface

#### Dashboard
- View API connection status
- See total newsletter count
- Track today's newsletters
- View recent activity
- Check next scheduled run time

#### Generate Newsletter
1. Navigate to "Generate Newsletter" page
2. Click "Generate Newsletter Now"
3. Watch real-time progress:
   - Scraping articles
   - Deduplicating stories
   - Generating summaries
   - Creating newsletter
   - Sending email (if configured)
4. Preview generated newsletter

#### Newsletter Archive
- Browse all past newsletters
- View creation dates and story counts
- Check email send status
- Open and read full newsletters

#### Configuration
- View API key status
- See all monitored news sources
- Check schedule settings

### Automated Daily Generation

The system automatically:
1. Runs at 7:00 AM every day
2. Scrapes all 10 news sources
3. Consolidates duplicate stories
4. Generates AI summaries
5. Creates HTML newsletter
6. Saves to database
7. Sends via SendFox (if configured)

### Manual Generation

Generate a newsletter anytime:
1. Open the web interface
2. Go to "Generate Newsletter"
3. Click "Generate Newsletter Now"
4. Wait for completion (2-5 minutes)

## Configuration

### Schedule Settings
Default: 7:00 AM daily

To change the schedule:
1. Open `scheduler.py`
2. Modify line 32:
   ```python
   schedule.every().day.at("07:00").do(self._generate_daily_newsletter)
   ```
3. Change "07:00" to your preferred time (24-hour format)

### Deduplication Threshold
Default: 0.7 (70% similarity)

To adjust sensitivity:
1. Open `deduplicator.py`
2. Modify line 13:
   ```python
   def __init__(self, similarity_threshold: float = 0.7):
   ```
3. Lower values = more strict (fewer duplicates detected)
4. Higher values = more lenient (more duplicates detected)

### OpenAI Model
Current: GPT-5

The model is configured in `summarizer.py` (line 20)

## Data Storage

### Database File
- **Location**: `newsletters.json`
- **Format**: JSON
- **Backup**: Automatic backup created on each save (`newsletters.json.backup`)

### Newsletter Data Structure
```json
{
  "id": "20251007_070000_123",
  "title": "AI Newsletter - October 07, 2025",
  "html_content": "<html>...</html>",
  "story_count": 15,
  "created_at": "2025-10-07T07:00:00",
  "generation_method": "scheduled",
  "email_sent": true,
  "email_sent_at": "2025-10-07T07:05:00"
}
```

## Deduplication Process

The system uses advanced techniques to identify duplicate stories:

1. **Text Preprocessing**: Cleans and normalizes article text
2. **TF-IDF Vectorization**: Converts text to numerical representations
3. **Cosine Similarity**: Measures similarity between articles
4. **Grouping**: Clusters similar articles (≥70% similarity)
5. **Consolidation**: Merges duplicates into single stories
   - Keeps article with most content
   - Tracks all source URLs
   - Notes consolidation reason

### Example
If the same AI breakthrough is covered by TechCrunch, MIT News, and The Verge, the system:
- Detects high similarity (>70%)
- Groups all three articles
- Creates one consolidated story
- Shows "CONSOLIDATED" badge
- Lists all 3 sources
- Provides links to all versions

## Troubleshooting

### No API Key Warnings
**Problem**: "OPENAI_API_KEY not found" or "SENDFOX_API_TOKEN not found"

**Solution**: Add the API keys in the Replit Secrets section

### Newsletter Generation Fails
**Problem**: Error during generation

**Solutions**:
- Check API key validity
- Verify internet connection
- Review logs for specific errors
- Check if news sources are accessible

### No Articles Scraped
**Problem**: 0 articles found

**Solutions**:
- News sources may have changed their HTML structure
- Network connectivity issues
- Sources may be blocking automated access
- Try again later when sources publish new content

### Email Not Sending
**Problem**: Newsletter generated but email not sent

**Solutions**:
- Verify SENDFOX_API_TOKEN is set correctly
- Check SendFox account status
- Ensure subscriber list exists
- Review SendFox API limits

### Scheduler Not Running
**Problem**: No automatic generation at 7 AM

**Solutions**:
- Ensure application is running continuously
- Check scheduler logs
- Verify workflow is active
- Restart the application

## API Rate Limits

### OpenAI
- Monitor your OpenAI usage
- Each newsletter generates 1 summary per unique story
- Typical newsletter: 10-20 API calls

### SendFox
- Check your SendFox plan limits
- One campaign created per newsletter
- Sent to all subscribers in your list

### News Sources
- System includes 1-second delays between source scraping
- Respects robots.txt
- Uses standard browser user-agent

## Maintenance

### Database Cleanup
Remove old newsletters:
```python
from database import NewsletterDatabase
db = NewsletterDatabase()
removed = db.cleanup_old_newsletters(days_to_keep=30)
```

### Export Newsletters
```python
db.export_newsletters('newsletters_backup.json')
```

### View Statistics
```python
stats = db.get_database_stats()
print(stats)
```

## Technical Stack

- **Frontend**: Streamlit
- **AI/ML**: OpenAI GPT-5, scikit-learn
- **Web Scraping**: BeautifulSoup4, trafilatura, requests
- **Scheduling**: schedule library
- **Email**: SendFox API
- **Storage**: JSON file database
- **Language**: Python 3.11

## Performance

### Typical Newsletter Generation
- **Scraping**: 30-60 seconds (10 sources)
- **Deduplication**: 5-10 seconds
- **Summarization**: 20-40 seconds (depends on story count)
- **Newsletter Creation**: 1-2 seconds
- **Total**: 2-4 minutes

### Resource Usage
- **Memory**: ~200-300 MB
- **Disk**: Minimal (newsletters stored as JSON)
- **Network**: Active during scraping and API calls

## Security

- API keys stored as environment secrets (never in code)
- No hardcoded credentials
- Secure HTTPS connections to all APIs
- Regular backup of newsletter database

## Future Enhancements

Potential features for next phase:
- Subscriber management dashboard
- Newsletter customization (topic filtering, length preferences)
- Analytics dashboard (open rates, engagement metrics)
- RSS feed generation
- A/B testing for newsletter formats
- Multiple newsletter templates
- Social media sharing integration

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review application logs
3. Verify API key configuration
4. Test with manual generation first

## License

This project is configured for personal/internal use with the Replit platform.

---

**Generated**: October 07, 2025  
**Version**: 1.0.0  
**Platform**: Replit + Streamlit
