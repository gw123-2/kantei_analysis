import sqlite3
import base_tools


def ask_user_for_name_correction(data):
    done = False
    while not done:
        message = """
select part you want to edit:
0:  Done
1:  first name: %s
2:  last name: %s
3:  furigana first name: %s
4:  furigana last name: %s
5:  gender: %s
6:  party: %s
"""% (data[1], data[2],data[3],data[4],data[5], data[6])
        selection = base_tools.get_int_input(message, 6)
        if selection == 0:
            done = True
        else:
            print("current:\t" + data[selection])
            data[selection] = input("new:\t")
    
    return data

def update_person_data(db_cursor:sqlite3.Cursor, new_data):
    db_cursor.execute("""
    UPDATE PERSON SET first_name = ?, last_name = ?, first_name_furigana = ?, last_name_furigana = ?, gender = ?, party = ? WHERE internal_person_id = ?;
    """, (new_data[1], new_data[2], new_data[3], new_data[4], new_data[5], new_data[6], new_data[0]))

def process_name_problem(db_cursor, problem):
    print("problem found with set: " + str(problem))
    person_data = base_tools.copy_tuple_to_list(problem)
    person_data = ask_user_for_name_correction(person_data)
    print("new data:\t"+str(person_data))
    update_person_data(db_cursor, person_data)


def clean_name_errors(db_cursor:sqlite3.Cursor):
    db_cursor.execute("""
        SELECT * FROM PERSON WHERE first_name = last_name
    """)
    list_of_problems = db_cursor.fetchall()
    for problem in list_of_problems:
        process_name_problem(db_cursor, problem)            

def get_sql_connection(path):
    #try:
        db_connection = sqlite3.connect(path)
        return db_connection
    #except 



if __name__ == "__main__":
    database_path = base_tools.get_path_for_existing_file("filename of database to clean:\t")
    database_connection = get_sql_connection(database_path)
    clean_name_errors(database_connection.cursor())
    #database_connection.commit()