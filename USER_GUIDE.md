# AI Newsletter Generator - User Guide

Welcome! This guide will help you get the most out of your AI Newsletter Generator. No technical knowledge required - just follow along!

---

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Generating Your First Newsletter](#generating-your-first-newsletter)
4. [Newsletter Management](#newsletter-management)
5. [Managing RSS Feeds](#managing-rss-feeds)
6. [Managing Categories](#managing-categories)
7. [Viewing Newsletter Archive](#viewing-newsletter-archive)
8. [Configuration & Settings](#configuration--settings)
9. [Common Tasks](#common-tasks)
10. [Tips & Best Practices](#tips--best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Getting Started

### What This App Does

This app automatically:
- **Collects** AI and tech news from multiple sources
- **Removes duplicates** (same story from different websites)
- **Creates summaries** using AI to make articles easier to read
- **Rates importance** of each story (1-10 scale)
- **Organizes** stories into categories
- **Generates** beautiful HTML newsletters
- **Sends** newsletters via email (when configured)

### First Time Setup

When you first open the app, you'll see the main interface with a sidebar on the left. That's your navigation menu!

**Navigation Menu:**
- **Dashboard** - See your stats and activity
- **Generate Newsletter** - Create a new newsletter
- **Newsletter Archive** - View past newsletters
- **Newsletter Management** - Create and customize newsletter profiles
- **RSS Feed Management** - Add/remove news sources
- **Category Management** - Organize story categories
- **Configuration** - Check API connections

### Setting Up API Keys (Required for AI Features)

Before you can generate newsletters with AI summaries, you need to set up your API keys:

#### OpenAI API Key (Required)

This key enables the AI to create summaries, rate stories, and organize them into categories.

**How to get your OpenAI API Key:**

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an OpenAI account
3. Click **"Create new secret key"**
4. Give it a name (e.g., "Newsletter Generator")
5. Copy the key (starts with `sk-`)

**How to add it to your app:**

1. In Replit, look for the **"Secrets"** tool in the left sidebar (🔒 lock icon)
2. Click **"+ New Secret"**
3. For the **key**, type: `OPENAI_API_KEY`
4. For the **value**, paste your OpenAI key
5. Click **"Add Secret"**
6. Refresh your app to load the key

**Checking if it worked:**
- Go to the **Dashboard** page
- Look at "API Status" in the top row
- You should see ✅ **Connected**

#### Resend Email Service (Optional - for sending emails)

Resend is already set up through Replit's integration! You should see ✅ **Connected** under "Resend Status" on the Dashboard.

**If you see ❌ Not Configured:**
1. Your Resend integration may need to be reconnected
2. Don't worry - you can still generate newsletters
3. You just won't be able to email them automatically
4. You can always download the HTML and send manually

**To enable actual email sending:**
- Email sending is currently disabled by default for safety
- Contact your developer to enable it and configure recipient addresses

---

## Dashboard Overview

The Dashboard is your home base. Here's what you'll see:

### Status Indicators (Top Row)

1. **API Status** 
   - ✅ Connected = OpenAI is working (needed for AI summaries)
   - ❌ No API Key = You need to add your OpenAI key

2. **Resend Status**
   - ✅ Connected = Email service is ready
   - ❌ Not Configured = Email not set up yet (newsletters will still generate)

3. **Total Newsletters**
   - Shows how many newsletters you've created overall

4. **Today's Newsletters**
   - Shows newsletters created today

### Recent Activity

Below the status indicators, you'll see a list of your most recent newsletters with:
- Title
- Creation date and time
- Number of stories included
- Whether email was sent

### Scheduling Information

At the bottom, you'll see when the next automatic newsletter will be created (default: 7:00 AM daily).

---

## Generating Your First Newsletter

Let's create your first newsletter!

### Step 1: Navigate to Generate Newsletter

Click **"Generate Newsletter"** in the left sidebar.

### Step 2: Select a Newsletter Configuration

At the top, you'll see a dropdown menu with newsletter options. Each newsletter configuration can have:
- Custom name
- Different RSS feed sources
- Different categories
- Custom branding (logo, colors)
- Maximum number of stories

**Default:** If this is your first time, you'll see one default newsletter configuration.

### Step 3: Click "Generate Newsletter Now"

Click the big blue **"🚀 Generate Newsletter Now"** button.

### Step 4: Watch the Progress

You'll see a progress bar showing what's happening:

1. **🔍 Scraping articles** (30-60 seconds)
   - Collecting news from all selected sources

2. **🔄 Deduplicating stories** (5-10 seconds)
   - Finding and removing duplicate stories

3. **🤖 Generating AI summaries** (20-40 seconds)
   - Creating summaries and scoring importance

4. **📄 Generating newsletter** (1-2 seconds)
   - Creating the final HTML and Markdown versions

5. **📧 Sending email** (if configured)
   - Sending via Resend email service

**Total time:** About 2-4 minutes

### Step 5: View Your Newsletter

Once complete:
- Your newsletter appears on screen
- Two download buttons appear: **Export HTML** and **Export Markdown**
- Newsletter is automatically saved to the archive

**Export Options:**
- **HTML** - Beautiful formatted version for email or web
- **Markdown** - Plain text format for editing or other uses

---

## Newsletter Management

This is where you create and customize different newsletter profiles. Think of each profile as a different "style" of newsletter.

### Creating a New Newsletter Profile

**Step 1:** Go to **"Newsletter Management"** in the sidebar

**Step 2:** Scroll to the **"Create New Newsletter"** section

**Step 3:** Fill in the details:

**Basic Information:**
- **Name** - Give your newsletter a name (e.g., "AI Weekly Digest")
- **Description** - Optional description of what this newsletter covers
- **Max Stories** - How many stories to include (default: 12)

**RSS Feed Selection:**
- Choose which news sources to use for this newsletter
- Leave empty to use all enabled feeds
- Tip: Create specialized newsletters by selecting specific sources

**Category Selection:**
- Choose which story categories to include
- Leave empty to use all enabled categories
- Tip: Create focused newsletters (e.g., only AI Research)

**Step 4:** Click **"➕ Create Newsletter"**

Your new newsletter profile is ready!

### Customizing Newsletter Branding

Each newsletter can have unique branding:

**Step 1:** Find your newsletter in the list

**Step 2:** Click **"Customize Branding"**

**Step 3:** Customize the following:

**Logo:**
- Upload your logo image (PNG or JPG)
- Toggle "Show Logo" on/off
- Logo appears at the top of your newsletter

**Header Colors:**
- **Background Color** - Pick the header background color
- **Text Color** - Pick the text color for readability
- **Font** - Choose from: Arial, Georgia, Courier, Verdana, Times New Roman

**Call-to-Action (CTA) Buttons:**
- Add up to 3 clickable buttons in your newsletter
- For each button, set:
  - **Text** - What the button says (e.g., "Visit Our Website")
  - **Link** - Where it goes (e.g., https://yourwebsite.com)
- Empty buttons won't appear

**Step 4:** Click **"💾 Save Branding"**

Your custom branding is applied!

### Editing a Newsletter

1. Find the newsletter in the list
2. Click **"✏️ Edit"**
3. Make your changes
4. Click **"💾 Save Changes"**

### Deleting a Newsletter

1. Find the newsletter in the list
2. Click **"🗑️ Delete"**
3. Confirm the deletion

**Warning:** You can't delete if there's only one newsletter configuration!

### Enabling/Disabling Newsletters

Toggle the **"Enabled"** switch to turn newsletters on/off without deleting them.

---

## Managing RSS Feeds

RSS feeds are the news sources where the app collects articles.

### Viewing Your Feeds

Go to **"RSS Feed Management"** to see all your news sources.

Each feed shows:
- **Name** - Source name (e.g., "TechCrunch AI")
- **Category** - Type of source (Tech News, Research, etc.)
- **URL** - The RSS feed address
- **Status** - Enabled or Disabled

### Adding a New RSS Feed

**Step 1:** Scroll to **"Add New RSS Feed"**

**Step 2:** Fill in the information:
- **Name** - Friendly name for the source
- **Description** - What kind of news it covers
- **RSS Feed URL** - The RSS feed address (usually ends in .xml or /feed)
- **Category** - Choose: Tech News, Research, AI Industry, Business, or Other

**Step 3:** Click **"➕ Add Feed"**

**Finding RSS Feed URLs:**
- Most news sites have RSS feeds - look for an RSS icon
- Try adding `/feed` or `/rss` to the end of a website URL
- Search Google: "[website name] RSS feed"

### Editing a Feed

1. Find the feed in the list
2. Click **"✏️ Edit"**
3. Make your changes
4. Click **"💾 Save"**

### Deleting a Feed

1. Find the feed
2. Click **"🗑️ Delete"**
3. Confirm deletion

### Enabling/Disabling Feeds

Use the **"Enabled"** toggle to temporarily turn feeds on/off without deleting them.

**Tip:** Disable feeds during testing or if a source becomes unreliable.

---

## Managing Categories

Categories help organize newsletter stories into sections (like AI Policy, AI Business, etc.).

### Viewing Categories

Go to **"Category Management"** to see all your categories.

Each category has:
- **Name** - Category name
- **Emoji** - Icon for visual appeal
- **Priority** - Display order (lower numbers first)
- **Status** - Enabled or Disabled

### Adding a New Category

**Step 1:** Scroll to **"Create New Category"**

**Step 2:** Fill in:
- **Name** - Category name (e.g., "AI Ethics")
- **Emoji** - Single emoji to represent it (e.g., ⚖️)
- **Priority** - Display order (1-998, lower appears first)

**Step 3:** Click **"➕ Create Category"**

**Default Categories:**
- AI Policy
- AI Business
- AI Research
- AI Products
- Machine Learning
- Robotics
- Tech Industry
- Other (always appears last)

### Editing a Category

1. Find the category
2. Click the **edit icon** next to it
3. Change name, emoji, or priority
4. Click **"Save"**

### Reordering Categories

Change the **Priority** number:
- **1** = Appears first
- **10** = Appears after priority 1-9
- **999** = Reserved for "Other" (always last)

### Deleting a Category

1. Find the category
2. Click **"🗑️ Delete"**
3. Confirm deletion

**Note:** You cannot delete the "Other" category - it's protected.

### Enabling/Disabling Categories

Toggle the **"Enabled"** switch to show/hide categories.

**Tip:** Disabled categories won't appear in new newsletters, but existing newsletters keep them.

---

## Viewing Newsletter Archive

The Archive stores all your generated newsletters.

### Accessing the Archive

Click **"Newsletter Archive"** in the sidebar.

### What You'll See

A table showing:
- **Title** - Newsletter name and date
- **Created** - When it was generated
- **Stories** - Number of articles included
- **Email Sent** - Whether it was emailed
- **Config** - Which newsletter configuration was used

### Viewing a Newsletter

Click the **"👁️ View"** button to see the full newsletter in your browser.

### Downloading Newsletters

For each newsletter, you can:
- **📥 Download HTML** - Get the email-ready version
- **📝 Download Markdown** - Get the plain text version (if available)

**Note:** Older newsletters may not have Markdown versions.

### Sorting and Searching

- Click column headers to sort
- Most recent newsletters appear first
- Use browser search (Ctrl+F / Cmd+F) to find specific dates

---

## Configuration & Settings

The Configuration page shows your system status and settings.

### API Keys

**OpenAI API Key:**
- Required for AI summarization
- Shows as `***` if configured
- Managed through environment variables

**Resend Email Service:**
- Shows connection status
- Displays the "from" email address
- Managed through Replit integrations

### News Sources

A read-only list of all configured RSS feeds.

### Schedule Settings

Shows when newsletters are automatically generated (default: 7:00 AM daily).

---

## Common Tasks

### How to Create a Weekly Digest Newsletter

1. Go to **Newsletter Management**
2. Create new newsletter: "Weekly AI Digest"
3. Select only high-priority feeds (MIT News, OpenAI Blog, etc.)
4. Set max stories to 20 (more content for weekly)
5. Customize branding with your colors
6. Generate manually once a week

### How to Create a Research-Only Newsletter

1. Go to **Newsletter Management**
2. Create newsletter: "AI Research Roundup"
3. Feed selection: Choose only Research feeds
4. Category selection: Choose only "AI Research" and "Machine Learning"
5. Set max stories to 10
6. Generate as needed

### How to Test Before Sending Emails

1. Generate newsletter with email sending disabled
2. View in Archive
3. Download HTML
4. Check content and formatting
5. When ready, enable email sending in code

### How to Change Newsletter Colors

1. Go to **Newsletter Management**
2. Find your newsletter
3. Click **"Customize Branding"**
4. Click the color pickers
5. Select your colors
6. Save changes
7. Next generated newsletter uses new colors

### How to Add Your Logo

1. Prepare logo image (PNG or JPG, recommended: 200-400px wide)
2. Go to **Newsletter Management**
3. Click **"Customize Branding"**
4. Click **"Browse"** under Logo Upload
5. Select your image
6. Toggle **"Show Logo"** on
7. Save changes

---

## Tips & Best Practices

### Newsletter Generation

✅ **Do:**
- Generate newsletters during low-traffic hours
- Review generated newsletters before sending
- Keep max stories between 10-15 for best readability
- Use descriptive newsletter names

❌ **Don't:**
- Generate multiple newsletters simultaneously
- Include too many stories (makes newsletter too long)
- Forget to check API key status before generating

### Feed Management

✅ **Do:**
- Start with 10-15 quality sources
- Test new feeds before adding permanently
- Disable unreliable feeds rather than deleting
- Organize feeds by category

❌ **Don't:**
- Add too many feeds (slows down generation)
- Use feeds that rarely update
- Keep broken/dead feeds enabled

### Category Organization

✅ **Do:**
- Use clear, descriptive category names
- Choose relevant emojis for visual appeal
- Set logical priority order
- Group similar topics together

❌ **Don't:**
- Create too many categories (keeps things simple)
- Use priority numbers randomly
- Disable categories that are actively used

### Branding

✅ **Do:**
- Use high-contrast colors for readability
- Test logos at different sizes
- Keep CTA buttons action-oriented ("Learn More", "Subscribe")
- Use consistent branding across newsletters

❌ **Don't:**
- Use light text on light backgrounds
- Upload huge logo files (compress first)
- Add too many CTA buttons (max 3)
- Use generic button text like "Click Here"

---

## Troubleshooting

### Problem: Newsletter generation fails

**Possible causes:**
- OpenAI API key missing or invalid
- Network connectivity issues
- RSS feeds are down
- Another generation already in progress

**Solutions:**
1. Check Configuration page - is OpenAI connected?
2. Wait 5 minutes and try again
3. Check Dashboard for recent activity
4. Try generating with fewer feeds

---

### Problem: No articles found

**Possible causes:**
- Feeds haven't published new content
- RSS feed URLs changed
- Network issues

**Solutions:**
1. Go to RSS Feed Management
2. Check if feeds are enabled
3. Try visiting feed URLs in browser
4. Disable problematic feeds temporarily
5. Try again in a few hours when new content published

---

### Problem: Duplicate stories appearing

**Possible causes:**
- Deduplication threshold too strict
- Stories are slightly different

**This is normal!** The app uses 60% similarity threshold. If stories are less than 60% similar, they're considered unique.

---

### Problem: Email not sending

**Possible causes:**
- Resend not configured
- Email sending code commented out
- No recipient addresses configured

**Solutions:**
1. Check Configuration page - is Resend connected?
2. Email sending is currently disabled by default for safety
3. To enable: See code comments in `app.py` and `scheduler.py`
4. Add recipient email addresses before enabling

---

### Problem: Can't see Markdown download option

**This is normal for old newsletters.** Only newsletters created after the Markdown feature was added have this option.

---

### Problem: Branding changes not appearing

**Solution:**
1. Make sure you clicked "Save Branding"
2. Generate a NEW newsletter (existing ones keep old branding)
3. Check the Archive to view the latest newsletter

---

### Problem: Categories appear in wrong order

**Solution:**
1. Go to Category Management
2. Edit the Priority numbers
3. Lower priority = appears first
4. Generate new newsletter to see changes

---

## Need More Help?

### Quick Reference

- **Dashboard** = Overview and stats
- **Generate Newsletter** = Create new newsletter
- **Newsletter Archive** = View past newsletters
- **Newsletter Management** = Configure newsletter profiles
- **RSS Feed Management** = Manage news sources
- **Category Management** = Organize story sections
- **Configuration** = Check API connections

### Video Tour

Look for visual indicators:
- ✅ = Success/Connected
- ❌ = Error/Not configured
- ⚠️ = Warning
- 🚀 = Action button
- 📊 = Statistics
- ⚙️ = Settings

---

## Glossary

**RSS Feed:** A web feed that publishes frequently updated content (like news articles)

**Deduplication:** Process of finding and removing duplicate stories from different sources

**AI Summarization:** Using artificial intelligence to create short summaries of long articles

**Impact Score:** Rating of how important/significant a story is (1-10 scale)

**Newsletter Configuration:** A saved profile with specific feeds, categories, and branding

**Branding:** Visual customization (logo, colors, fonts) for your newsletter

**CTA (Call-to-Action):** Clickable button that encourages readers to take action

**Markdown:** Plain text format that's easy to read and edit

**HTML:** Web page format used for emails and browsers

---

**Happy Newsletter Creating! 🎉**

*Last Updated: November 2025*
