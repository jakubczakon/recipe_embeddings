# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'../')

import json
    
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from cozinhabrasileira.items import CozinhabrasileiraItem

#class MySpider(Spider):
#    name = "recetas"
#    allowed_domains = ["cozinhabrasileira.com"]
#    start_urls = ["http://www.cozinhabrasileira.com/acompanhamentos/abobora_cabotia_com_linguica"]
#
#    def parse(self, response):
#        hxs = Selector(response)
#        full_recipe = hxs.xpath("//p[@class='recipe']")
#
#        ingredients = full_recipe.xpath("//span[@itemprop = 'ingredients']/text()")
#        ingr_list = []
#        for ingredient in ingredients:        
#            ingr_list.append(ingredient.extract())
#        items = {"ingredients":ingr_list,
#                 "recipe":full_recipe.xpath("//span[@itemprop = 'recipeInstructions']/text()").extract(),
#                 "title":hxs.xpath("//header/h1[@itemprop = 'name headline']/text()").extract()
#                }
#        return items
        
class MySpider(CrawlSpider):
    name = "recetas"
    allowed_domains = ["cozinhabrasileira.com"]
    start_urls = ["http://www.cozinhabrasileira.com"]


    rules = (
        Rule(SgmlLinkExtractor(allow=(), 
                               restrict_xpaths=('//article[@class="col-xs-6 col-sm-3 sidebar-offcanvas"]',)
                               ), 
             callback="parse_items", 
             follow= True),
        Rule(SgmlLinkExtractor(allow=(), 
                               restrict_xpaths=('//article[@class="col-lg-4 lista"]',)
                               ), 
             callback="parse_items", 
             follow= True),
    )

    def parse_items(self, response):
        hxs = Selector(response)
        full_recipe = hxs.xpath("//p[@class='recipe']")

#        ingredients = full_recipe.xpath("//span[@itemprop = 'ingredients']/text()")        
#        ingr_list = []
#        item = CozinhabrasileiraItem()
#        for ingredient in ingredients:        
#            ingr_list.append(ingredient.extract())
            
        ingredients = full_recipe.xpath("//span[@itemprop = 'ingredients']/text()")
        ingr_list = []
        for ingredient in ingredients:        
            ingr_list.append(ingredient.extract())
        items = {"ingredients":ingr_list,
                 "recipe":full_recipe.xpath("//span[@itemprop = 'recipeInstructions']/text()").extract(),
                 "title":hxs.xpath("//header/h1[@itemprop = 'name headline']/text()").extract()
                }
        return items
#        item["ingredients"] = ingr_list
#        item["recipe"] = full_recipe.xpath("//span[@itemprop = 'recipeInstructions']/text()").extract()
#        item["title"] = hxs.xpath("//header/h1[@itemprop = 'name headline']/text()").extract()
#        items = []
#        items.append(item)
#        return(items)
       