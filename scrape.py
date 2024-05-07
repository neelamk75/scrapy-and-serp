import scrapy
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from custom_search import GoogleSerperAPIWrapper
import time


google_serper = GoogleSerperAPIWrapper()


class MySpider(scrapy.Spider):
    name = 'my_spider'
    # Comment out / modify the custom_settings to apply a delay accordingly
    custom_settings = {
    'DOWNLOAD_DELAY': 2,  
}
    
    def __init__(self, query, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.query = query
        self.start_time = time.time()

    def start_requests(self):
        results = google_serper.run(self.query)
        urls = [result['link'] for result in results if isinstance(result, dict) and 'link' in result]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Extract paragraphs only
        paragraph = response.css('p::text').getall()
        yield {'paragraph': paragraph}

    def closed(self, reason):
        elapsed_time = time.time() - self.start_time
        print(f"Total time taken: {elapsed_time} seconds")

configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def run_spiders():

    '''Provide a query
    Here, 100 requests of a query sent '''
    queries = ["what is tax"] * 100
    for query in queries:
        spider = MySpider(query)
        yield runner.crawl(MySpider, query=query)
    reactor.stop()


run_spiders()
reactor.run()
