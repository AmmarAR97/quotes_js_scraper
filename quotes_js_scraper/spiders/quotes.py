import scrapy
from quotes_js_scraper.items import QuoteItem
from scrapy_playwright.page import PageMethod


class QuotesSpider(scrapy.Spider):
    name = 'quotes'

    # def start_requests(self):
    #     """
    #     JavaScript with next page
    #     """
    #     # url = 'http://quotes.toscrape.com/js/'
    #     yield scrapy.Request(
    #         url,
    #         callback=self.parse,
    #         meta=dict(
    #             playwright=True,
    #             playwright_include_page=True,
    #             playwright_page_methods=[PageMethod('wait_for_selector', 'div.quote')],
    #             errback=self.errback_close_page,
    #         )
    #     )

    def start_requests(self):
        """
        Infinite scrolling
        """
        url = 'https://quotes.toscrape.com/scroll'
        QUOTES_PER_PAGE = 20

        playwright_page_methods = [
            PageMethod('wait_for_selector', 'div.quote'),
            PageMethod('evaluate', 'window.scrollBy(0, document.body.scrollHeight)'),
            PageMethod('wait_for_selector', f'div.quote:nth-child({QUOTES_PER_PAGE + 1})'),
        ]

        yield scrapy.Request(
            url=url,
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                playwright_page_methods=playwright_page_methods,
            ),
        )

    async def parse(self, response):
        page = response.meta['playwright_page']
        await page.close()

        for quote in response.css('.quote'):
            item = QuoteItem()
            item['quote'] = quote.css('span.text::text').get()
            item['author'] = quote.css('small.author::text').get()
            item['tags'] = quote.css('div.tags a.tag::text').getall()
            yield item

        # UNCOMMENT FOR NEXT PAGE
        # next_page = response.css('.pager .next>a::attr(href)').get()
        #
        # if next_page is not None:
        #     next_page_url = 'http://quotes.toscrape.com' + next_page
        #     yield scrapy.Request(next_page_url, meta=dict(
        #         playwright=True,
        #         playwright_include_page=True,
        #         playwright_page_methods=[
        #             PageMethod('wait_for_selector', 'div.quote'),
        #         ],
        #         errback=self.errback_close_page,
        #     ))

    async def errback_close_page(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

