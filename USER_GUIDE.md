dd New RSS Feed"**

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
