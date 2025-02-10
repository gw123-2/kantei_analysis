import sqlite3
import re as regex

def setup_database(database_connection:sqlite3.Connection):
    database_cursor = database_connection.cursor()
    database_cursor.execute("""
        CREATE TABLE PERSON(
                            internal_person_id INTEGER PRIMARY KEY,
                            first_name TEXT NOT NULL,
                            last_name TEXT NOT NULL,
                            gender TEXT NOT NULL,
                            birth_date TEXT NOT NULL,
                            death_date TEXT);
        
    """)
    database_connection.commit()
    database_cursor.execute("""
    CREATE TABLE CABINETT(
                            cabinett_number INTEGER NOT NULL,
                            cabinett_reshuffle_times  INTEGER NOT NULL,
                            start_date TEXT NOT NULL,
                            end_date TEXT,
                            prime_minister INTEGER,

                            PRIMARY KEY (cabinett_number, cabinett_reshuffle_times)
                            );
""")
    database_connection.commit()

def scrape_cabinett_html_for_ministers(cabinett_site:str):
    cabinett_number = regex.findall("第\d{1,3}代",cabinett_site)
    cabinett_shuffle = regex.findall("<p class=\"module-detail-text module-text--note\">.{3,5}年\d{1,2}月\d{1,2}日発足　.{3,5}年\d{1,2}月\d{1,2}日現在</p>",cabinett_site )

    print(str(cabinett_number) + " Cabinett, shuffles: " + str(clean_cabinett_shuffle_htmltext_dates(cabinett_shuffle)))

def clean_cabinett_shuffle_htmltext_dates(dates:list):
    clean_dates = dates
    for i in range(len(dates)):
        clean_dates[i] = cleanup_shuffle_date(dates[i])
    return clean_dates

def cleanup_shuffle_date(date:str):
    clean_date:str = regex.findall(".{3,5}年\d{1,2}月\d{1,2}日発足　.{3,5}年\d{1,2}月\d{1,2}日現在", date)[0]
    clean_date.replace("発足", "")
    clean_date.replace("現在", "")

    return clean_date.split("　")


def get_html_text(url:str):
    html_file = open(url, encoding="utf8", errors="surrogateescape")
    html_text = html_file.read()
    html_file.close()
    return html_text

if __name__ == "__main__":
    database_path = input("path to databse:")
    database_connection = sqlite3.connect(database_path)
    
    setup_database(database_connection)

    site_to_be_analyzed = input("input url to site: ")
    cabinett_site_html = get_html_text(site_to_be_analyzed)
    scrape_cabinett_html_for_ministers(cabinett_site_html)

