import scrapy
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from bs4 import BeautifulSoup
import time
import io
from custom_search import GoogleSerperAPIWrapper
import hashlib


google_serper = GoogleSerperAPIWrapper()


class MySpider(scrapy.Spider):
    name = 'my_spider'
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
    }

    def __init__(self, query, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.query = query
        self.start_time = time.time()
        self.query_hash = hashlib.sha256(query.encode()).hexdigest()
        self.output_file = f"{self.query_hash}.md" 


    def start_requests(self):
        results = google_serper.run(self.query)
        urls = [result['link'] for result in results if isinstance(result, dict) and 'link' in result]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        content = ''
        for heading in headings:
            heading_text = heading.get_text().strip()
            content += f"# {heading_text}\n\n" 
            # Find paragraphs associated with the current heading
            paragraphs = heading.find_all_next(['p'])
            for paragraph in paragraphs:
                paragraph_text = paragraph.get_text().strip()
                if paragraph_text:
                    content += f"{paragraph_text}\n\n" 
        self.save_to_file(response.url, content)


    def save_to_file(self, url, content):
        with io.open(self.output_file, 'w', encoding='utf-8') as file:
            file.write(content)


    def closed(self, reason):
        elapsed_time = time.time() - self.start_time
        print(f"Total time taken: {elapsed_time} seconds")


configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def run_spiders():
    queries = ["tax deduction 2024", "what is the difference between filing taxes late and not filing taxes at all?", \
               "What's the difference between a Form W-2 and a Form 1099-MISC or Form 1099-NEC?"]
    for query in queries:
        spider = MySpider(query)
        yield runner.crawl(MySpider, query=query)
    reactor.stop()


run_spiders()
reactor.run()
