# filename: src/crawler/crawler/spiders/site_spider.py
import scrapy
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
import tldextract
import json

class SiteSpider(scrapy.Spider):
    name = 'site_spider'
    
    def __init__(self, start_url='', max_pages=30, *args, **kwargs):
        super(SiteSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.max_pages = int(max_pages)
        self.page_count = 0
        
        # Extract the domain to stay within the same site
        self.allowed_domains = [tldextract.extract(start_url).registered_domain]
        self.link_extractor = LinkExtractor()
        self.crawled_data = {}

    def parse(self, response):
        # Limit the number of pages to crawl
        if self.page_count >= self.max_pages:
            self.crawler.engine.close_spider(self, 'page_limit_reached')
            return

        self.page_count += 1
        
        # Use BeautifulSoup to extract clean text
        soup = BeautifulSoup(response.body, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(['script', 'style', 'nav', 'footer', 'header']):
            script_or_style.decompose()

        text = soup.get_text(separator=' ', strip=True)
        
        # Store the cleaned text with its URL
        self.crawled_data[response.url] = text
        
        # Follow links on the page
        links = self.link_extractor.extract_links(response)
        for link in links:
            yield scrapy.Request(link.url, callback=self.parse)

    def closed(self, reason):
        # When the spider finishes, save the data to a file
        with open('data/url_to_doc.json', 'w', encoding='utf-8') as f:
            json.dump(self.crawled_data, f, ensure_ascii=False, indent=4)
        self.logger.info(f"Spider closed: {reason}. Crawled {len(self.crawled_data)} pages.")