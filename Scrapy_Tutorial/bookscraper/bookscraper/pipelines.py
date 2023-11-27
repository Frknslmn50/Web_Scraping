# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector


class BookscraperPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        #Strip all white spaces from the fields if not description
        field_names = adapter.field_names()
        for field in field_names:
            if field != 'description':
                adapter[field] = adapter[field].strip()
        
        # Convert category to lower case
        adapter['category'] = adapter['category'].lower()

        # Get stock and convert to integer
        splitted_string = adapter['availability'].split('(')[1]
        if len(splitted_string) < 2:
            adapter['availability'] = 0
        else:
            adapter['availability'] = int(splitted_string.split(" ")[0])

        # Get price and convert to float
        price_keys = ['price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            adapter[price_key] = float(adapter[price_key].replace('£',''))

        # Convert rating to integer ex: One -> 1
        rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
        adapter['star_rating'] = rating_map[adapter['star_rating']]

        # Convert number of reviews to integer
        adapter['number_of_reviews'] = int(adapter['number_of_reviews'])



        return item

class SaveToMySQLPipeline:

    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        self.conn = mysql.connector.connect(
            host = 'localhost',
            user = 'your_db_username',
            passwd = 'your_db_password',
            database = 'books'
        )
        self.cur = self.conn.cursor()

    def create_table(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS books(
            id int not null auto_increment primary key,
            url varchar(255),
            title text,
            price_excl_tax float,
            price_incl_tax float,
            tax float,
            availability int,
            number_of_reviews int,
            star_rating int,
            category varchar(255),
            description text
        )""")

    def process_item(self, item, spider):
        self.store_db(item)
        return item

    def store_db(self, item):
        adapter = ItemAdapter(item)
        self.cur.execute("""INSERT INTO books (
                          url, 
                          title, 
                          price_excl_tax, 
                          price_incl_tax, 
                          tax, 
                          availability, 
                          number_of_reviews, 
                          star_rating, category, 
                          description
                          ) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",(
                              adapter['url'], 
                              adapter['title'], 
                              adapter['price_excl_tax'], 
                              adapter['price_incl_tax'], 
                              adapter['tax'], 
                              adapter['availability'], 
                              adapter['number_of_reviews'], 
                              adapter['star_rating'], 
                              adapter['category'], 
                              adapter['description']
                            )
                        )
        self.conn.commit()

    def close_spider(self, spider):
        # Close connection and cursor after spider is done
        self.cur.close()
        self.conn.close()