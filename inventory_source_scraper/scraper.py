import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
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
        self.driver = webdriver.Chrome()
        self.driver.wait = WebDriverWait(self.driver, 5)

    def run(self):
        self.login()
        self.apply_filter()

        page_count = self.get_page_count()
        page_count = 1
        for i in range(page_count):
            items = self.get_inventory_products(i, None)
            for item in items:
                if 'upc' not in item:
                    continue

                products = self.get_inventory_products(0, item['upc'])
                upc = item['upc']
                product_amazon = self.get_amazon_product(upc)

                for product_inventory in products:
                    name = product_inventory['title']
                    company = product_inventory['manufacturer'] if 'manufacturer' in product_inventory else ''
                    price_inventory = product_inventory['wholesale_price']
                    price_amazon = product_amazon['price']
                    shipping_amazon = product_amazon['shipping']
                    save_data(name, upc, company, price_inventory, price_amazon, shipping_amazon)
                print(upc, product_amazon['price'])
            self.update_state(state='PROGRESS', meta={
                'current': i,
                'total': page_count
            })
        return {
            'current': 4,
            'total': 4,
            'status': 'Task Completed'
        }

    def login(self):
        self.driver.get(self.url_login)
        input_email = self.driver.find_element_by_name('email')
        input_password = self.driver.find_element_by_name('password')
        btn_login = self.driver.find_element_by_css_selector('button[type="submit"]')
        input_email.send_keys(self.login_email)
        input_password.send_keys(self.login_password)
        btn_login.click()

    def apply_filter(self):
        """apply a location filter as USA
        """
        script = '$(".sidebar-col .options div:nth-child(3) .dropdown-menu div:nth-child(6)").click();' \
                 '$(".sidebar-col .text-right div.btn.btn-lg.btn-primary").click();'
        self.driver.get(self.url_products)
        time.sleep(20)
        self.driver.execute_script(script)
        time.sleep(10)

    def get_inventory_products(self, index, upc):
        url = 'https://app.inventorysource.com/api/solr/'

        if upc:
            fq = f'upc:"{upc}"'
        else:
            fq = '-dropshipper_id:(384 592 192 276 266 207 321 363 232 369 132 577 334 445 262 413 0 295 146 235 231 ' \
                 '302 144 380 151 371 527 288 286 287 489 494 256 248 281 336 447 448 483 460 310 442 463 435 444 ' \
                 '528 86 457 318 320 446 143 407 97 345 330 392 461 441 297 469 431 551 34 236 268 159 474 486 152 ' \
                 '449 352 552 113 424 574 459 237 338 31 405 500 436 396 187 264 395 576 466 350 458 214 365 354 284 ' \
                 '27 171 367 468 24 583 177 419 301 119 580 439 134 39 349 342 313 51 498 585 73 275 130 490 412 84 ' \
                 '104 221 590 247 167 581 420 200 589 283 197 546 67 46 163 325 62 139 110 172 277 273 102 205 215 ' \
                 '332 549 181 38 129 454 452 427 316 422 426 485 402 482 501 440 434 456 450 430 465 414 190 195 545 ' \
                 '394 306 290 400 491 493 279 404 193 510 475 521 488 343 370 291 484 189 425 476 220 376 487 344 ' \
                 '118 519 438 557 497 252 451 433 529 575 520 382 401 423 108 409 473 186 522 415 478 480 443 319 ' \
                 '421 408 228 360 357 317 269 309 429 467 326 453 428 539 464 470 472 368 254 322 315 331 385 300 ' \
                 '538 230 393 91 169 185 255 261 28 227 77 296 211 271 260 340 337 253 293 289 140 179 141 564 258 ' \
                 '245 397 225 251 366 218 204 410 347 96 523 517 294 308 416 558 162 377 213 180 311 88 257 565 379 ' \
                 '524 145 586 511 496 216 244) AND ((product_status_id:1 AND is_restricted:false) OR (' \
                 'is_restricted:true AND dropshipper_id:(50 314 411 304 299 274 13 495 263 517 388 82 298 390 312 ' \
                 '391 308 194 386 136 183 142 303 292 257 432 399 150 229 5 265 364 362 188 339 387 203 324 246 356 ' \
                 '233 329))) AND dropshipper_id:(50 314 389 533 411 272 304 410 79 234 347 299 505 274 544 19 96 58 ' \
                 '13 495 29 263 572 587 14 240 305 282 199 158 508 135 418 523 173 21 147 517 512 381 164 212 571 ' \
                 '515 548 504 584 550 567 201 294 372 403 7 359 210 553 534 541 327 513 417 563 588 155 506 383 358 ' \
                 '570 530 507 535 509 514 308 531 591 117 194 4 378 242 361 516 582 128 416 156 562 341 558 168 569 ' \
                 '250 202 518 377 92 555 165 136 183 142 153 37 30 303 74 503 259 540 213 217 398 292 270 76 180 542 ' \
                 '241 311 88 32 257 222 432 346 196 556 406 559 399 80 579 492 525 150 502 565 499 537 243 285 229 ' \
                 '379 5 122 90 265 364 524 362 188 83 116 568 267 339 578 101 145 12 586 249 536 323 203 532 566 280 ' \
                 '511 208 353 496 560 335 374 233 561 278 547 216 112 198 78 244 375 329 554)'

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
                                    resolve(response);
                                },
                                error: function(xhr) {
                                    console.log("Error:", xhr);
                                    resolve(null);
                                }
                            });
                        });
                    }
                    const result = await getResult(url, params);
                    return result;
                    '''
        result = self.driver.execute_script(script)
        return result['response']['docs'] if result else []

    def get_amazon_product(self, upc):
        self.driver.execute_script('window.open("");')
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(f'https://www.amazon.com/s?k={upc}&ref=nb_sb_noss')
        price_whole = self.driver.find_elements_by_css_selector('div[data-component-type=s-search-result] span[cel_widget_id=MAIN-SEARCH_RESULTS] .a-price-whole')
        price_fraction = self.driver.find_elements_by_css_selector('div[data-component-type=s-search-result] span[cel_widget_id=MAIN-SEARCH_RESULTS] .a-price-fraction')
        count_price_whole = len(price_whole)

        if count_price_whole > 0:
            price = price_whole[0].text + '.' + price_fraction[0].text
        else:
            price = ''

        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        return {
            'price': price,
            'shipping': 'No'
        }

    def get_page_count(self):
        """get number of pages
        """
        el_div = self.driver.find_element_by_css_selector('div[popover-is-open="search.go_to_page.is_open"] div')
        content = el_div.text

        return int(content[10:])

