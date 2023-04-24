from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
import time
import scrapy
from scrapy_splash import SplashRequest
import logging
from scrapy.utils.log import configure_logging

import os

from urllib.parse import urljoin
from urllib.parse import urlparse, parse_qs

# https://rw.kikuu.com/
# https://www.olado.rw/womens-fashion/
# https://www.dubuy.com/rw-en


def crawlerActions():
    # Disable logging
    logging.getLogger('scrapy').setLevel(logging.WARNING)

    # Configure logging
    configure_logging(install_root_handler=False)

    class KimironkoSpider(scrapy.Spider):
        name = "kimironko"
        allowed_domains = ['kimironkomarket.rw']
        start_urls = [
            'https://kimironkomarket.rw/product-category/groceries/spices-and-herbs/',
            "https://kimironkomarket.rw/product-category/groceries/starch/",
            "https://kimironkomarket.rw/product-category/groceries/meats-and-proteins/",
            "https://kimironkomarket.rw/product-category/groceries/canned-and-packed-foods/",
            "https://kimironkomarket.rw/product-category/groceries/fruits/",
            "https://kimironkomarket.rw/product-category/household/",
            "https://kimironkomarket.rw/product-category/household/kitchenary/",
            "https://kimironkomarket.rw/product-category/household/",
            "https://kimironkomarket.rw/product-category/made-in-rwanda/",
            "https://kimironkomarket.rw/product-category/cosmetics/",
            "https://kimironkomarket.rw/product-category/electronics/computer-accessories/",
            "https://kimironkomarket.rw/product-category/home-appliances/",
            "https://kimironkomarket.rw/product-category/sports-goods/clothing/",
            "https://kimironkomarket.rw/product-category/sports-goods/clothing/",
            "https://kimironkomarket.rw/product-category/sports-goods/fitness/",
            "https://kimironkomarket.rw/product-category/gifts/",
        ]

        script = """
            function scrollToBottom() {
                window.scrollTo(0, document.body.scrollHeight);
            }
            scrollToBottom();
            return 0;
        """

        # custom settings - save to csv: name, price, image
        custom_settings = {
            'FEED_FORMAT': 'csv',
            'FEED_URI': 'kimironko.csv',

        }

        def start_requests(self):
            for url in self.start_urls:
                yield SplashRequest(url, self.parse, endpoint='execute', args={
                    'lua_source': self.script,
                    'wait': 5
                })

        def parse(self, response):

            print("Starting crawl for page - kimironko ")
            print("total products seen: ", len(response.css('.product')))
            print()
            # getting all products
            for product in response.css('.product'):
                yield {
                    'name': product.css('h3.product-title a::text').get(),
                    'price': product.css('span.amount bdi::text').get(),
                    'image': product.css('div.thumbnail-wrapper a img::attr(src)').get(),
                    'link': product.css('div.thumbnail-wrapper a::attr(href)').get()
                }

                time.sleep(3)

    process = CrawlerProcess(settings=get_project_settings())
    print()
    print("Starting Kimironko crawl...")
    print()
    # process.crawl(KimironkoSpider)

    # process.start()

    print()
    print("Crawl Kimironko finished.")
    print("********************************************************")
    print()

    # check number of products

    class BeiMartSpider(scrapy.Spider):
        name = "beiMart"
        start_urls = [
            'https://beimart.com/product-category/all-products/',
        ]
        # custom settings - save to csv: name, price, image
        custom_settings = {
            'FEED_FORMAT': 'csv',
            'FEED_URI': 'beiMart.csv',
        }

        def parse(self, response):
            base_url = 'https://beimart.com/product-category/all-products'
            # string class woocommerce-result-count => string format:	Showing 1–24 of 502 results
            current_page = int(response.css('span.current::text').get())
            print()
            print("Starting crawl for page: ", current_page)
            print()
            # getting all products
            for product in response.css('.product'):
                yield {
                    'name': product.css('h2.woocommerce-loop-product__title::text').get(),
                    'price': product.css('span.amount bdi::text').get(),
                    'image': product.css('img.attachment-woocommerce_thumbnail::attr(src)').get(),
                    'link': product.css('a.woocommerce-LoopProduct-link::attr(href)').get(),
                }

            # getting next page - get a tag with text value of current_page + 1
            urls = response.css(
                'a.page-numbers ::attr(href)').getall()

            print("urls: ", urls)

            next_page = None

            # find element that contains ?page=current_page + 1

            for url in urls:
                looking_for = "/page/" + str(current_page + 1)
                if looking_for in url:
                    next_page = base_url + url
                    break

            # cancel on page 20
            if current_page == 21:
                next_page = None

            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    print("Starting beiMart crawl...")

    # process.crawl(BeiMartSpider)
    # process.start()

    # stop reactor

    print("Crawl beiMart finished.")
    print("********************************************************")

    # check number of products

    class OladoSpider(scrapy.Spider):
        name = "olado"
        start_urls = [
            "https://www.olado.rw/womens-fashion/"

        ]

        # custom settings - save to csv: name, price, image
        custom_settings = {
            'FEED_FORMAT': 'csv',
            'FEED_URI': 'olado.csv',

        }

        def parse(self, response):
            base_url = 'https://www.olado.rw/womens-fashion'
            # string format: Displaying 30 items in 184 items, page  1 out of   7 pages
            # get current page
            page_text = response.css(
                'a.gotoPage::text').get()
            current_page = page_text.split(" ")[-8]
            print(current_page)
            # remove ' at the end of the string
            total_pages = page_text.split(" ")[-3]
            print("Starting crawl for page ", current_page)
            print("total products seen: ", len(response.css('div.AllList')))
            print()
            # getting all products
            for product in response.css('div.AllList'):
                yield {
                    'name': product.css('span.prodname::text').get(),
                    # price format: RWF 1,000. Remove RWF and comma
                    'price': product.css('span.prodCurrency::text').get().replace("RWF", "").replace(",", ""),
                    'image': product.css('div.list-img img::attr(data-src)').get(),
                    'link': product.css('a.alink::attr(href)').get()
                }

                time.sleep(2)

            urls = response.css(
                'ul.paging li a::attr(href)').getall()

            print("urls: ", urls)

            next_page = None

            # find element that contains ?page=current_page + 1

            # check if current page has ' at the end and remove it
            if current_page[-1] == "'":
                current_page = current_page[:-1]

            for url in urls:
                looking_for = "/?page=" + str(int(current_page) + 1)
                if looking_for in url:
                    next_page = base_url + url
                    break

            if current_page == total_pages:
                next_page = None

            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    # process.crawl(OladoSpider)
    # process.start()

    print()

    print("Crawl Olado finished.")
    print("********************************************************")
    print()

    class KikuuSpider(scrapy.Spider):
        name = "kikuu"
        start_urls = [
            'https://rw.kikuu.com/search/result?belongCategory=845690&kw=Clothing',
            "https://rw.kikuu.com/search/result?belongCategory=444785&kw=Shoes",
            "https://rw.kikuu.com/search/result?belongCategory=277363&kw=Luggage%20&%20Bags",
            "https://rw.kikuu.com/search/result?belongCategory=806773&kw=Watch%20&%20Jewelry",
            "https://rw.kikuu.com/search/result?belongCategory=464250&kw=Kids%20&%20Toys",
            "https://rw.kikuu.com/search/result?belongCategory=929652&kw=Home%20&%20Appliances",
            "https://rw.kikuu.com/search/result?belongCategory=777586&kw=Beauty",
            "https://rw.kikuu.com/search/result?belongCategory=322948&kw=Weddings",
            "https://rw.kikuu.com/search/result?belongCategory=582026&kw=Hair",
            "https://rw.kikuu.com/search/result?belongCategory=348046&kw=Phones%20&%20Tel",
            "https://rw.kikuu.com/search/result?belongCategory=209288&kw=Electronics",
            "https://rw.kikuu.com/search/result?belongCategory=264590&kw=Computer%20&%20Office",
            "https://rw.kikuu.com/search/result?belongCategory=364590&kw=Automobile%20Accessory%20&%20Tools",
        ]
        # custom settings - save to csv: name, price, image
        custom_settings = {
            'FEED_FORMAT': 'csv',
            'FEED_URI': 'kikuu.csv',
        }

        def parse(self, response):
            base_url = response.url

            print("total products seen: ", len(
                response.css('li.searchGoods-item___3gN71')))
            print()
            # getting all products
            for product in response.css('li.searchGoods-item___3gN71'):
                yield {
                    'name': product.css('p.searchGoods-name___2Sm89::text').get(),
                    # price format: RWF 1,000. Remove RWF and comma
                    'price': product.css('p.searchGoods-price___2nc3K::text').get().replace("RWF", "").replace(",", ""),
                    'image': product.css('img.searchGoods-image-pic___2qjgd::attr(src)').get(),
                    'link': base_url + product.css('a.searchGoods-link___3-nXo::attr(href)').get()
                }

                time.sleep(2)

            next_page = None

            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    process.crawl(KikuuSpider)
    process.start()

    # with open('olado.csv', 'r') as f:
    #     print("Total olado products: " + str(len(f.readlines())))

    # with open('kimironko.csv', 'r') as f:
    #     print("Total Kimironko products: " + str(len(f.readlines())))

    # with open('beiMart.csv', 'r') as f:
    #     print("Total beiMart products: " + str(len(f.readlines())))


if __name__ == '__main__':
    crawlerActions()
