# -*- coding: utf-8 -*-
import scrapy
import re
import json
#import urlparse
from anansi.canonicalize import canonicalize
from datetime import datetime
from scrapy.contrib.spiders import CrawlSpider

TODAY = datetime.today()

class XYZSpider(CrawlSpider):
    name = "xyz"

    #def start_requests(self):
    start_urls = ['https://www.xyz.com/']
    allowed_domains = [xyz.com']
    handle_httpstatus_list = [404, 301, 302]
    
    def parse(self, response):
        crawledLinks = []
        #pattern = re.compile("^https:\/\/([a-zA-Z0-9]*\.)*xyz\.com.*\?globe")
        title = None
        meta_description = None
        h1 = None
        isNoindex = None
        isRedirect = False
        outlinks = None
        outlinkCount = None
        redirect_target = None
        links = []
        is_yield = False

        if response.status == 301 or response.status == 302:
            isRedirect = True
            noIndex = response.xpath('//meta[@name="robots"]/@content').extract()
            if "NOINDEX" in str(noIndex) or "noindex" in str(noIndex) or "Noindex" in str(noIndex):
               isNoindex = True
            else:
               isNoindex = False
            if response.headers['Location'] is not None:          
                redirect_target = response.headers['Location'].decode("utf-8")
                if canonicalize(redirect_target) != canonicalize(response.url):
                   links.append(redirect_target)
                   is_yield = True

              
        elif response.status == 200: 
            noIndex = response.xpath('//meta[@name="robots"]/@content').extract()
            if "NOINDEX" in str(noIndex) or "noindex" in str(noIndex) or "Noindex" in str(noIndex):
               isNoindex = True
            else:
               isNoindex = False
           
            links = response.xpath('//a/@href').extract()
            title = response.xpath('//title/text()').extract_first()
            meta_description = response.xpath('//meta[@name=\'description\']/@content').extract()[0].lstrip('{"').rstrip('}"')
            #h1 = response.xpath("//h1/text()").extract()
            h1 = [item.replace('\n', '').rstrip('"}').lstrip('{"').
                  strip(' ').strip('\t') for item in response.xpath("//h1/text()").extract()]
            outlinks = links
            outlinkCount = len(links)
            is_yield = True

        elif response.status == 404:
            is_yield = True

        # Generate values for response parameters
        if is_yield:
            yield {
             'url_raw':response.url,
             'url_canonical':canonicalize(response.url),
             'httpcode':response.status,
             'title':title,
             'meta-description': meta_description,
             'h1':h1,
             'isNoindex':isNoindex,
             'isRedirect':isRedirect,
             'outlinks': outlinks,
             'outlinkCount': outlinkCount,
             'redirect_target': redirect_target
            }

        for link in links:
             if not pattern.match(link) and not link in crawledLinks:
                link = response.urljoin(link)
                crawledLinks.append(link)
                request = scrapy.Request(link, meta = {
                      'handle_httpstatus_list': [302, 301, 404]
                  },
                  callback=self.parse, follow=True)
                yield request

