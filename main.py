from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scraping.scrape import MySpider 
# from update_vector.raptor import RaptorPack


# raptor_pack = RaptorPack()


@defer.inlineCallbacks
def run_spiders():
    # Add queries here
    queries = ["tax deduction 2024", "what is the difference between filing taxes late and not filing taxes at all?",
               "What's the difference between a Form W-2 and a Form 1099-MISC or Form 1099-NEC?"]

    for query in queries:
        spider = MySpider(query)
        yield runner.crawl(MySpider, query=query)
    reactor.stop()


# def add_vector_db ():
#     raptor_pack.run()


configure_logging()
runner = CrawlerRunner()


if __name__ == '__main__':
    run_spiders()
    reactor.run()
    # add_vector_db()
