# MangaUpdates Scraper
Scrape MangaUpdates and create a database containing that data in PostgreSQL


Requirements:

PostgreSQL Installed on Computer

Python Packages:

-requests

-lxml

-beautifulsoup4

-psycopg2




database.ini in the same folder as scrape_manga_updates.py with the following format:

```
[postgresql]
host=localhost
database=your_database_name
user=postgres
password=your_password
```

Create a table in your PostgreSQL database with the name "manga_info". Make sure the table has the same labels as found in lines 33-36 of scrape_manga_updates.py. 

Future Developments:

-Create a function to update the database based on the most recently added manga to the MangaUpdates website (thus avoiding the need to recreate the entire database). 

-Let the user click on a series in "Related Series" and jump to that row in the PostgreSQL table.

-Look into improving the speed at which the database is created (in order to avoid being kicked from the website, the scraper only works every 5 seconds. This results in an extremely long database creation time (around 10 days at the time of update)).
