import datetime
from bs4 import BeautifulSoup
import requests
from random import randint
import time
import re
import psycopg2
from Observer import Observer
from Subject import Subject

current_date = datetime.datetime.now()
formatted_date = current_date.strftime("%m%%2F%d%%2F%Y")
total_articles: int = 0
total_pages: int = 0
terminate = False


class DataUpdate(Subject):
    def __init__(self):
        self.observers = []
        self.data = ""

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update(self.data)

    def set_data(self, data):
        self.data = data
        self.notify_observers()


class GetData(Observer):
    def __init__(self):
        self.data = []

    def update(self, data):
        self.data = data


data_update = DataUpdate()
observer = GetData()
data_update.add_observer(observer)


def wait():
    time.sleep(randint(3, 7))


def create_table():
    try:
        connection = psycopg2.connect(
            user='postgres',
            password='12345',
            database='Demo',
            host='localhost',  # load the data to the postgreSQL
            port=5432
        )
        cursor = connection.cursor()

        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ZeroHedge (
                id SERIAL PRIMARY KEY,
                title TEXT,
                author_name TEXT,
                date_time TEXT,
                category TEXT,
                type TEXT,
                relevance NUMERIC,
                url TEXT,
                comments INTEGER,
                views INTEGER,
                image_urls TEXT[],
                "references" TEXT[],
                content TEXT
            )
        ''')
        connection.commit()
        print("Table created successfully")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while creating PostgreSQL table:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()


def insert_article_to_db(item: dict):
    try:
        connection = psycopg2.connect(
            user='postgres',
            password='12345',
            database='Demo',
            host='localhost',
            port=5432
        )
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO ZeroHedge (Title, author_name, date_time, category, type, relevance, url, comments, views, image_urls, "references", content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            item['Title'],
            item['authorName'],
            item['dateTime'],
            item['category'],
            item['type'],
            item['relevance'],
            item['url'],
            item['comments'],
            item['views'],
            item['imageUrls'],
            item['references'],
            item['content']
        ))
        connection.commit()
        # print("Data inserted successfully")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while inserting data into PostgreSQL:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()


def scrape_content(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        content = soup.select_one('main').get_text()
        content = content.rstrip('0Loading...')
    except:
        content = 'None'
    try:
        image_urls = [img['src'] for img in (soup.select_one('main').select('img[data-entity-type="file"]'))]
    except:
        image_urls = 'None'
    try:
        references = [ref['href'] for ref in soup.select_one('main').select('a[href]')]
    except:
        references = 'None'
    try:
        ID = re.findall(r'nid":.*?,', response.text)[0].split(':"')[1].rstrip('",')
        time.sleep(1)
        comments = requests.get(f'https://cms.zerohedge.com/coral-talk-comment-counts?nids={ID}').json()[ID]
        time.sleep(1)
        views = requests.get(f'https://cms.zerohedge.com/statistics-ajax?entity_ids={ID}').json()[ID]
    except:
        comments = 0
        views = 0
    return comments, views, image_urls, references, content


def scrape(query: str):
    query = query.replace(' ', '+')
    global total_pages
    global total_articles
    current_page: int = 0
    while current_page <= total_pages:

        base_url = f'https://cms.zerohedge.com/api/views/search?[max]={formatted_date}&qTitle={query}&page={current_page}&_format=json'

        try:
            response = requests.get(base_url)
            json_data = response.json()
            total_pages = int(json_data['pager']['pages'])
            total_articles = json_data['pager']['count']
            raw_articles = response.json()['results']
            print(f'current_page: {current_page}, total_pages: {total_pages}, total_articles: {total_articles}')
            for raw_article in raw_articles:
                global terminate
                if not terminate:
                    article = dict()
                    try:
                        article['Title'] = str(raw_article['title']).split('"en">')[1].replace('&quot;', '"').rstrip('</a>')
                    except:
                        article['Title'] = 'None'
                    try:
                        article['authorName'] = raw_article['authorName']
                    except:
                        article['authorName'] = 'None'
                    try:
                        article['dateTime'] = raw_article['created']
                    except:
                        article['dateTime'] = 'None'
                    try:
                        article['category'] = raw_article['category']
                    except:
                        article['category'] = 'None'
                    try:
                        article['type'] = raw_article['type']
                    except:
                        article['type'] = 'None'
                    try:
                        article['relevance'] = raw_article['relevance']
                    except:
                        article['relevance'] = 'None'
                    try:
                        article['url'] = 'https://www.zerohedge.com' + str(raw_article['title'].split('"')[1])
                    except:
                        article['url'] = 'None'
                    try:
                        article['comments'], article['views'], article['imageUrls'], article['references'], article['content'] = scrape_content(article['url'])
                    except:
                        article['comments'], article['views'], article['imageUrls'], article['references'], article['content'] = 0, 0, [], [], 'None'
                    insert_article_to_db(article)
                    global data_update
                    data_update.set_data(article)
                    wait()
                else:
                    return
            current_page += 1
        except requests.RequestException as e:
            print(f"Error fetching URL: {base_url}")


def stop():
    global terminate
    terminate = True


def main(query: str):
    create_table()
    scrape(query=query)

