#!/usr/bin/env python3
"""
Test newsletter generation with sample articles
"""

from deduplicator import StoryDeduplicator
from summarizer import ArticleSummarizer
from newsletter import NewsletterGenerator
from sendfox_client import SendFoxClient
from database import NewsletterDatabase
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample AI news articles
SAMPLE_ARTICLES = [
    {
        'title': 'OpenAI Releases GPT-5 with Major Performance Improvements',
        'url': 'https://example.com/gpt5-release',
        'full_content': '''OpenAI has announced the release of GPT-5, marking a significant advancement in large language models. The new model demonstrates substantial improvements in reasoning capabilities, multimodal understanding, and factual accuracy. According to OpenAI, GPT-5 achieves state-of-the-art performance on numerous benchmarks, including mathematical problem-solving, code generation, and complex reasoning tasks. The model features enhanced safety measures and reduced hallucinations compared to its predecessors. Industry experts predict this release will accelerate AI adoption across various sectors.''',
        'published_date': datetime.now().isoformat(),
        'source': 'TechCrunch AI'
    },
    {
        'title': 'MIT Researchers Develop Breakthrough AI Chip That Uses 90% Less Energy',
        'url': 'https://example.com/mit-ai-chip',
        'full_content': '''Researchers at MIT have developed a revolutionary AI chip that consumes 90% less energy than current GPU-based systems. The chip uses novel neuromorphic computing principles inspired by the human brain. This breakthrough could enable AI deployment in battery-powered devices and reduce the environmental impact of large-scale AI systems. The research team demonstrated the chip running complex neural networks at speeds comparable to traditional GPUs while drawing minimal power. This development addresses one of the major challenges in AI: energy consumption and sustainability.''',
        'published_date': datetime.now().isoformat(),
        'source': 'MIT News AI/ML'
    },
    {
        'title': 'Google Announces Gemini 2.0 with Enhanced Multimodal Capabilities',
        'url': 'https://example.com/gemini-2',
        'full_content': '''Google has unveiled Gemini 2.0, the next generation of its multimodal AI model. The new version excels at understanding and generating content across text, images, video, and audio simultaneously. Gemini 2.0 introduces advanced reasoning capabilities and can handle tasks requiring deep contextual understanding. The model is being integrated across Google's product ecosystem, including Search, Gmail, and Google Workspace. Developers can access Gemini 2.0 through Google Cloud's AI platform starting next month.''',
        'published_date': datetime.now().isoformat(),
        'source': 'The Verge AI'
    },
    {
        'title': 'AI-Powered Drug Discovery Platform Identifies Potential Cancer Treatment',
        'url': 'https://example.com/ai-drug-discovery',
        'full_content': '''A pharmaceutical company using AI-powered drug discovery has identified a promising compound for treating aggressive forms of cancer. The AI system analyzed millions of molecular structures and predicted their effectiveness against cancer cells. Early clinical trials show encouraging results with minimal side effects. This represents a significant milestone in using artificial intelligence to accelerate drug development, potentially reducing the typical 10-15 year timeline for bringing new drugs to market. The approach could revolutionize pharmaceutical research and development.''',
        'published_date': datetime.now().isoformat(),
        'source': 'ScienceDaily AI'
    },
    {
        'title': 'Major Tech Companies Form Alliance for Responsible AI Development',
        'url': 'https://example.com/ai-alliance',
        'full_content': '''Leading technology companies including Microsoft, Meta, and IBM have formed a new alliance focused on responsible AI development. The consortium aims to establish industry standards for AI safety, transparency, and ethical use. Key initiatives include developing frameworks for AI impact assessments, creating shared safety protocols, and promoting AI literacy. The alliance will also work with policymakers to inform AI regulation. This collaborative effort reflects growing recognition of the need for coordinated approaches to AI governance.''',
        'published_date': datetime.now().isoformat(),
        'source': 'Wired AI'
    },
    {
        'title': 'Anthropic Introduces Claude 3 with Advanced Reasoning Features',
        'url': 'https://example.com/claude-3',
        'full_content': '''Anthropic has launched Claude 3, featuring significantly improved reasoning and analysis capabilities. The model excels at complex problem-solving, including mathematical proofs, scientific analysis, and strategic planning. Claude 3 introduces a new Constitutional AI framework that ensures outputs align with human values and ethical principles. Performance benchmarks show Claude 3 outperforming competitors on tasks requiring nuanced understanding and careful reasoning. The model is available through Anthropic's API and select enterprise partnerships.''',
        'published_date': datetime.now().isoformat(),
        'source': 'AI News'
    },
    {
        'title': 'OpenAI Unveils GPT-5: Next Generation Language Model',
        'url': 'https://example.com/openai-gpt5',
        'full_content': '''OpenAI has officially released GPT-5, its most advanced language model to date. The release includes breakthrough improvements in reasoning, coding, and multimodal capabilities. GPT-5 demonstrates enhanced understanding of complex instructions and produces more accurate, contextually appropriate responses. The model incorporates advanced safety features and shows reduced bias in its outputs. Early adopters report significant productivity gains across various applications including software development, content creation, and data analysis.''',
        'published_date': datetime.now().isoformat(),
        'source': 'Forbes AI'
    },
    {
        'title': 'EU Passes Comprehensive AI Regulation Framework',
        'url': 'https://example.com/eu-ai-regulation',
        'full_content': '''The European Union has passed landmark AI regulation that will govern AI development and deployment across member states. The framework categorizes AI systems by risk level and imposes requirements based on potential harm. High-risk AI applications will face strict requirements including transparency obligations, human oversight, and regular audits. The regulation aims to balance innovation with protection of fundamental rights. Companies have a two-year transition period to comply with the new rules, which could influence global AI governance standards.''',
        'published_date': datetime.now().isoformat(),
        'source': 'MIT Technology Review'
    }
]

