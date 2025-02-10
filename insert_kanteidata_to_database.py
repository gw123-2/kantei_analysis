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
                            cabinett_reshuffle  INTEGER NOT NULL,
                            start_date TEXT NOT NULL,
                            end_date TEXT NOT NULL ,
                            prime_minister INTEGER,

                            PRIMARY KEY (cabinett_number, cabinett_reshuffle)
                            );
""")
    database_connection.commit()


def populate_database_with_cabinett_data(database_connection:sqlite3.Connection, cabinett_site:str):
    cabinett_number = get_cabinett_number_from_html(cabinett_site)
    cabinett_shuffle = get_cabinett_shuffles_from_html(cabinett_site)
        
    insert_new_cabinett_into_database(database_connection, cabinett_number, cabinett_shuffle)

def insert_new_cabinett_into_database(database_connection:sqlite3.Connection, number, shuffles):
    database_cursor = database_connection.cursor()
    for i in range(len(shuffles)):
        database_cursor.execute("""
            INSERT INTO CABINETT (cabinett_number, cabinett_reshuffle, start_date, end_date) VALUES(?, ?, ? ,?)
        """, (str(number), str(i), str(shuffles[i][0]), str(shuffles[i][1]))  )
        database_connection.commit()
    
def get_cabinett_number_from_html(cabinett_site:str):
    cabinett_number:str = regex.findall("第\d{1,3}代",cabinett_site)[0]
    cabinett_number = cabinett_number.replace("第", "")
    cabinett_number = cabinett_number.replace("代", "")
    return cabinett_number

def get_cabinett_shuffles_from_html(cabinett_site):
    shuffles_raw = regex.findall("<p class=\"module-detail-text module-text--note\">.{3,5}年\d{1,2}月\d{1,2}日発足　.{3,5}年\d{1,2}月\d{1,2}日現在</p>",cabinett_site )
    clean_shuffles = clean_cabinett_shuffle_htmltext_dates(shuffles_raw)
    return clean_shuffles

def clean_cabinett_shuffle_htmltext_dates(dates:list):
    clean_dates = dates
    for i in range(len(dates)):
        clean_dates[i] = cleanup_shuffle_date(dates[i])
    return clean_dates

def cleanup_shuffle_date(date:str):
    clean_date:str = regex.findall(">.{3,5}年\d{1,2}月\d{1,2}日発足　.{3,5}年\d{1,2}月\d{1,2}日現在", date)[0]
    clean_date = clean_date.replace("発足", "")
    clean_date = clean_date.replace("現在", "")
    clean_date = clean_date.replace(">", "")

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

    populate_database_with_cabinett_data(database_connection, cabinett_site_html)

