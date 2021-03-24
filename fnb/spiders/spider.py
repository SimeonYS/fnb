import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FnbItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class FnbSpider(scrapy.Spider):
	name = 'fnb'
	start_urls = ['https://www.fnbalaska.com/about-us/about-first-national/press-releases?ccm_paging_p_b13456=1&ccm_order_by_b13456=cv.cvDatePublic&ccm_order_by_direction_b13456=desc']

	def parse(self, response):
		post_links = response.xpath('//td/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//li[@class="next"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//p[@class="date"]/text()').get()
		title = response.xpath('(//h2)[1]/text()').get()
		content = response.xpath('//div[@class="content-well"]//text()[not (ancestor::h2 or ancestor::p[@class="date"] or ancestor::h1)]').getall()
		content = [p.strip() for p in content if p.strip()][:-1]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=FnbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
