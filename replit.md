# AI Daily Newsletter Generator

## Overview

An automated daily newsletter system that collects AI and technology news from 10 trusted sources, intelligently consolidates duplicate stories using TF-IDF similarity matching, generates AI-powered summaries via OpenAI, and distributes beautifully formatted newsletters through Resend email at 7 AM daily. The system includes a Streamlit web interface for manual triggers, newsletter archives, and real-time status monitoring.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Structure

**Framework**: Python-based system with Streamlit web interface
- Modular component architecture with single-responsibility classes
- Background scheduler using threading for daily automation
- JSON-based persistence for newsletter storage
- Session state management for web interface

### Core Components

**News Scraper** (`scraper.py`)
- RSS feed parsing from 10 AI/tech news sources (TechCrunch, MIT News, VentureBeat, Wired, The Verge, etc.)
- Content extraction using Trafilatura library
- Retry logic with exponential backoff for reliability
- Rate limiting and user-agent rotation to avoid blocking

**Story Deduplication** (`deduplicator.py`)
- TF-IDF vectorization with scikit-learn (1000 features, 1-2 n-grams)
- Cosine similarity matrix calculation
- Configurable similarity threshold (default 0.6)
- Groups duplicate stories across sources and consolidates metadata

**AI Summarization** (`summarizer.py`)
- OpenAI GPT-4 Turbo integration for content summarization
- Generates concise summaries with key points extraction
- Automatic impact scoring (1-10 scale) - measures significance to AI practitioners, businesses, and researchers
- Category classification for story organization (AI Policy, AI Business, AI Research, AI Products, Machine Learning, Robotics, Tech Industry, Other)
- Fallback handling when API unavailable

**Newsletter Generation** (`newsletter.py`)
- HTML template generation with responsive design
- Markdown format generation following standardized template structure
- Stories grouped by category with section headers and emoji icons
- Category-based organization: preferred categories first, then alphabetical, then "Other"
- Robust category handling - normalizes non-string/falsy categories to "Other"
- Plain text version creation for email compatibility
- Story sorting by impact score within each category
- Supports both web display and email distribution
- Dynamic branding application:
  - Custom logo embedding via base64 encoding
  - Header styling with configurable colors (background and text)
  - Font family customization for headers
  - CSS injection for personalized newsletter appearance
  - Falls back to default Innopower branding if not specified
- Markdown template format:
  - Clean header with newsletter title and subtitle
  - Story count display
  - Category sections with emoji headers
  - Each story shows: title, impact score, summary, key points, and article link
  - CTA buttons interspersed between story categories
  - Consistent footer with branding and generation date

**Email Distribution** (`resend_client.py`)
- Resend API integration via Replit connector
- Secure credential management through Replit integrations
- Simple email sending with HTML content support
- Test email functionality for verification
- Comprehensive error handling and logging
- Note: List management handled separately from email sending

**User Authentication** (`auth.py`)
- Secure user login and registration system
- Password hashing: PBKDF2-HMAC-SHA256 with 100,000 iterations
- Cryptographic salt: Random 32-byte salt per user (secrets.token_bytes)
- User data storage: JSON file (users.json) with hashed passwords and salts
- Session management: Streamlit session state for authentication
- Features: User signup, login, logout, profile management, password change
- Security: All passwords hashed with per-user salts, no plain text storage
- User profiles: Username, email, full name, creation date, last login
- Access control: All application pages protected behind authentication

**Scheduling System** (`scheduler.py`)
- Schedule library for daily 7 AM newsletter generation
- Threaded execution to avoid blocking web interface
- Automatic workflow orchestration (scrape → deduplicate → summarize → generate → send)
- Thread-safe coordination with manual workflows via shared lock
- Currently uses default newsletter configuration (future: support multiple configs)

**Data Persistence** (`database.py`)
- JSON file-based storage (`newsletters.json`)
- Newsletter archiving with metadata
- Automatic backup creation before saves
- Retrieval methods for archive browsing

**Web Interface** (`app.py`)
- Streamlit dashboard with real-time metrics
- Manual newsletter generation with progress tracking
- Dual export functionality: HTML and Markdown formats for both new and archived newsletters
- Archive browser for historical newsletters with view and download options
- RSS Feed Management page for adding, editing, deleting, and toggling news sources
- Category Management page for creating and maintaining custom story categories
- Configuration panel for API status
- Backward compatibility for archived newsletters (markdown available for new newsletters only)

**Feed Management** (`feed_manager.py`, `feeds.json`)
- JSON-based storage for RSS feed configuration
- CRUD operations: add, update, delete, toggle enable/disable
- Feed categorization (Tech News, Research, AI Industry, Business, Other)
- Dynamic feed loading - scraper automatically reloads when feeds change
- Backup system for feed configuration safety

**Category Management** (`category_manager.py`, `categories.json`)
- JSON-based storage for newsletter categories with priority, emoji, and enabled status
- CRUD operations: add, edit, delete, toggle enable/disable, reorder by priority
- Default categories: AI Policy, AI Business, AI Research, AI Products, Machine Learning, Robotics, Tech Industry, Other
- Priority-based ordering (1-998 for custom categories, 999 reserved for "Other")
- Dynamic category loading - summarizer automatically reloads when categories change
- Inline editing with emoji support and priority management
- "Other" category protected from deletion and always appears last
- Backup system for category configuration safety

