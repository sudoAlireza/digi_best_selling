import scrapy


class BestSellingScraperSpider(scrapy.Spider):
    name = 'best_selling_scraper'
    start_urls = ['https://api.digikala.com/v1/search/?sort=7&page=1']


    def parse(self, response):
        result = response.json()
        pages_number = result.get('data').get('pager').get('total_pages')
        if pages_number:
            pages_number = int(pages_number)
        else:
            pages_number = 1

        pages_number = 10 if (pages_number > 10) else pages_number

        products = result.get('data').get('products')


        for product in products:
            dkp = product.get('id')
            product_page = f'https://api.digikala.com/v1/product/{dkp}/'
            yield scrapy.Request(product_page, callback=self.parse_product)


        for page in range(2, pages_number+1):
            pagination = f'&page={page}'
            url = response.url.split('&page=')[0]
            category_url = url + pagination + '&has_selling_stock=1'
            yield scrapy.Request(category_url, callback=self.parse)


    def parse_product(self, response):
        item = {}

        result = response.json()
        product = result.get('data').get('product')

        price = product.get('default_variant').get('price')
        item['first_price'] = price.get('rrp_price')
        item['last_price'] = price.get('selling_price')

        breadcrumb = product.get('breadcrumb')
        navbar = list()
        for n in breadcrumb[:-1]:
            navbar.append(n.get('title'))
        
        item['sub_cat'] = navbar[-1]
        item['main_cat'] = navbar[1]

        item['rate'] = product.get('rating').get('rate')
        item['rate_count'] = product.get('rating').get('count')
        item['rate_count'] = product.get('comments_count')

        yield item
