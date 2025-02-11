import sqlite3
import re as regex

def setup_database(database_connection:sqlite3.Connection):
    database_cursor = database_connection.cursor()
    database_cursor.execute("""
        CREATE TABLE PERSON(
                            internal_person_id INTEGER PRIMARY KEY,
                            first_name TEXT NOT NULL,
                            last_name TEXT NOT NULL,
                            first_name_furigana TEXT,
                            last_name_furigana TEXT,
                            gender TEXT NOT NULL,
                            party TEXT NOT NULL
                            );
        
    """)
    database_cursor.execute("""
    CREATE TABLE CABINETT(
                            cabinett_number INTEGER NOT NULL,
                            cabinett_reshuffle  INTEGER NOT NULL,
                            start_date TEXT NOT NULL,
                            end_date TEXT NOT NULL ,

                            PRIMARY KEY (cabinett_number, cabinett_reshuffle)
                            );
""")
    database_cursor.execute("""
    CREATE TABLE CABINETT_ROLE(
                            cabinett_number INTEGER NOT NULL,
                            cabinett_reshuffle  INTEGER NOT NULL,
                            cabinett_member TEXT NOT NULL,
                            role_name TEXT NOT NULL ,

                            PRIMARY KEY (cabinett_number, cabinett_reshuffle, role_name, cabinett_member)
                            );
""")
    database_connection.commit()


def populate_database_with_cabinett_members(database_connection:sqlite3.Connection, cabinett_site:str):
    database_cursor_insert = database_connection.cursor()

    shuffle_member_matrix = create_Shuffle_memebers_matrix(cabinett_site)
    for shuffle in range(len(shuffle_member_matrix)) :
        print("SHUFFLE " + str(shuffle))
        for member_with_role in shuffle_member_matrix[shuffle]:
            Insert_person_to_database(database_connection, member_with_role[0], "m", "LDP")
            person_id = get_id_of_person(database_connection, member_with_role[0])
            cabinett_number = get_cabinett_number_from_html(cabinett_site)
            for role in member_with_role[1]:
                print("GIVE ROLE "+ role +" TO " + str(person_id) + " FOR CABINETT "+ cabinett_number + " RESHUFFLE " + str(shuffle))
                try:
                    database_cursor_insert.execute("INSERT INTO CABINETT_ROLE (cabinett_number, cabinett_reshuffle, cabinett_member, role_name) VALUES(?,?,?,?);",(cabinett_number, shuffle, person_id, role))
                except sqlite3.IntegrityError:
                    print("ALREADY EXISTING")
        database_connection.commit()
            


            

def is_role_in_columns(role, columns):
    for column in columns:
        if column == role:
            return True
    return False


def person_in_database(database_connection:sqlite3.Connection, name):
    return get_id_of_person(database_connection, name) > 0
    
def get_id_of_person(database_connection:sqlite3.Connection, name):
    database_cursor = database_connection.cursor()
    database_cursor.execute("""
        SELECT internal_person_id FROM PERSON WHERE first_name = ? AND last_name = ? AND first_name_furigana = ? AND last_name_furigana = ?;
    """, (name[0][0],name[0][1],name[1][0], name[1][1]))
    try:
        query_result = database_cursor.fetchone()
        person_id = int(query_result[0])
    except TypeError:
        person_id = -1
    
    return person_id

def Insert_person_to_database(database_connection:sqlite3.Connection, name, gender, party):
    
    database_cursor =  database_connection.cursor()

    if(not person_in_database(database_connection, name)):
        database_cursor.execute("""
                INSERT INTO PERSON (first_name, last_name, first_name_furigana, last_name_furigana, gender, party) VALUES(?, ? ,? ,?, ?, ?);
            """, (name[0][0],name[0][1],name[1][0], name[1][1], gender, party))
        




def create_Shuffle_memebers_matrix(cabinett_site):
    shuffle_html_blocks = regex.findall("<section>.+?</section>", cabinett_site, flags=regex.DOTALL)
 
    shuffle_members_matrix = []
    for block in shuffle_html_blocks:
        members_with_role_in_shuffle_html = regex.findall("<tr>.+?scope=\"row\".+?</tr>", block, flags=regex.DOTALL)
        members_with_role_in_shuffle_clean = get_cabinett_members_with_role_per_shuffle_clean(members_with_role_in_shuffle_html)

        shuffle_members_matrix.append(members_with_role_in_shuffle_clean)
    
    return shuffle_members_matrix 
        

def get_cabinett_members_with_role_per_shuffle_clean(shuffle_raw_html):
    members_with_role_in_shuffle_clean = []        
    for member in shuffle_raw_html:
    
        name_html:str = regex.findall("<td>.+?</td>", member, flags=regex.DOTALL)[0]        
        name_clean = split_cabinett_member_name_in_clean_kanji_furigana(name_html)

        roles_html = regex.findall("<li>.+?</li>", member, flags=regex.DOTALL)
        roles_clean = get_clean_roles_from_html(roles_html)
    
        members_with_role_in_shuffle_clean.append([name_clean, roles_clean])
    return members_with_role_in_shuffle_clean

def split_cabinett_member_name_in_clean_kanji_furigana(name_raw_html):

    name_clean = name_raw_html.replace("<td>", "")
    name_clean = name_clean.replace("</td>", "")

    if name_clean.find("alt=") >= 0:
        real_name_ind = name_clean.find("alt=\"")
        name_clean= name_clean[real_name_ind:]

    name_clean = name_clean.replace("\"", "")
    name_clean = name_clean.replace("alt=", "")
    name_clean = name_clean.replace(">", "")
    name_clean = name_clean.replace("　", " ")
    name_clean:str = name_clean.replace("）", "")
    name_clean = name_clean.split("（")
    name_furigana_clean = name_clean[1].split(" ")
    name_kanji_clean = name_clean[0].split(" ")

    return [name_kanji_clean, name_furigana_clean]



def get_clean_roles_from_html(roles_raw_html):
    roles_clean = []
    for role_html in roles_raw_html:
        if not is_cabinett_role_faulty(role_html):
            clean_role = cleanup_role_name(role_html)
            roles_clean.append(clean_role)
    return roles_clean


def cleanup_role_name(role_raw_html):
    clean_role = role_raw_html.replace("<li>" ,"")
    clean_role = clean_role.replace("</li>" ,"")
    return clean_role


def is_cabinett_role_faulty(role_html):
    filter_role = regex.findall(".{3,5}年\d{1,2}月\d{1,2}日", role_html)
    return len(filter_role)>0


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
    try:
        html_file = open(url, encoding="utf8", errors="surrogateescape")
        html_text = html_file.read()
        html_file.close()
        return html_text
    except FileNotFoundError:
        print("file cannot be found")
        return None
if __name__ == "__main__":
    database_path = input("path to databse:")
    database_connection = sqlite3.connect(database_path)
    
    setup_database(database_connection)

    cabinett_site_html = None
    while cabinett_site_html == None:
        site_to_be_analyzed = input("input url to site: ")
        cabinett_site_html = get_html_text(site_to_be_analyzed)
    
    populate_database_with_cabinett_data(database_connection, cabinett_site_html)
    populate_database_with_cabinett_members(database_connection, cabinett_site_html)

