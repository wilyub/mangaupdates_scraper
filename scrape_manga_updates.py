#!/usr/bin/env python
import requests
import lxml
from bs4 import BeautifulSoup
import psycopg2
from configparser import ConfigParser
import os
import time

def config():
    filename='database.ini'
    section='postgresql'
    # create a parser
    ini_path = os.path.join(os.getcwd(), filename)
    parser = ConfigParser()
    # read config file
    parser.read(ini_path)

    # get section, default to postgresql
    db={}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

def insert_manga(data_list):
    """Connect to the PostgreSQL MangaUpdates database server & add a row for a manga entry"""

    insert_stmt = (
        "INSERT INTO manga_info (manga_name, book_type, author, artist, genres, related_series, categories, "
        "status_origin, start_year, completely_scan, original_publisher, serialized, licensed_english, english_publisher, user_rating) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    )
    conn = None
    try:
        # read connection 
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()
        # execute data insertion
        cur.execute(insert_stmt, data_list)
        # commit changes to database
        conn.commit()
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

if __name__ == '__main__':
    base_url = 'https://www.mangaupdates.com/whatsnew.html?orderby=date&&'
    base_page = requests.get(base_url)
    base_soup = BeautifulSoup(base_page.content, 'lxml')
    most_recent = base_soup.find('div', class_='row no-gutters text p-3')
    most_recent_url = most_recent.find('a', title='Series Info')['href']
    max_value = int(most_recent_url[44:])
    child = base_soup.find('b', string='2021')
    parent = child.find_parent('p')
    year_list = parent.find_all('a', rel='nofollow')
    for link in year_list:
        year_link = link['href']
        new_base_page = requests.get(year_link)
        new_base_soup = BeautifulSoup(new_base_page.content, 'lxml')
        new_most_recent = new_base_soup.find('div', class_='row no-gutters text p-3')
        new_most_recent_url = new_most_recent.find('a', title='Series Info')['href']
        check_value = int(new_most_recent_url[44:])
        if check_value > max_value:
            max_value = check_value
    manga_base_url = 'https://www.mangaupdates.com/series.html?id='

    for x in range(1,max_value + 1):
        manga_url = manga_base_url + str(x)
        manga_page = requests.get(manga_url)
        manga_soup = BeautifulSoup(manga_page.content, 'lxml')
        check_error = manga_soup.find('span', class_='releasestitle tabletitle')
        if check_error == None:
            continue
        else:
            manga_name = manga_soup.find('span', class_='releasestitle tabletitle').text
        data_collection = manga_soup.find_all('div', class_='sContent')
        if len(data_collection) != 27:
            continue
        #Indexes for data_collection
        #1 = Type
        manga_type_unclean = data_collection[1].text
        manga_type_clean = ''
        for letter in manga_type_unclean:
            if letter.isalpha():
                manga_type_clean = manga_type_clean + letter
            else:
                break
        #2 = Related Series
        related_array = data_collection[2].find_all('u')
        related_series = []
        for related in related_array:
            related_series = related_series + [related.text]
        #6 = Status Origin
        status_volume = data_collection[6].text.split()
        if len(status_volume) == 2:
            status_unclean = (status_volume[1])[1:]
        elif len(status_volume) == 1:
            status_unclean = status_volume[0]
        else:
            status_unclean = (status_volume[2])[1:]
        status_clean = ''
        for letter in status_unclean:
            if letter != ')':
                status_clean = status_clean + letter
            else:
                break
        #7 = Completely Scan
        comp_scan_unclean = data_collection[7].text
        comp_scan_clean = ''
        for letter in comp_scan_unclean:
            if letter.isalpha():
                comp_scan_clean = comp_scan_clean + letter
            else:
                break
        #11 = Rating
        average_info = data_collection[11].text.split()
        if len(average_info) == 1:
            user_rating = 0.0
        else:
            user_rating = average_info[1]
        #14 = Genres
        genre_array = data_collection[14].find_all('u')
        genre_collection = []
        for genre in range(len(genre_array)-1):
            genre_collection = genre_collection + [genre_array[genre].text]
        #15 = Categories
        category_array = data_collection[15].find_all('a', rel='nofollow')
        category_collection = []
        for category in category_array:
            category_collection = category_collection + [category.text]
        #18 = Author
        if data_collection[18].find('u') == None:
            author = "N/A"
        else:
            author = data_collection[18].find('u').text
        #19 = Artist
        if data_collection[19].find('u') == None:
            artist = "N/A"
        else:
            artist = data_collection[19].find('u').text
        #20 = Start Year
        start_year_unclean = data_collection[20].text
        start_year_clean = ''
        for number in start_year_unclean:
            if number.isdigit():
                start_year_clean = start_year_clean + number
            else:
                break
        if start_year_clean == '':
            start_year_clean = 0
        #21 = Original Publisher
        orig_pub_unclean = data_collection[21].find_all('u')
        orig_pub_clean = []
        for orig in orig_pub_unclean:
            orig_pub_clean = orig_pub_clean + [orig.text]
        #22 = Serialized
        serialized_unclean = data_collection[22].find_all('u')
        serialized_clean = []
        for seri in serialized_unclean:
            serialized_clean = serialized_clean + [seri.text]
        #23 = Licensed English
        licensed_unclean = data_collection[23].text
        licensed_clean = ''
        for letter in licensed_unclean:
            if letter.isalpha():
                licensed_clean = licensed_clean + letter
            else:
                break
        #24 = English Publisher
        eng_pub_unclean = data_collection[24].find_all('u')
        eng_pub_clean = []
        for pub in eng_pub_unclean:
            eng_pub_clean = eng_pub_clean + [pub.text]

        data_cleaned_collection = (manga_name, manga_type_clean, author, artist, genre_collection, related_series, category_collection, 
            status_clean, start_year_clean, comp_scan_clean, orig_pub_clean, serialized_clean, licensed_clean, eng_pub_clean, user_rating)

        insert_manga(data_cleaned_collection)
        time.sleep(5)     