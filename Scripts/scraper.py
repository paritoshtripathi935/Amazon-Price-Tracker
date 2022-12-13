# -*- coding: utf-8 -*-
"""
Module to get and parse the product info on Amazon Search
"""

import re
import time
import uuid
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import json
import os
from product import Product


base_url = "https://www.amazon.com"

class Scraper():

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'authority': 'www.amazon.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }
        self.product_obj_list = []
        self.page_list = []

    def prepare_url(self, search_word):
        #print("Preparing Url", urljoin(base_url, ("/s?k=%s" % (search_word.replace(' ', '+')))))
        return urljoin(base_url, ("/s?k=%s" % (search_word.replace(' ', '+'))))

    def get_request(self, url):
        try:
            response = self.session.get(url, headers=self.headers)
            if response.status_code != 200:
                raise requests.HTTPError(
                    "Error occured, status code:{response.status_code}")
        #  returns None if requests.exceptions.ConnectionError or requests.HTTPError occurs
        except (requests.exceptions.ConnectionError, requests.HTTPError) as e:
            return None
        if response.status_code == 200:
            print("GET request Successfully", url)
            return response
        else:
            print("GET request Failed", url)
            return None

    def check_page_validity(self, page_content):

        if "We're sorry. The Web address you entered is not a functioning page on our site." in page_content:
            valid_page = False
        elif "Try checking your spelling or use more general terms" in page_content:
            valid_page = False
        elif "Sorry, we just need to make sure you're not a robot." in page_content:
            valid_page = False
        elif "The request could not be satisfied" in page_content:
            valid_page = False
        else:
            #print("Valid page found")
            valid_page = True
        return valid_page

    def get_page_content(self, search_url):
        valid_page = True
        trial = 0
        # if a page does not get a valid response it retries(5 times)
        max_retries = 5
        while (trial < max_retries):

            response = self.get_request(search_url)

            if (not response):
                return None

            valid_page = self.check_page_validity(response.text)

            if valid_page:
                break

            print("No valid page was found, retrying in 3 seconds...")
            time.sleep(3)
            trial += 1

        if not valid_page:
            print(
                "Even after retrying, no valid page was found on this thread, terminating thread...")
            return None
        #print("Getting page content")
        return response.text

    def get_product_url(self, product):
        regexp = "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal".replace(' ', '\s+')
        classes = re.compile(regexp)
        
        product_url = product.find('a', attrs={'class': classes}).get('href')
        #print("Final URL", base_url + product_url)
        return base_url + product_url

    def get_product_asin(self, product):
        #print("Getting product ASIN")
        return product.get('data-asin')

    def get_product_title(self, product):
        regexp = "a-color-base a-text-normal".replace(' ', '\s+')
        classes = re.compile(regexp)
        try:
            title = product.find('span', attrs={'class': classes})
            #print("Getting product title", title.text.strip())
            return title.text.strip()

        except AttributeError:
            return ''

    def get_product_price(self, product):
        try:
            price = product.find('span', attrs={'class': 'a-offscreen'})
            #print("Getting product price", float(price.text.strip('$').replace(',', '')))
            return float(price.text.strip('$').replace(',', ''))

        except (AttributeError, ValueError):
            return None

    def get_product_image_url(self, product):
        image_tag = product.find('img')
        #print("Getting product image url", image_tag)
        return image_tag.get('src')

    def get_product_rating(self, product):
        try:
            rating = re.search(r'(\d.\d) out of 5', str(product))
            #print("Getting product rating", float(rating.group(1)))
            return float(rating.group(1))

        except (AttributeError, ValueError):
            return None

    def get_product_review_count(self, product):

        try:
            review_count = product.find(
                'span', attrs={'class': 'a-size-base', 'dir': 'auto'})
            #print("Getting product review count", int(review_count.text.strip().replace(',', '')))
            return int(review_count.text.strip().replace(',', ''))

        except (AttributeError, ValueError):
            return None

    def get_product_bestseller_status(self, product):
        try:
            bestseller_status = product.find(
                'span', attrs={'class': 'a-badge-text'})
            #print("Getting product bestseller status", bestseller_status.text.strip())
            return bestseller_status.text.strip() == 'Best Seller'

        except AttributeError:
            return False

    def get_product_prime_status(self, product):
        regexp = "a-icon a-icon-prime a-icon-medium".replace(' ', '\s+')
        classes = re.compile(regexp)
        prime_status = product.find('i', attrs={'class': classes})
        #print("Getting product prime status", prime_status)
        return bool(prime_status)

    def get_product_info(self, product):
        product_obj = Product()
        product_obj.url = self.get_product_url(product)
        product_obj.asin = self.get_product_asin(product)
        product_obj.title = self.get_product_title(product)
        product_obj.price = self.get_product_price(product)
        product_obj.img_url = self.get_product_image_url(product)
        product_obj.rating_stars = self.get_product_rating(product)
        product_obj.review_count = self.get_product_review_count(product)
        product_obj.bestseller = self.get_product_bestseller_status(product)
        product_obj.prime = self.get_product_prime_status(product)

        self.product_obj_list.append(product_obj)

    def get_page_count(self, page_content):

        soup = BeautifulSoup(page_content, 'html5lib')
        try:
            pagination = soup.find_all(
                'li', attrs={'class': ['a-normal', 'a-disabled', 'a-last']})
            return int(pagination[-2].text)
        except IndexError:
            return 1

    def prepare_page_list(self, search_url):
        for i in range(1, self.page_count + 1):
            self.page_list.append(search_url + '&page=' + str(i))

    def get_products(self, page_content):
        soup = BeautifulSoup(page_content, "html5lib")
        product_list = soup.find_all(
            'div', attrs={'data-component-type': 's-search-result'})

        for product in product_list:
            self.get_product_info(product)

    def get_products_wrapper(self, page_url):
        page_content = self.get_page_content(page_url)
        if (not page_content):
            return

        self.get_products(page_content)

    def generate_output_file(self, stamp_date,search_term):
        products_json_list = []
        # generate random file name
        filename = str(search_term) + '.json'
        # every object gets converted into json format
        for obj in self.product_obj_list:
            products_json_list.append(obj.to_json())

        products_json_list = ','.join(products_json_list)
        json_data = '[' + products_json_list + ']'
        # make Data/files/{filename} directory if it doesn't exist
        if not os.path.exists('Data/files/{}'.format(stamp_date)):
            os.makedirs('Data/files/{}'.format(stamp_date))

        with open('Data/files/{}/'.format(stamp_date) + filename, mode='w') as f:
            f.write(json_data)
        self.product_obj_list.clear()

    def search(self, search_word, stamp_date):
        search_url = self.prepare_url(search_word)
        page_content = self.get_page_content(search_url)
        if (not page_content):
            return

        self.page_count = self.get_page_count(page_content)
        if self.page_count <= 1:
            self.get_products(page_content)

        else:
            # if page count is more than 1, then we prepare a page list and start a thread at each page url
            self.prepare_page_list(search_url)
            # creating threads at each page in page_list
            with ThreadPoolExecutor() as executor:
                for page in self.page_list:
                    executor.submit(self.get_products_wrapper, page)

        # generate a json output file
        self.generate_output_file(stamp_date, search_word)