**Newsletter Configuration Management** (`newsletter_config.py`, `newsletter_configs.json`)
- Multiple newsletter configurations with independent settings
- Each config specifies: name, description, selected feeds, selected categories, max stories
- Empty feed/category lists default to "use all enabled" for central management flexibility
- CRUD operations: add, update, delete, toggle enable/disable
- Schedule settings per newsletter (time, enabled/disabled)
- Generate page allows selecting which newsletter config to use
- Database tracks config_id and config_name for each generated newsletter
- Archive view displays which config was used for each newsletter
- Backup system for configuration safety
- Thread-safe generation via shared lock with scheduler
- Full branding customization per newsletter:
  - Custom logo upload (PNG/JPG) stored in attached_assets directory
  - Header background color customization via color picker
  - Header text color customization via color picker
  - Header font selection (Arial, Georgia, Courier, Verdana, Times New Roman)
  - Logo toggle (show/hide)
  - All branding settings applied dynamically during newsletter generation
- Call-to-Action (CTA) buttons customization:
  - 3 customizable CTA buttons per newsletter
  - Each button has text and link properties
  - Buttons styled with header text color from branding
  - Empty buttons automatically hidden from display
  - Buttons appear centered between stories and footer

**Shared Resources** (`shared_resources.py`)
- Persistent threading lock for newsletter generation coordination
- Survives Streamlit reruns (unlike module-level locks in app.py)
- Serializes manual and scheduled newsletter runs to prevent concurrent execution
- Protects database writes and Resend API sends from race conditions
- Both app.py and scheduler.py import and use the same lock instance

### Data Flow

1. **Scheduled/Manual Trigger** → Initiates workflow
2. **Scraping** → Collects articles from 10 RSS feeds (limited to 15 most recent for performance)
3. **Deduplication** → Identifies and consolidates similar stories using TF-IDF/cosine similarity
4. **Summarization** → Generates AI summaries, scores, and categories via OpenAI (top 15 stories)
5. **Newsletter Generation** → Creates HTML, Markdown, and text versions (top 12 by impact score)
6. **Persistence** → Saves to JSON database with all formats
7. **Distribution** → Sends via Resend email API
8. **Display** → Available in web interface archive with dual export options

### Key Design Patterns

**Singleton Components**: Components cached via `@st.cache_resource` for efficient resource usage

**Background Threading**: Scheduler runs in daemon thread to enable concurrent web interface operation

**Thread Safety**: Shared lock module prevents concurrent newsletter generation
- Lock in shared_resources.py persists across Streamlit reruns
- Both manual and scheduled workflows coordinate via the same lock instance
- Non-blocking acquisition (blocking=False) with user-friendly warnings
- Proper cleanup with finally blocks ensures lock release

**Parameter Passing**: No shared state mutation for thread safety
- Scraper accepts custom_sources parameter (avoids mutating self.sources)
- Summarizer accepts custom_categories parameter (avoids mutating self.categories)
- Each newsletter config generates with isolated feed/category lists

**Graceful Degradation**: System continues with reduced functionality when APIs unavailable (logs warnings, uses fallbacks)

**Modular Pipeline**: Each processing stage is independent and replaceable

## External Dependencies

### Third-Party Services

**OpenAI API**
- Purpose: AI-powered article summarization and analysis
- Model: GPT-4 Turbo Preview
- Configuration: Requires `OPENAI_API_KEY` environment variable
- Usage: Generates summaries, key points, impact scores, and categories

**Resend Email API**
- Purpose: Email newsletter distribution
- Configuration: Managed via Replit connector integration
- Authentication: Automatic API key and from_email management
- Functionality: Transactional email sending with HTML support
- Note: Requires recipient email list configuration in code

### Python Libraries

**Web & Interface**
- `streamlit`: Web dashboard and user interface
- `pandas`: Data display and manipulation in UI

**Content Processing**
- `trafilatura`: Article content extraction from web pages
- `beautifulsoup4`: HTML parsing
- `feedparser`: RSS feed parsing

**Machine Learning**
- `scikit-learn`: TF-IDF vectorization and cosine similarity
- `numpy`: Numerical operations for similarity calculations

**Scheduling & Utilities**
- `schedule`: Daily automation at 7 AM
- `requests`: HTTP requests with retry logic
- `urllib3`: Advanced HTTP features and retry strategies

### Data Storage

**JSON Database** (`newsletters.json`)
- Stores newsletter archive with full HTML/text content
- Includes metadata: ID, title, generation timestamp, story count
- Automatic backup mechanism before writes
- No external database server required

### Content Sources (RSS Feeds)

Monitors 10 sources:
1. TechCrunch AI - AI startups and industry news
2. MIT News AI/ML - Academic research coverage
3. AI News - Dedicated AI news and trends
4. MIT Technology Review - In-depth tech analysis
5. VentureBeat AI - Business and enterprise AI
6. Wired AI - Cultural AI perspectives
7. Forbes AI - Business and market insights
8. OpenAI Blog - First-party research updates
9. ScienceDaily AI - Scientific breakthroughs
10. The Verge AI - Tech media coverage