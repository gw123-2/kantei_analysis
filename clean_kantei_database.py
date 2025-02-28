import sqlite3
import base_tools

def clean_name_errors(db_cursor:sqlite3.Cursor):
    list_of_problems = db_cursor.execute("""
        SELECT * FROM PERSON WHERE first_name = last_name
    """)
     

def get_sql_connection(path):
    #try:
        db_connection = sqlite3.connect(path)
        return db_connection
    #except 



if __name__ == "__main__":
    database_path = base_tools.get_path_for_existing_file("filename of database to clean:\t")
    database_connection = get_sql_connection(database_path)
    clean_name_errors(database_connection.cursor())
