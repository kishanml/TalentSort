import asyncio
import time
import re

from crawl4ai import CrawlerRunConfig, AsyncWebCrawler
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.filters import (
    FilterChain,
    URLPatternFilter,
    DomainFilter,
    ContentTypeFilter,
)
from crawl4ai.deep_crawling.scorers import (
    KeywordRelevanceScorer
)


def sanitize_filename(url):
    return re.sub(r'[\\/*?:"<>|]', "_", url.replace("https://", "").replace("http://", "")) + ".md"


async def web_crawler(base_url, allowed_domains, url_patterns, keywords, keyword_wts=0.25):
    # Create a sophisticated filter chain
    filter_chain = FilterChain(
        [
            DomainFilter(
                allowed_domains=allowed_domains
            ),
            URLPatternFilter(patterns=url_patterns),
            ContentTypeFilter(allowed_types=["text/html"]),
        ]
    )

    # Create a composite scorer that combines multiple scoring strategies
    keyword_scorer = KeywordRelevanceScorer(
        keywords=keywords, weight=keyword_wts
    )
    
    # Markdown generator
    cleaned_md_generator = DefaultMarkdownGenerator(
        content_source="cleaned_html",  
        options={
            "ignore_links": True,
            "ignore_images": True
        }
    )
    
    # Set up the configuration
    config = CrawlerRunConfig(
        deep_crawl_strategy=BestFirstCrawlingStrategy(
            max_depth=2,
            include_external=False,
            filter_chain=filter_chain,
            url_scorer=keyword_scorer,
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        stream=True,
        verbose=True,
        markdown_generator=cleaned_md_generator
    )

    # Execute the crawl
    results = []
    start_time = time.perf_counter()

    async with AsyncWebCrawler() as crawler:
        async for result in await crawler.arun(
            url=base_url, config=config
        ):
            results.append(result)
            score = result.metadata.get("score", 0)
            depth = result.metadata.get("depth", 0)
            print(f"→ Depth: {depth} | Score: {score:.2f} | {result.url}")
            
            filename = sanitize_filename(result.url)
            with open(filename, "a+", encoding="utf-8") as file:
                file.write(str(result.markdown))

    duration = time.perf_counter() - start_time

    # Summarize the results
    print(f"\n✅ Crawled {len(results)} high-value pages in {duration:.2f} seconds")
    print(
        f"✅ Average score: {sum(r.metadata.get('score', 0) for r in results) / len(results):.2f}"
    )

    # Group by depth
    depth_counts = {}
    for result in results:
        depth = result.metadata.get("depth", 0)
        depth_counts[depth] = depth_counts.get(depth, 0) + 1

    print("\n📊 Pages crawled by depth:")
    for depth, count in sorted(depth_counts.items()):
        print(f"  Depth {depth}: {count} pages")
        
        
if __name__ == "__main__":
    asyncio.run(web_crawler(
        base_url="https://quantumitinnovation.com",
        allowed_domains=["quantumitinnovation.com"],
        url_patterns=["*home*", "*about*", "*contact*", "*company*", "*service*"],
        keywords=[
            "web-development", "web-development", "digital-marketing", "artificial-intelligence",
            "php", "android app", "ios app", "swift", "cross platform", "ipad app", "game", "mobile app", "ror", "node.js", "react", "joomla", "ui", "ux", "seo", "social media", "marketing", "iot", "robotic"
        ]
    ))