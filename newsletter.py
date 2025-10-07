from typing import List, Dict
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsletterGenerator:
    def __init__(self):
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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
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

    def generate_newsletter(self, summarized_stories: List[Dict]) -> str:
        """Generate complete HTML newsletter from summarized stories"""
        if not summarized_stories:
            return self._generate_empty_newsletter()
        
        # Sort stories by impact score (highest first)
        sorted_stories = sorted(summarized_stories, 
                              key=lambda x: x.get('impact_score', 0), 
                              reverse=True)
        
        # Generate newsletter components
        header_html = self._generate_header(sorted_stories)
        stats_html = self._generate_stats(sorted_stories)
        stories_html = self._generate_stories_html(sorted_stories)
        footer_html = self._generate_footer()
        
        # Combine all components
        newsletter_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Daily Newsletter - {datetime.now().strftime('%B %d, %Y')}</title>
            {self.template_style}
        </head>
        <body>
            <div class="container">
                {header_html}
                <div class="content">
                    {stats_html}
                    {stories_html}
                </div>
                {footer_html}
            </div>
        </body>
        </html>
        """
        
        return newsletter_html

    def _generate_header(self, stories: List[Dict]) -> str:
        """Generate newsletter header"""
        current_date = datetime.now().strftime('%B %d, %Y')
        story_count = len(stories)
        
        return f"""
        <div class="header">
            <h1>🤖 AI Daily</h1>
            <p>Your curated AI & technology newsletter for {current_date}</p>
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
        """Generate HTML for all stories"""
        stories_html = ""
        
        for story in stories:
            story_html = self._generate_story_html(story)
            stories_html += story_html
        
        return stories_html

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
                    <h1>🤖 AI Daily</h1>
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