def main():
    logger.info("="*60)
    logger.info("TESTING NEWSLETTER GENERATION WITH SAMPLE ARTICLES")
    logger.info("="*60)
    
    # Initialize components
    deduplicator = StoryDeduplicator()
    summarizer = ArticleSummarizer()
    newsletter_gen = NewsletterGenerator()
    sendfox = SendFoxClient()
    db = NewsletterDatabase()
    
    try:
        # Step 1: Use sample articles
        logger.info(f"\nUsing {len(SAMPLE_ARTICLES)} sample AI news articles")
        articles = SAMPLE_ARTICLES
        
        # Step 2: Deduplicate stories
        logger.info("\n" + "="*60)
        logger.info("STEP 1: Deduplicating and consolidating stories...")
        logger.info("="*60)
        unique_stories = deduplicator.deduplicate_stories(articles)
        logger.info(f"✅ Consolidated to {len(unique_stories)} unique stories")
        
        stats = deduplicator.get_duplicate_statistics(articles, unique_stories)
        logger.info(f"   - Duplicates removed: {stats['duplicates_removed']}")
        logger.info(f"   - Consolidated stories: {stats['consolidated_stories']}")
        
        # Step 3: Summarize articles
        logger.info("\n" + "="*60)
        logger.info("STEP 2: Generating AI summaries with OpenAI...")
        logger.info("="*60)
        summaries = []
        for i, story in enumerate(unique_stories, 1):
            logger.info(f"Summarizing story {i}/{len(unique_stories)}: {story.get('title', 'Unknown')[:60]}...")
            summary = summarizer.summarize_story(story)
            summaries.append(summary)
        
        logger.info(f"✅ Generated {len(summaries)} summaries")
        
        summary_stats = summarizer.get_summary_statistics(summaries)
        logger.info(f"   - Successful summaries: {summary_stats['successful_summaries']}")
        logger.info(f"   - Average impact score: {summary_stats['average_impact_score']}/10")
        logger.info(f"   - High impact stories: {summary_stats['high_impact_stories']}")
        
        # Step 4: Generate newsletter
        logger.info("\n" + "="*60)
        logger.info("STEP 3: Generating newsletter HTML...")
        logger.info("="*60)
        newsletter_html = newsletter_gen.generate_newsletter(summaries)
        logger.info("✅ Newsletter HTML generated successfully")
        
        # Step 5: Save to database
        logger.info("\n" + "="*60)
        logger.info("STEP 4: Saving newsletter to database...")
        logger.info("="*60)
        newsletter_data = {
            'title': f"AI Daily Newsletter - {datetime.now().strftime('%B %d, %Y')}",
            'html_content': newsletter_html,
            'story_count': len(summaries),
            'created_at': datetime.now().isoformat(),
            'generation_method': 'manual'
        }
        newsletter_id = db.save_newsletter(newsletter_data)
        logger.info(f"✅ Newsletter saved with ID: {newsletter_id}")
        
        # Step 6: Send email (if configured)
        logger.info("\n" + "="*60)
        logger.info("STEP 5: Sending newsletter via SendFox...")
        logger.info("="*60)
        email_sent = sendfox.send_newsletter(newsletter_html, newsletter_data['title'])
        
        if email_sent:
            db.mark_newsletter_sent(newsletter_id)
            logger.info("✅ Newsletter sent successfully via email!")
        else:
            logger.warning("⚠️  Newsletter generated but email not sent (SendFox not configured)")
        
        # Final summary
        logger.info("\n" + "="*60)
        logger.info("NEWSLETTER GENERATION COMPLETE!")
        logger.info("="*60)
        logger.info(f"Title: {newsletter_data['title']}")
        logger.info(f"Unique Stories: {len(summaries)}")
        logger.info(f"Newsletter ID: {newsletter_id}")
        logger.info(f"Email Sent: {'Yes' if email_sent else 'No'}")
        logger.info("="*60)
        
        # Save outputs
        text_version = newsletter_gen.generate_text_version(summaries)
        with open('latest_newsletter.txt', 'w', encoding='utf-8') as f:
            f.write(text_version)
        logger.info("📄 Plain text saved to: latest_newsletter.txt")
        
        with open('latest_newsletter.html', 'w', encoding='utf-8') as f:
            f.write(newsletter_html)
        logger.info("📄 HTML saved to: latest_newsletter.html")
        
        logger.info("\n✅ You can now view the newsletter in the Streamlit app!")
        logger.info("   Go to 'Newsletter Archive' to see the generated newsletter")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
