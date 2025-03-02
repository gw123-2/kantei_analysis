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
    print(str(len(list_of_problems))+ " name problems found")
    for problem in list_of_problems:
        process_name_problem(db_cursor, problem)
          
        if AUTOSAVE:
            save_to_db(database_connection)

def let_user_choose_set_to_keep(variants):
    message = "which version do you want to keep? every other version will be replaced and finally removed.\n select by typing a number:"
    for i in range(len(variants)):
        message += "\n" + str(i) + ": " + str(variants[i])
    message += "\nkeep: "
    set_to_keep = base_tools.get_int_input(message, len(variants)-1)
    return set_to_keep

def overwrite_duplicates_in_database(db_cursor:sqlite3.Cursor, variants, set_to_keep):
    id_to_keep = variants[set_to_keep][0]
    for variant in variants:
        if not variant[0] == id_to_keep:
            db_cursor.execute("""
        UPDATE CABINETT_ROLE SET cabinett_member = ? WHERE cabinett_member = ?;                          
    """, (id_to_keep, variant[0]))
            print("replacing " + str(variant))
            db_cursor.execute("""
        UPDATE PERSON SET gender = ? WHERE internal_person_id = ?;                          
    """, ("#REMOVE#", variant[0]))
            print("flagged "+ str(variant))
            
    
def process_duplicate(db_cursor:sqlite3.Cursor, duplicate):
    db_cursor.execute("""
    SELECT * FROM PERSON WHERE first_name = ? and last_name = ?;
""", (duplicate[1], duplicate[2]))
    variants = db_cursor.fetchall()
    set_to_keep = let_user_choose_set_to_keep(variants)
    print("keeping: " + str(variants[set_to_keep]))
    overwrite_duplicates_in_database(db_cursor, variants, set_to_keep)
    

def clean_duplicates(db_cursor:sqlite3.Cursor):
    db_cursor.execute("""
    SELECT internal_person_id, first_name, last_name, COUNT(*) FROM PERSON WHERE gender != "#REMOVE#" GROUP BY first_name, last_name HAVING COUNT(*)>1 ;
""")
    duplicates = db_cursor.fetchall()
    print(str(len(duplicates)) + " duplicates found")
    for duplicate in duplicates:
        process_duplicate(db_cursor, duplicate)
            
        if AUTOSAVE:
            save_to_db(database_connection)

def delete_dataset_from_database(db_cursor:sqlite3.Cursor, dataset):
    if base_tools.get_bool_input(str(dataset) + " does not have a role (is not referenced). do you want to delete the set?"):
        print("deleting " + str(dataset))

        db_cursor.execute("""
        DELETE FROM PERSON WHERE internal_person_id = ?;
        """, (dataset[0],))

        if AUTOSAVE:
            save_to_db(database_connection)
    else:
        print("skipped  " + str(dataset))


def process_nonreferenced_persons(db_cursor:sqlite3.Cursor):
    db_cursor.execute("""
    SELECT * FROM PERSON WHERE internal_person_id NOT IN (SELECT cabinett_member FROM CABINETT_ROLE);
""")
    unreferenced_person_datasets = db_cursor.fetchall()
    print(str(len(unreferenced_person_datasets)) + " unreferenced persons found.")
    for orphan in unreferenced_person_datasets:
        delete_dataset_from_database(db_cursor, orphan)


def remove_flagged_persons(db_cursor:sqlite3.Cursor):
    db_cursor.execute("""
    DELETE FROM PERSON WHERE gender = "#REMOVE#"
""")


def get_sql_connection(path):
    #try:
        db_connection = sqlite3.connect(path)
        return db_connection
    #except 

def save_to_db(db_connection:sqlite3.Connection):
    print("saving...")
    db_connection.commit()
    print("saved")

if __name__ == "__main__":
    step = 0
    max_step = 4
    
    database_path = base_tools.get_path_for_existing_file("filename of database to clean:\t")
    database_connection = get_sql_connection(database_path)

    AUTOSAVE = base_tools.get_bool_input("Do you want to activate autosave after every manual change? this process might be slower than normal.")

    try:
        cursor = database_connection.cursor()
        clean_name_errors(cursor)
        save_to_db(database_connection)
        step = 1

        clean_duplicates(cursor)
        save_to_db(database_connection)
        step = 2

        


        if(base_tools.get_bool_input("Do you want to delete flagged Datasets?")):
            remove_flagged_persons(cursor)
            save_to_db(database_connection)
        step = 3

        process_nonreferenced_persons(cursor)
        save_to_db(database_connection)
        step = 4
        
        cursor.close()
        print("done.")
    except KeyboardInterrupt:
        print("\nManually cancelled via KeyboardInterrupt (Ctrl + C) after step " + str(step) + "/" + str(max_step) + ".")
        if(base_tools.get_bool_input("do you want to save the changes made?")):
            database_connection.commit()
    database_connection.close()