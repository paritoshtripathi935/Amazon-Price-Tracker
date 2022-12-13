import requests
from bs4 import BeautifulSoup
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from user_agent import get_ua
from requests import get
import pandas as pd
import datetime

request = requests.Session()
retry = Retry(connect=5, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
request.mount('http://', adapter)
request.mount('https://', adapter)


# create a class scraper
class Scraper:
    def __init__(self):
        self.rival_name = "Amazon"
        self.product_url = "https://www.amazon.in/dp/"
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}
        self.site = "https://www.amazon.in"
        self.stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def search_products(self, product):
        search_url = self.site + "/s?k=" + product
        response = request.get(search_url, headers=self.headers)

        if response.status_code == 200:
            search_page = BeautifulSoup(response.text, "html.parser")
            print("Getting search page of product", product)
            return search_page
        else:
            print("Error in getting search page of product", product)
            
    
    def get_product_details(self, product):
        search_page = self.search_products(product)
        search_class = search_page.find("div", {"class": "s-main-slot s-result-list s-search-results sg-row"})

        if search_class is not None:
            # product id
            # <span data-component-type="s-status-badge-component" class="rush-component" data-component-props="{&quot;badgeType&quot;:&quot;best-seller&quot;,&quot;asin&quot;:&quot;B094CBQ32N&quot;}" data-component-id="6"><div class="a-row a-badge-region"><span id="B094CBQ32N-best-seller" class="a-badge" aria-labelledby="B094CBQ32N-best-seller-label B094CBQ32N-best-seller-supplementary" data-a-badge-supplementary-position="right" tabindex="0" data-a-badge-type="status"><span id="B094CBQ32N-best-seller-label" class="a-badge-label" data-a-badge-color="sx-orange" aria-hidden="true"><span class="a-badge-label-inner a-text-ellipsis"><span class="a-badge-text" data-a-badge-color="sx-cloud">Best seller</span></span></span><span id="B094CBQ32N-best-seller-supplementary" class="a-badge-supplementary-text a-text-ellipsis" aria-hidden="true">in Amazon Renewed</span></span></div></span>

            # image links
            image_class = search_class.find_all("div", {"class": "sg-col sg-col-4-of-12 sg-col-4-of-16 sg-col-4-of-20 s-list-col-left"})
            product_id = image_class[3].find("span", {"data-component-props": True})
            print("Getting product id of product", product_id)
            
            image_list = [i.find("img").get("src") for i in image_class]
            image_list = list(set(image_list))
            print("Getting image links of product")

            product_info = []
            card_class = search_class.find_all("div", {"class": "sg-col-inner"})
            for productInfo in card_class:
                try:
                    product_class = productInfo.find("a", {"class": "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"})
                    product_link = product_class['href']
                    product_name = product_class.text.strip()
                    product_price = productInfo.find("span", {"class": "a-price-whole"}).text.strip()
                    product_rating = productInfo.find("span", {"class": "a-icon-alt"}).text.strip()
                    product_rating = product_rating.split(" ")[0]
                    product_rating = float(product_rating)
                    product_info.append([product_name, product_price, product_link, product_rating])
                except Exception as e:
                    pass

            # map all the data
            data = {
                "product_name": "name",
                "product_price": "price",
                "product_link": "link",
                "product_rating": "rating",
                "product_id": "id",
                "image_link": "image"
            }

            for product_name, product_price, product_link, product_rating in product_info:
                data["product_name"] = product_name
                data["product_price"] = product_price
                data["product_link"] = product_link
                data["product_rating"] = product_rating
                data["product_id"] = None
                data["image_link"] = None
                # save the data in json file
                with open("data.json", "a") as f:
                    json.dump(data, f)
                    f.write("\n")


if __name__ == "__main__":
    scraper = Scraper()
    scraper.get_product_details("iphone")