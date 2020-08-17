import pymysql


class Database:
    host = 'localhost'
    user = 'root'
    password = 'root'
    db = 'inventory_source_scraper'

    def __init__(self):
        self.con = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                   cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.con.cursor()
        self.cur.execute('CREATE DATABASE IF NOT EXISTS %s' % self.db)
        self.con = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.db, autocommit=True,
                                   cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.con.cursor()
        self.cur.execute('CREATE TABLE IF NOT EXISTS `products` ('
                         '`id` int(11) NOT NULL auto_increment, '
                         '`name` VARCHAR(800), '
                         '`upc` VARCHAR(20), '
                         '`vendor` VARCHAR(50), '
                         '`company` VARCHAR(100), '
                         '`price_inventory` VARCHAR(10), '
                         '`price_msrp` VARCHAR(10), '
                         '`price_amazon` VARCHAR(10), '
                         '`shipping_amazon` VARCHAR(10), '
                         'PRIMARY KEY (`id`))')
        self.cur.execute('set max_allowed_packet=134217728')

    def remove_data(self):
        self.cur.execute('TRUNCATE TABLE `products`')

    def save_data(self, product):
        query = """INSERT INTO `products` (`name`, `upc`, `vendor`, `company`, `price_inventory`, `price_msrp`, 
        `price_amazon`, `shipping_amazon`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) """
        self.cur.execute(query, (product['name'],
                                 product['upc'],
                                 product['vendor'],
                                 product['company'],
                                 product['price_inventory'],
                                 product['price_msrp'],
                                 product['price_amazon'],
                                 product['shipping_amazon']))
        return

    def get_all_products(self):
        query = 'SELECT * FROM `products`'
        self.cur.execute(query)
        result = self.cur.fetchall()
        return result

