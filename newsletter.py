from typing import List, Dict
from datetime import datetime
import logging
import base64
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsletterGenerator:
    def __init__(self):
        self.logo_base64 = None  # Lazy load when needed
        
        self.template_style = """
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8f9fa;
            }
            .container {
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: black;
                color: #cda600;
                padding: 40px 30px;
                text-align: center;
            }
            .header img {
                max-width: 400px;
                width: 100%;
                height: auto;
                margin-bottom: 20px;
            }
            .header h1 {
                margin: 0;
                font-size: 2.5em;
                font-weight: 700;
            }
            .header p {
                margin: 10px 0 0 0;
                font-size: 1.1em;
                opacity: 0.9;
            }
            .content {
                padding: 30px;
            }
            .summary-section {
                margin-bottom: 20px;
                background: #f8f9fa;
                border-radius: 6px;
                padding: 15px;
                border-left: 4px solid #667eea;
            }
            .stats {
                background: #e3f2fd;
                border-radius: 6px;
                padding: 20px;
                margin-bottom: 30px;
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
            }
            .stat-item {
                text-align: center;
                margin: 5px;
            }
            .stat-number {
                font-size: 2em;
                font-weight: bold;
                color: #1976d2;
                display: block;
            }
            .stat-label {
                color: #666;
                font-size: 0.9em;
            }
            .story {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin-bottom: 25px;
                overflow: hidden;
                transition: box-shadow 0.2s;
            }
            .story:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            .story-header {
                padding: 20px;
                background: white;
            }
            .story-title {
                font-size: 1.4em;
                font-weight: 600;
                color: #333;
                margin-bottom: 10px;
                line-height: 1.3;
            }
            .story-meta {
                display: flex;
                gap: 15px;
                margin-bottom: 15px;
                font-size: 0.9em;
                color: #666;
                flex-wrap: wrap;
            }
            .story-category {
                background: #667eea;
                color: white;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8em;
                font-weight: 500;
            }
            .story-impact {
                display: flex;
                align-items: center;
                gap: 5px;
            }
            .story-sources {
                color: #888;
            }
            .story-summary {
                font-size: 1.1em;
                line-height: 1.6;
                color: #444;
                margin-bottom: 15px;
            }
            .key-points {
                background: #f5f5f5;
                border-radius: 4px;
                padding: 15px;
                margin-top: 15px;
            }
            .key-points h4 {
                margin: 0 0 10px 0;
                color: #555;
                font-size: 0.95em;
                font-weight: 600;
            }
            .key-points ul {
                margin: 0;
                padding-left: 20px;
            }
            .key-points li {
                margin-bottom: 5px;
                color: #666;
                font-size: 0.9em;
            }
            .read-more {
                display: inline-block;
                color: #667eea;
                text-decoration: none;
                font-weight: 500;
                margin-top: 10px;
            }
            .read-more:hover {
                text-decoration: underline;
            }
            .footer {
                background: #f8f9fa;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #e0e0e0;
                color: #666;
            }
            .consolidated-badge {
                background: #ff9800;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.75em;
                font-weight: bold;
            }
            .category-section {
                margin-bottom: 40px;
            }
            .category-header {
                font-size: 1.8em;
                color: #333;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 3px solid #667eea;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .category-count {
                font-size: 0.6em;
                color: #888;
                font-weight: normal;
            }
            .category-cta {
                background: linear-gradient(135deg, #cda600 0%, #b89400 100%);
                border-radius: 8px;
                padding: 25px;
                margin: 30px 0 40px 0;
                text-align: center;
                color: white;
            }
            .category-cta h3 {
                margin: 0 0 15px 0;
                font-size: 1.3em;
                font-weight: 600;
            }
            .category-cta p {
                margin: 0 0 20px 0;
                font-size: 1em;
                opacity: 0.95;
            }
            .cta-button {
                display: inline-block;
                background: white;
                color: #cda600;
                padding: 12px 30px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: 600;
                font-size: 1em;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .cta-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
            @media (max-width: 600px) {
                body {
                    padding: 10px;
                }
                .header {
                    padding: 30px 20px;
                }
                .header h1 {
                    font-size: 2em;
                }
                .content {
                    padding: 20px;
                }
                .stats {
                    flex-direction: column;
                    gap: 10px;
                }
                .story-meta {
                    flex-direction: column;
                    gap: 8px;
                }
            }
        </style>
        """

    def generate_newsletter(self, summarized_stories: List[Dict], title: str = None, branding: Dict = None, cta_buttons: List[Dict] = None) -> str:
        """Generate complete HTML newsletter from summarized stories"""
        if not summarized_stories:
            return self._generate_empty_newsletter()
        
        # Sort stories by impact score (highest first)
        sorted_stories = sorted(summarized_stories, 
                              key=lambda x: x.get('impact_score', 0), 
                              reverse=True)
        
        # Use provided title or generate default
        if not title:
            title = f"AI Daily Newsletter - {datetime.now().strftime('%B %d, %Y')}"
        
        # Use provided branding or defaults
        if not branding:
            branding = {
                'header_color': '#000000',
                'header_text_color': '#cda600',
                'header_font': 'Arial, sans-serif',
                'logo_path': 'attached_assets/Innopower Logo white background_1760182832027.png',
                'logo_enabled': True
            }
        
        # Generate newsletter components with branding
        header_html = self._generate_header(sorted_stories, title, branding)
        stats_html = self._generate_stats(sorted_stories)
        stories_html = self._generate_stories_html(sorted_stories)
        cta_html = self._generate_cta_buttons(cta_buttons, branding)
        footer_html = self._generate_footer()
        
        # Generate custom styles with branding colors and fonts
        custom_style = self._generate_custom_style(branding)
        
        # Combine all components
        newsletter_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            {self.template_style}
            {custom_style}
        </head>
        <body>
            <div class="container">
                {header_html}
                <div class="content">
                    {stats_html}
                    {stories_html}
                    {cta_html}
                </div>
                {footer_html}
            </div>
        </body>
        </html>
        """
        
        return newsletter_html

    def _load_logo(self, logo_path: str = None) -> str:
        """Load and encode logo as base64"""
        try:
            if not logo_path:
                logo_path = "attached_assets/Innopower Logo white background_1760182832027.png"
            
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    logo_data = base64.b64encode(f.read()).decode('utf-8')
                    return f"data:image/png;base64,{logo_data}"
            else:
                logger.warning(f"Logo file not found: {logo_path}")
                return ""
        except Exception as e:
            logger.error(f"Error loading logo: {e}")
            return ""
    
    def _generate_custom_style(self, branding: Dict) -> str:
        """Generate custom CSS based on branding settings"""
        header_color = branding.get('header_color', '#000000')
        header_text_color = branding.get('header_text_color', '#cda600')
        header_font = branding.get('header_font', 'Arial, sans-serif')
        
        return f"""
        <style>
            .header {{
                background: {header_color} !important;
                font-family: {header_font} !important;
            }}
            .header p {{
                color: {header_text_color} !important;
                font-family: {header_font} !important;
            }}
            .header h1 {{
                color: {header_text_color} !important;
                font-family: {header_font} !important;
            }}
        </style>
        """
    
    def _generate_header(self, stories: List[Dict], title: str = None, branding: Dict = None) -> str:
        """Generate newsletter header"""
        current_date = datetime.now().strftime('%B %d, %Y')
        story_count = len(stories)
        
        # Use provided title or generate default
        if not title:
            title = f"AI Daily Newsletter - {current_date}"
        
        # Use provided branding or defaults
        if not branding:
            branding = {'logo_enabled': True, 'logo_path': None}
        
        # Load logo with custom path if provided
        logo_path = branding.get('logo_path')
        logo_base64 = self._load_logo(logo_path)
        
        # Show logo if enabled
        if branding.get('logo_enabled', True) and logo_base64:
            logo_html = f'<img src="{logo_base64}" alt="Newsletter Logo">'
        else:
            logo_html = '<h1>AI Daily</h1>'
        
        return f"""
        <div class="header">
            {logo_html}
            <p>{title}</p>
        </div>
        """

    def _generate_stats(self, stories: List[Dict]) -> str:
        """Generate newsletter statistics section"""
        total_stories = len(stories)
        
        # Calculate category distribution
        categories = {}
        total_sources = 0
        high_impact_count = 0
        
        for story in stories:
            category = story.get('category', 'Other')
            categories[category] = categories.get(category, 0) + 1
            
            if story.get('is_consolidated'):
                total_sources += story.get('source_count', 1)
            else:
                total_sources += 1
                
            if story.get('impact_score', 0) >= 7:
                high_impact_count += 1
        
        top_category = max(categories.items(), key=lambda x: x[1])[0] if categories else "N/A"
        
        return f"""
        <div class="stats">
            <div class="stat-item">
                <span class="stat-number">{total_stories}</span>
                <span class="stat-label">Unique Stories</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{total_sources}</span>
                <span class="stat-label">Sources Analyzed</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{high_impact_count}</span>
                <span class="stat-label">High Impact</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{top_category}</span>
                <span class="stat-label">Top Category</span>
            </div>
        </div>
        """

    def _generate_stories_html(self, stories: List[Dict]) -> str:
        """Generate HTML for all stories, grouped by category"""
        # Group stories by category
        from collections import defaultdict
        categories = defaultdict(list)
        
        for story in stories:
            category = story.get('category', 'Other')
            # Coerce to string and normalize to "Other" for resilience
            category = str(category).strip() if category else 'Other'
            if not category:
                category = 'Other'
            categories[category].append(story)
        
        # Define preferred category order (most important first)
        preferred_order = [
            'AI Policy', 'AI Business', 'AI Research', 'AI Products', 
            'Machine Learning', 'Robotics', 'Tech Industry'
        ]
        
        # Collect all categories: preferred order first, then remaining categories alphabetically, then 'Other' last
        remaining_categories = sorted([cat for cat in categories.keys() 
                                      if cat not in preferred_order and cat != 'Other'])
        all_categories = preferred_order + remaining_categories
        if 'Other' in categories:
            all_categories.append('Other')
        
        stories_html = ""
        
        # CTA messages to rotate through
        cta_messages = [
            {
                "title": "Stay Ahead of AI Innovation",
                "message": "Join the Innopower community for exclusive insights, AI trends, and networking opportunities.",
                "button_text": "Visit Innopower.ai",
                "url": "https://innopower.ai"
            },
            {
                "title": "Connect with AI Leaders",
                "message": "Attend our next Innopower event to network with AI innovators and industry experts.",
                "button_text": "Explore Events",
                "url": "https://innopower.ai"
            },
            {
                "title": "Join the AI Revolution",
                "message": "Follow Innopower for cutting-edge AI insights, resources, and community updates.",
                "button_text": "Follow Innopower",
                "url": "https://innopower.ai"
            }
        ]
        
        # Generate stories grouped by category
        for idx, category in enumerate(all_categories):
            if category in categories and categories[category]:
                # Add category section header
                stories_html += f"""
                <div class="category-section">
                    <h2 class="category-header">
                        {self._get_category_icon(category)} {category}
                        <span class="category-count">({len(categories[category])} stories)</span>
                    </h2>
                """
                
                # Add stories in this category
                for story in categories[category]:
                    story_html = self._generate_story_html(story)
                    stories_html += story_html
                
                # Add CTA at bottom of category (rotate through messages)
                cta = cta_messages[idx % len(cta_messages)]
                stories_html += f"""
                <div class="category-cta">
                    <h3>{cta['title']}</h3>
                    <p>{cta['message']}</p>
                    <a href="{cta['url']}" class="cta-button" target="_blank" rel="noopener">{cta['button_text']}</a>
                </div>
                """
                
                stories_html += "</div>"
        
        return stories_html
    
    def _get_category_icon(self, category: str) -> str:
        """Get emoji icon for category"""
        icons = {
            'AI Policy': '⚖️',
            'AI Business': '💼',
            'AI Research': '🔬',
            'AI Products': '🚀',
            'Machine Learning': '🤖',
            'Robotics': '🦾',
            'Tech Industry': '💻',
            'Other': '📰'
        }
        return icons.get(category, '📰')

    def _generate_story_html(self, story: Dict) -> str:
        """Generate HTML for a single story"""
        title = story.get('title', 'Untitled')
        summary = story.get('summary', 'No summary available')
        category = story.get('category', 'Other')
        impact_score = story.get('impact_score', 5)
        key_points = story.get('key_points', [])
        url = story.get('url', '#')
        source = story.get('source', 'Unknown')
        
        # Generate impact stars
        impact_stars = '⭐' * min(impact_score, 5)
        
        # Handle consolidated stories
        consolidated_badge = ""
        sources_info = source
        if story.get('is_consolidated'):
            source_count = story.get('source_count', 1)
            consolidated_badge = f'<span class="consolidated-badge">CONSOLIDATED</span>'
            all_sources = story.get('all_sources', [])
            sources_info = f"{source_count} sources: {', '.join(all_sources[:3])}{'...' if len(all_sources) > 3 else ''}"
        
        # Generate key points HTML
        key_points_html = ""
        if key_points:
            points_list = ''.join([f'<li>{point}</li>' for point in key_points])
            key_points_html = f"""
            <div class="key-points">
                <h4>Key Points:</h4>
                <ul>{points_list}</ul>
            </div>
            """
        
        return f"""
        <div class="story">
            <div class="story-header">
                <h2 class="story-title">{title}</h2>
                <div class="story-meta">
                    <span class="story-category">{category}</span>
                    <div class="story-impact">
                        <span>Impact: {impact_stars} ({impact_score}/10)</span>
                    </div>
                    <span class="story-sources">{sources_info}</span>
                    {consolidated_badge}
                </div>
                <div class="story-summary">{summary}</div>
                {key_points_html}
                <a href="{url}" class="read-more" onclick="window.open('{url}', '_blank'); return false;" rel="noopener">Read Full Article →</a>
            </div>
        </div>
        """

    def _generate_cta_buttons(self, cta_buttons: List[Dict] = None, branding: Dict = None) -> str:
        """Generate CTA buttons section"""
        if not cta_buttons:
            return ""
        
        # Get button color from branding (use header_text_color as button color)
        button_color = branding.get('header_text_color', '#cda600') if branding else '#cda600'
        
        # Filter out empty buttons
        active_buttons = [btn for btn in cta_buttons if btn.get('text') and btn.get('link')]
        
        if not active_buttons:
            return ""
        
        # Generate button HTML
        buttons_html = ""
        for button in active_buttons:
            buttons_html += f"""
            <a href="{button['link']}" class="cta-button" style="background-color: {button_color}; color: #ffffff; text-decoration: none; padding: 12px 30px; border-radius: 5px; display: inline-block; margin: 10px 5px; font-weight: bold;">
                {button['text']}
            </a>
            """
        
        return f"""
        <div style="text-align: center; margin: 40px 0; padding: 30px 0; border-top: 2px solid #eee; border-bottom: 2px solid #eee;">
            {buttons_html}
        </div>
        """
    
    def _generate_footer(self) -> str:
        """Generate newsletter footer"""
        current_time = datetime.now().strftime('%I:%M %p %Z')
        
        return f"""
        <div class="footer">
            <p><strong>AI Daily Newsletter</strong> - Powered by intelligent curation</p>
            <p>Generated on {datetime.now().strftime('%B %d, %Y')} at {current_time}</p>
            <p>This newsletter aggregates and summarizes AI news from 10+ trusted sources</p>
            <p style="font-size: 0.8em; color: #999; margin-top: 15px;">
                Stories are automatically curated, deduplicated, and summarized using advanced AI
            </p>
        </div>
        """

    def _generate_empty_newsletter(self) -> str:
        """Generate newsletter when no stories are available"""
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Lazy load logo
        if self.logo_base64 is None:
            self.logo_base64 = self._load_logo()
        
        logo_html = f'<img src="{self.logo_base64}" alt="Innopower Logo">' if self.logo_base64 else '<h1>AI Daily</h1>'
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Daily Newsletter - {current_date}</title>
            {self.template_style}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    {logo_html}
                    <p>Your curated AI & technology newsletter for {current_date}</p>
                </div>
                <div class="content">
                    <div class="summary-section">
                        <h2>No Stories Available</h2>
                        <p>We weren't able to find any new AI/technology stories today. This might be due to:</p>
                        <ul>
                            <li>Technical issues with news source scraping</li>
                            <li>No new articles published in the last 24 hours</li>
                            <li>All articles were filtered out during deduplication</li>
                        </ul>
                        <p>Please try again later or contact support if this issue persists.</p>
                    </div>
                </div>
                <div class="footer">
                    <p><strong>AI Daily Newsletter</strong> - Powered by intelligent curation</p>
                    <p>Generated on {current_date}</p>
                </div>
            </div>
        </body>
        </html>
        """

    def generate_text_version(self, summarized_stories: List[Dict]) -> str:
        """Generate plain text version of the newsletter"""
        if not summarized_stories:
            return "AI Daily Newsletter - No stories available today"
        
        current_date = datetime.now().strftime('%B %d, %Y')
        text_content = f"""
AI DAILY NEWSLETTER
{current_date}
{'=' * 50}

Today's AI & Technology Stories: {len(summarized_stories)}

"""
        
        # Sort by impact score
        sorted_stories = sorted(summarized_stories, 
                              key=lambda x: x.get('impact_score', 0), 
                              reverse=True)
        
        for i, story in enumerate(sorted_stories, 1):
            title = story.get('title', 'Untitled')
            summary = story.get('summary', 'No summary available')
            category = story.get('category', 'Other')
            impact_score = story.get('impact_score', 5)
            url = story.get('url', '')
            
            text_content += f"""
{i}. {title}
Category: {category} | Impact: {impact_score}/10
{summary}
Read more: {url}

{'---'}

"""
        
        text_content += f"""
Newsletter generated automatically by AI Daily
Powered by intelligent curation and summarization
"""
        
        return text_content

    def generate_markdown(self, summarized_stories: List[Dict], title: str = None, cta_buttons: List[Dict] = None) -> str:
        """Generate markdown version of the newsletter"""
        if not summarized_stories:
            return "# AI Daily Newsletter\n\nNo stories available today"
        
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Use provided title or generate default
        if not title:
            newsletter_title = f"AI Daily Newsletter: {current_date}"
        else:
            newsletter_title = title
        
        markdown_content = f"""---

{newsletter_title}
Your curated AI & technology newsletter

---

Total Stories Today: {len(summarized_stories)}

---

"""
        
        # Group stories by category
        categorized_stories = {}
        for story in summarized_stories:
            category = story.get('category', 'Other')
            if not category or not isinstance(category, str):
                category = 'Other'
            
            if category not in categorized_stories:
                categorized_stories[category] = []
            categorized_stories[category].append(story)
        
        # Category order and emoji mapping
        category_order = ['AI Policy', 'AI Business', 'AI Research', 'AI Products', 'Machine Learning', 'Robotics', 'Tech Industry']
        category_emojis = {
            'AI Policy': '⚖️',
            'AI Business': '💼',
            'AI Research': '🔬',
            'AI Products': '🚀',
            'Machine Learning': '🤖',
            'Robotics': '🦾',
            'Tech Industry': '💻',
            'Other': '📰'
        }
        
        # Process categories in order
        processed_categories = []
        for category in category_order:
            if category in categorized_stories:
                processed_categories.append(category)
        
        # Add remaining categories alphabetically
        for category in sorted(categorized_stories.keys()):
            if category not in processed_categories and category != 'Other':
                processed_categories.append(category)
        
        # Add 'Other' last if it exists
        if 'Other' in categorized_stories:
            processed_categories.append('Other')
        
        # Prepare CTA buttons
        active_ctas = []
        if cta_buttons:
            active_ctas = [btn for btn in cta_buttons if btn.get('text') and btn.get('link')]
        
        # Generate markdown for each category
        cta_index = 0
        for cat_idx, category in enumerate(processed_categories):
            stories = categorized_stories[category]
            emoji = category_emojis.get(category, '📰')
            
            markdown_content += f"{emoji} {category}\n"
            
            # Sort stories by impact score within category
            sorted_stories = sorted(stories, key=lambda x: x.get('impact_score', 0), reverse=True)
            
            for story in sorted_stories:
                title = story.get('title', 'Untitled')
                summary = story.get('summary', 'No summary available')
                impact_score = story.get('impact_score', 5)
                url = story.get('url', '')
                key_points = story.get('key_points', [])
                
                markdown_content += f"{title}\n"
                markdown_content += f"Impact Score: {impact_score}/10\n"
                markdown_content += f"{summary}\n"
                
                if key_points:
                    markdown_content += "Key Points:\n"
                    for point in key_points:
                        markdown_content += f"{point}\n"
                    markdown_content += "\n"
                
                if url:
                    markdown_content += f"Read Full Article\n\n"
                
                markdown_content += "---\n\n"
            
            # Add CTA button after some categories
            if active_ctas and cta_index < len(active_ctas):
                # Add CTA after every 2-3 categories
                if (cat_idx + 1) % 2 == 0 or cat_idx == len(processed_categories) - 1:
                    cta = active_ctas[cta_index]
                    markdown_content += f"{cta['text']}\n{cta['link']}\n\n---\n\n"
                    cta_index += 1
        
        # Footer
        markdown_content += f"""Innopower AI Newsletter Powered by intelligent curation and AI summarization Generated on {current_date} Visit Innopower.ai
"""
        
        return markdown_content
