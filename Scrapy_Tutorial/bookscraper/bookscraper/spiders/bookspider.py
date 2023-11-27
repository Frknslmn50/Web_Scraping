import scrapy
from bookscraper.items import BookItem
import random

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    # custom_settings = {
    #     "FEEDS": {
    #         "books.json": {
    #             "format": "json",
    #             "overwrite": True
    #        }
    #     }
    # }

    user_agent_list = [
        # Desktop User Agents
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.48 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
        
        # Mobile User Agents
        "Mozilla/5.0 (Linux; Android 11; SM-G965U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36"
    ]

    def parse(self, response):
        books = response.css("article.product_pod")

        for book in books:
            # get the relative url of the book
            relative_url = book.css('h3 a::attr(href)').get()

            book_url = response.urljoin(relative_url)
            # follow the book page and parse book data
            yield response.follow(book_url, callback=self.parse_book_page)
        
        # follow the next page and call parse again
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield response.follow(next_page_url, callback=self.parse)
    
    def parse_book_page(self, response):
        table_rows = response.css('table tr')
        book_item = BookItem()

        
        book_item["url"] =  response.url
        book_item['title'] = response.css('div.content h1::text').get()
        book_item['price_excl_tax'] = table_rows[2].css("td::text").get()
        book_item['price_incl_tax'] = table_rows[3].css("td::text").get()
        book_item['tax'] = table_rows[4].css("td::text").get()
        book_item['availability'] = table_rows[5].css("td::text").get()
        book_item['number_of_reviews'] = table_rows[6].css("td::text").get()
        book_item['star_rating'] = response.css('p.star-rating::attr(class)').get().split()[-1]
        book_item['category'] = response.css('div.page_inner ul.breadcrumb li:nth-child(3) a::text').get()
        book_item['description'] = response.css('div.content div#product_description + p::text').get()
        

        yield book_item

