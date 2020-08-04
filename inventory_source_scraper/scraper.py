import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from pyvirtualdisplay import Display
from bs4 import BeautifulSoup
from celery import Task
from .util import save_data


class Scraper(Task):
    """Product Scraper class
    """
    name = 'Scraper'
    url_login = 'https://app.inventorysource.com/#/login'
    url_products = 'https://app.inventorysource.com/#/products/'
    url_amazon = 'https://www.amazon.com/'
    login_email = 'rmaluski@comcast.net'
    login_password = 'Upwork1'

    def __init__(self):
        self.pool = ThreadPoolExecutor(max_workers=8)
        display = Display(visible=0, size=(1024, 768))
        display.start()
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-extensions')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Chrome(chrome_options=options)
        # self.driver = webdriver.Chrome()
        self.driver.wait = WebDriverWait(self.driver, 5)

    def run(self):
        self.update_state(state='PROGRESS', meta={
            'current': 0,
            'total': 200000  # temporary total count
        })

        page_count = self.get_page_count()
        print('pagecount', page_count)
        page_count = 16

        futures = {self.pool.submit(self.scrape, i): i for i in range(page_count)}

        for future in as_completed(futures):
            i = futures[future]
            print('as_completed', i)
            products = future.result()
            save_data(products)
            self.update_state(state='PROGRESS', meta={
                'current': i,
                'total': page_count
            })

        return {
            'current': page_count,
            'total': page_count,
            'status': 'Task Completed'
        }

    def scrape(self, page_index):
        items = self.get_inventory_products(page_index, None)
        data_to_save = []

        for item in items:
            if 'upc' not in item:
                continue

            products = self.get_inventory_products(0, item['upc'])
            upc = item['upc']
            product_amazon = self.get_amazon_product(upc)

            for product_inventory in products:
                vendor_id = product_inventory['dropshipper_id']

                if vendor_id == 308:
                    vendor = 'US Direct (All Niches)'
                elif vendor_id == 274:
                    vendor = 'Doba'
                else:
                    continue

                name = product_inventory['title']
                company = product_inventory['manufacturer'] if 'manufacturer' in product_inventory else ''
                price_inventory = product_inventory['wholesale_price']
                price_msrp = product_inventory['msrp']
                price_amazon = product_amazon['price']
                shipping_amazon = product_amazon['shipping']
                product = {
                    'name': name,
                    'upc': upc,
                    'vendor': vendor,
                    'company': company,
                    'price_inventory': price_inventory,
                    'price_amazon': price_amazon,
                    'price_msrp': price_msrp,
                    'shipping_amazon': shipping_amazon
                }
                data_to_save.append(product)

        return data_to_save

    def login(self):
        try:
            self.driver.get(self.url_login)
            input_email = self.driver.find_element_by_name('email')
            input_password = self.driver.find_element_by_name('password')
            btn_login = self.driver.find_element_by_css_selector('button[type="submit"]')
            input_email.send_keys(self.login_email)
            input_password.send_keys(self.login_password)
            btn_login.click()
        except:
            print('already logged in')

    def apply_filter(self):
        """apply a filter
        """
        script = '$(".sidebar-col .options div:nth-child(1) .dropdown-menu div:nth-child(66)").click();' \
                 '$(".sidebar-col .options div:nth-child(1) .dropdown-menu div:nth-child(222)").click();' \
                 '$(".sidebar-col .options div:nth-child(3) .dropdown-menu div:nth-child(6)").click();' \
                 '$(".sidebar-col .options div:nth-child(4) .dropdown-menu div:nth-child(3)").click();' \
                 '$(".sidebar-col .options div:nth-child(9) .dropdown-menu div:nth-child(3)").click();'
        self.driver.get(self.url_products)
        time.sleep(10)
        self.driver.execute_script(script)
        el_wholesale_start = self.driver.find_element_by_css_selector('.sidebar-col .options div:nth-child(5) div div '
                                                                 'div:nth-child(1) div input')
        el_wholesale_close = self.driver.find_element_by_css_selector('.sidebar-col .options div:nth-child(5) div div '
                                                                 'div:nth-child(3) div input')
        el_msrp_start = self.driver.find_element_by_css_selector('.sidebar-col .options div:nth-child(6) div div '
                                                            'div:nth-child(1) div input')
        el_msrp_close = self.driver.find_element_by_css_selector('.sidebar-col .options div:nth-child(6) div div '
                                                            'div:nth-child(3) div input')
        el_btn_apply = self.driver.find_element_by_css_selector('.sidebar-col .text-right div.btn.btn-lg.btn-primary')
        el_wholesale_start.send_keys('1')
        el_wholesale_close.send_keys('125')
        el_msrp_start.send_keys('25')
        el_msrp_close.send_keys('250')
        el_btn_apply.click()
        time.sleep(10)

    def get_inventory_products(self, index, upc):
        url = 'https://app.inventorysource.com/api/solr/'

        if upc:
            fq = f'upc:"{upc}"'
        else:
            fq = '((product_status_id:1 AND is_restricted:false AND dropshipper_id:(274 308)) OR (is_restricted:true ' \
                 'AND dropshipper_id:(274 308))) AND dropshipper_id:(292 505 274 565 364 234 389 516 147 492 259 37 ' \
                 '188 540 548 50 495 14 341 74 83 222 533 593 299 96 531 535 530 594 513 346 19 90 411 314 542 210 7 ' \
                 '547 398 308 499 294 410 58 563 32 29 524 544 213 496 406 579 12 555 128 117 243 417 537 379 263 136 ' \
                 '265 418 229 285 13 122 5 101 362 525 372 582 168 587 508 569 381 347 194 212 217 173 523 158 282 ' \
                 '272 361 199 250 377 240 512 541 305 242 358 514 534 550 4 183 572 517 515 303 21 92 571 558 567 135 ' \
                 '584 506 562 416 88 509 591 156 507 588 556 518 78 198 164 257 559 399 339 502 116 568 267 503 578 ' \
                 '142 570 155 145 553 165 202 201 378 504 30 304 359 383 80 76 180 241 79 403 432 196 153 270 311 150 ' \
                 '327 586 249 536 323 203 532 566 511 208 353 560 335 374 233 561 278 216 112 244 375 329 554) AND ' \
                 'has_valid_image:true AND wholesale_price:[1 TO 125] AND msrp:[25 TO 250] AND upc:[* TO *] '

        params = {
            'fl': 'id,dropshipper_id,product_status_id,deactivate_date,has_valid_image,thumbnail,image,title,cat1,'
                  'cat2,sku,parent_sku,manufacturer,manufacturer_id,upc,weight,quantity,description,'
                  'description_short,wholesale_price,map_price,msrp,is_restricted,insert_date,is_amazon_filter,'
                  'images,product_variant_parent_id,variants,dimensional_weight,shipping_cost,attributes,length,'
                  'width,height,warehouses',
            'fq': fq,
            'q': '*:*',
            'start': index * 50,
            'rows': 50,
            'sort': '',
            'wt': 'json'
        }
        script = f'''const url = "{url}"; const params = {params};''' + '''
                    function getResult(url, params) {
                        return new Promise(resolve => {
                            $.ajax({
                                url: url,
                                type: "POST",
                                data: JSON.stringify({params: params}),
                                headers: {
                                    'Accept': 'application/json',
                                    'Content-Type': 'application/json'
                                },
                                success: function(response) {
                                    if (response.response) {
                                        resolve(response.response.docs);
                                    } else {
                                        resolve([]);
                                    }
                                },
                                error: function(xhr) {
                                    resolve([]);
                                }
                            });
                        });
                    }
                    const result = await getResult(url, params);
                    return result;
                    '''
        result = self.driver.execute_script(script)
        return result

    def get_amazon_product(self, upc):
        url = f'https://www.amazon.com/s?k={upc}&ref=nb_sb_noss'
        headers = {
            'authority': 'www.amazon.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/51.0.2704.64 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }
        request = requests.get(url, headers=headers)
        content = BeautifulSoup(request.text, 'html.parser')
        price_whole = content.select('div[data-component-type=s-search-result] span['
                                     'cel_widget_id=MAIN-SEARCH_RESULTS] .a-price-whole')
        price_fraction = content.select('div[data-component-type=s-search-result] span['
                                        'cel_widget_id=MAIN-SEARCH_RESULTS] .a-price-fraction')
        count_price_whole = len(price_whole)

        if count_price_whole > 0:
            price = price_whole[0].text + price_fraction[0].text
        else:
            price = ''

        product = {
            'price': price,
            'shipping': 'No'
        }

        return product

    def get_page_count(self):
        """get number of pages
        """
        self.login()
        self.apply_filter()
        time.sleep(10)

        el_div = self.driver.find_element_by_css_selector('div[popover-is-open="search.go_to_page.is_open"] div')
        content = el_div.text

        return int(content[10:])
