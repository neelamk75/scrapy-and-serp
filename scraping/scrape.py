import scrapy
from bs4 import BeautifulSoup
import time
import io
from scraping.custom_search import GoogleSerperAPIWrapper
import hashlib


OUTPUT_FOLDER = "text_output"


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
        self.output_file = f"{OUTPUT_FOLDER}/{self.query_hash}.md" 


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



