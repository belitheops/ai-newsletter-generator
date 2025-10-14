import os
from openai import OpenAI
from typing import Dict, List
import logging
import json
from category_manager import CategoryManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArticleSummarizer:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
        
        # Using GPT-4 Turbo for reliable summarization
        self.model = "gpt-4-turbo-preview"
        
        # Load categories from CategoryManager
        self.category_manager = CategoryManager()
        self.valid_categories = self.category_manager.get_category_names(enabled_only=True)
    
    def reload_categories(self):
        """Reload categories from CategoryManager (useful when categories are updated)"""
        self.category_manager = CategoryManager()
        self.valid_categories = self.category_manager.get_category_names(enabled_only=True)
        logger.info(f"Reloaded categories: {len(self.valid_categories)} categories available")

    def summarize_story(self, story: Dict) -> Dict:
        """
        Summarize a single story using OpenAI
        Returns story with added summary and metadata
        """
        try:
            # Prepare content for summarization
            title = story.get('title', '')
            content = story.get('full_content', '')
            source = story.get('source', '')
            
            # Combine title and content, limit to avoid token limits
            text_to_summarize = f"Title: {title}\n\nContent: {content[:3000]}"
            
            if not text_to_summarize.strip():
                logger.warning(f"No content to summarize for story: {title}")
                return self._create_fallback_summary(story)
            
            # Create summary using OpenAI
            summary_data = self._generate_summary(text_to_summarize, source)
            
            # Add summary to story
            summarized_story = story.copy()
            summarized_story.update({
                'summary': summary_data.get('summary', ''),
                'key_points': summary_data.get('key_points', []),
                'impact_score': summary_data.get('impact_score', 5),
                'category': summary_data.get('category', 'AI/Technology'),
                'summary_generated_at': self._get_current_timestamp()
            })
            
            return summarized_story
            
        except Exception as e:
            logger.error(f"Error summarizing story '{story.get('title', 'Unknown')}': {e}")
            return self._create_fallback_summary(story)

    def _generate_summary(self, text: str, source: str) -> Dict:
        """Generate summary using OpenAI API"""
        if not self.client:
            logger.error("OpenAI client not initialized - API key missing")
            raise ValueError("OpenAI API key not configured")
            
        try:
            categories_list = ', '.join([f'"{cat}"' for cat in self.valid_categories])
            
            prompt = f"""
            Please analyze the following AI/technology news article and provide a comprehensive summary.
            
            Article text:
            {text}
            
            Please provide your response in JSON format with the following structure:
            {{
                "summary": "A concise 2-3 sentence summary of the main story",
                "key_points": ["bullet point 1", "bullet point 2", "bullet point 3"],
                "impact_score": 7,
                "category": "AI/Technology category"
            }}
            
            Guidelines:
            - Keep the summary concise but informative (50-100 words)
            - Include 2-4 key points that capture the most important aspects
            - Rate impact on a scale of 1-10 (1=minor news, 10=major breakthrough)
            - Categorize as one of: {categories_list}
            - Focus on what's new or significant about this story
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert AI/technology news analyst. Provide concise, accurate summaries of tech news articles."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and clean the response
            return self._validate_summary_response(result)
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise

    def _validate_summary_response(self, result: Dict) -> Dict:
        """Validate and clean the OpenAI response"""
        validated = {
            'summary': str(result.get('summary', '')).strip(),
            'key_points': [],
            'impact_score': 5,
            'category': 'Other'
        }
        
        # Validate key points
        key_points = result.get('key_points', [])
        if isinstance(key_points, list):
            validated['key_points'] = [str(point).strip() for point in key_points[:4]]  # Max 4 points
        
        # Validate impact score
        try:
            impact = int(result.get('impact_score', 5))
            validated['impact_score'] = max(1, min(10, impact))  # Clamp between 1-10
        except (ValueError, TypeError):
            validated['impact_score'] = 5
        
        # Validate category - use custom categories
        category = result.get('category', 'Other')
        validated['category'] = category if category in self.valid_categories else 'Other'
        
        return validated

    def _create_fallback_summary(self, story: Dict) -> Dict:
        """Create a basic summary when OpenAI fails"""
        title = story.get('title', 'No title available')
        content = story.get('full_content', '')
        
        # Create basic summary from title and first sentence of content
        first_sentence = content.split('.')[0][:200] if content else "No content available"
        
        fallback_story = story.copy()
        fallback_story.update({
            'summary': f"{title}. {first_sentence}.",
            'key_points': [title] if title != 'No title available' else [],
            'impact_score': 5,
            'category': 'Other',
            'summary_generated_at': self._get_current_timestamp(),
            'fallback_summary': True
        })
        
        return fallback_story

    def summarize_multiple_stories(self, stories: List[Dict]) -> List[Dict]:
        """Summarize multiple stories"""
        summarized_stories = []
        
        for i, story in enumerate(stories):
            logger.info(f"Summarizing story {i+1}/{len(stories)}: {story.get('title', 'Unknown')}")
            summarized_story = self.summarize_story(story)
            summarized_stories.append(summarized_story)
        
        return summarized_stories

    def get_summary_statistics(self, summarized_stories: List[Dict]) -> Dict:
        """Get statistics about the summarization process"""
        total_stories = len(summarized_stories)
        
        # Count fallback summaries
        fallback_count = sum(1 for story in summarized_stories if story.get('fallback_summary', False))
        
        # Category distribution
        categories = {}
        for story in summarized_stories:
            category = story.get('category', 'Other')
            categories[category] = categories.get(category, 0) + 1
        
        # Average impact score
        impact_scores = [story.get('impact_score', 5) for story in summarized_stories]
        avg_impact = sum(impact_scores) / len(impact_scores) if impact_scores else 0
        
        stats = {
            'total_stories_summarized': total_stories,
            'successful_summaries': total_stories - fallback_count,
            'fallback_summaries': fallback_count,
            'success_rate': (total_stories - fallback_count) / total_stories if total_stories > 0 else 0,
            'category_distribution': categories,
            'average_impact_score': round(avg_impact, 1),
            'high_impact_stories': sum(1 for score in impact_scores if score >= 7)
        }
        
        return stats

    def _get_current_timestamp(self) -> str:
        """Get current timestamp as ISO string"""
        from datetime import datetime
        return datetime.now().isoformat()
