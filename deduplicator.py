import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import logging
import re
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StoryDeduplicator:
    def __init__(self, similarity_threshold: float = 0.6):
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )

    def deduplicate_stories(self, articles: List[Dict]) -> List[Dict]:
        """
        Deduplicate and consolidate similar stories from multiple sources
        Returns list of unique stories with consolidated information
        """
        if not articles:
            return []
        
        logger.info(f"Starting deduplication of {len(articles)} articles")
        
        # Prepare text for similarity analysis
        article_texts = []
        for article in articles:
            # Combine title and content for better similarity detection
            text = f"{article.get('title', '')} {article.get('full_content', '')[:500]}"  # First 500 chars
            article_texts.append(self._preprocess_text(text))
        
        # Calculate similarity matrix
        similarity_matrix = self._calculate_similarity_matrix(article_texts)
        
        # Find duplicate groups
        duplicate_groups = self._find_duplicate_groups(similarity_matrix)
        
        # Consolidate duplicate stories
        unique_stories = self._consolidate_duplicate_groups(articles, duplicate_groups)
        
        logger.info(f"Consolidated {len(articles)} articles into {len(unique_stories)} unique stories")
        
        return unique_stories

    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for similarity analysis"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Convert to lowercase
        text = text.lower().strip()
        
        return text

    def _calculate_similarity_matrix(self, texts: List[str]) -> np.ndarray:
        """Calculate cosine similarity matrix for all text pairs"""
        try:
            # Fit TF-IDF vectorizer
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            return similarity_matrix
        
        except Exception as e:
            logger.error(f"Error calculating similarity matrix: {e}")
            # Return identity matrix as fallback
            n = len(texts)
            return np.eye(n)

    def _find_duplicate_groups(self, similarity_matrix: np.ndarray) -> List[List[int]]:
        """Find groups of similar articles based on similarity threshold"""
        n_articles = similarity_matrix.shape[0]
        visited = set()
        duplicate_groups = []
        
        for i in range(n_articles):
            if i in visited:
                continue
            
            # Find all articles similar to article i
            similar_indices = []
            for j in range(n_articles):
                if i != j and similarity_matrix[i][j] >= self.similarity_threshold:
                    similar_indices.append(j)
            
            if similar_indices:
                # Create group with article i and its similar articles
                group = [i] + similar_indices
                duplicate_groups.append(group)
                
                # Mark all articles in this group as visited
                for idx in group:
                    visited.add(idx)
            else:
                # Article i is unique
                duplicate_groups.append([i])
                visited.add(i)
        
        return duplicate_groups

    def _consolidate_duplicate_groups(self, articles: List[Dict], duplicate_groups: List[List[int]]) -> List[Dict]:
        """Consolidate duplicate articles into single representative stories"""
        consolidated_stories = []
        
        for group in duplicate_groups:
            if len(group) == 1:
                # Single article, no consolidation needed
                consolidated_stories.append(articles[group[0]])
            else:
                # Multiple articles, consolidate them
                consolidated_story = self._consolidate_group(articles, group)
                consolidated_stories.append(consolidated_story)
        
        return consolidated_stories

    def _consolidate_group(self, articles: List[Dict], group_indices: List[int]) -> Dict:
        """Consolidate multiple similar articles into a single story"""
        group_articles = [articles[i] for i in group_indices]
        
        # Choose the article with the most content as primary
        primary_article = max(group_articles, key=lambda x: len(x.get('full_content', '')))
        
        # Consolidate information
        consolidated_story = {
            'title': primary_article.get('title', ''),
            'url': primary_article.get('url', ''),
            'full_content': primary_article.get('full_content', ''),
            'published_date': primary_article.get('published_date', ''),
            'source': primary_article.get('source', ''),
            'is_consolidated': True,
            'source_count': len(group_articles),
            'all_sources': [article.get('source', '') for article in group_articles],
            'all_urls': [article.get('url', '') for article in group_articles],
            'consolidation_reason': f"Similar story found across {len(group_articles)} sources"
        }
        
        # If primary article has limited content, try to get more from other sources
        if len(consolidated_story['full_content']) < 200:
            for article in group_articles:
                content = article.get('full_content', '')
                if len(content) > len(consolidated_story['full_content']):
                    consolidated_story['full_content'] = content
                    consolidated_story['url'] = article.get('url', '')
        
        return consolidated_story

    def get_duplicate_statistics(self, articles: List[Dict], unique_stories: List[Dict]) -> Dict:
        """Get statistics about the deduplication process"""
        total_articles = len(articles)
        unique_stories_count = len(unique_stories)
        duplicates_removed = total_articles - unique_stories_count
        
        # Count consolidated stories
        consolidated_count = sum(1 for story in unique_stories if story.get('is_consolidated', False))
        
        # Source distribution
        source_counts = defaultdict(int)
        for article in articles:
            source_counts[article.get('source', 'Unknown')] += 1
        
        stats = {
            'total_articles_scraped': total_articles,
            'unique_stories': unique_stories_count,
            'duplicates_removed': duplicates_removed,
            'consolidation_rate': duplicates_removed / total_articles if total_articles > 0 else 0,
            'consolidated_stories': consolidated_count,
            'source_distribution': dict(source_counts),
            'similarity_threshold': self.similarity_threshold
        }
        
        return stats
