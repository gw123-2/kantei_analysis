import sqlite3
import re as regex
import urllib.request
import base_tools

DEFAULT_KANTEI_INDEX = "https://www.kantei.go.jp/jp/rekidainaikaku/index.html"

def setup_database(database_cursor:sqlite3.Cursor):
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
    


def log( *args, filename=None):
    string = create_combined_string(args, "; ")
    if(filename==None):
        print(string)
    else:
        append_file(filename, string)
        

def append_file(filename, new_content):
    file = open(filename, "a", encoding="utf-8")
    file.write(str(new_content))
    file.close

def create_combined_string(list, splitter_character):
    string = ""
    first = True
    for arg in list:
        if not first:
            string += splitter_character
        else:
            first = False
        string += str(arg)
    return string

def populate_database_with_cabinett_members(database_connection:sqlite3.Connection, cabinett_site:str):
    database_cursor = database_connection.cursor()
    
    cabinett_number = get_cabinett_number_from_html(cabinett_site)
    shuffle_member_matrix = create_Shuffle_memebers_matrix(cabinett_site)
    insert_shuffle_member_matrix_into_database(database_cursor, shuffle_member_matrix, cabinett_number)

    database_connection.commit()
    
            
def insert_shuffle_member_matrix_into_database(database_cursor, shuffle_member_matrix, cabinett_number):
    for shuffle in range(len(shuffle_member_matrix)) :
        log("SHUFFLE " + str(shuffle+1)+ "/" + str(len(shuffle_member_matrix)))
        for member_with_role in shuffle_member_matrix[shuffle]:
            add_minister_to_cabinett(database_cursor, member_with_role, cabinett_number, shuffle)
                
        

def add_minister_to_cabinett(database_cursor, member_with_role, cabinett_number, shuffle):
    Insert_person_to_database(database_cursor, member_with_role[0], "m", "LDP")
    person_id = get_id_of_person(database_cursor, member_with_role[0])
    for role in member_with_role[1]:
        give_roles_to_minister(database_cursor, role, person_id, cabinett_number, shuffle)

def give_roles_to_minister(database_cursor, role, person_id, cabinett_number, shuffle):
    #log("GIVE ROLE "+ role +" TO " + str(person_id) + " FOR CABINETT "+ cabinett_number + " RESHUFFLE " + str(shuffle))
    try:
        database_cursor.execute("INSERT INTO CABINETT_ROLE (cabinett_number, cabinett_reshuffle, cabinett_member, role_name) VALUES(?,?,?,?);",(cabinett_number, shuffle, person_id, role))
    except sqlite3.IntegrityError:
       #log("ALREADY EXISTING")
       pass

            

def is_role_in_columns(role, columns):
    for column in columns:
        if column == role:
            return True
    return False


def person_in_database(database_connection:sqlite3.Connection, name):
    return get_id_of_person(database_connection, name) > 0
    
def get_id_of_person(database_cursor:sqlite3.Cursor, name):
    database_cursor.execute("""
        SELECT internal_person_id FROM PERSON WHERE last_name = ? AND first_name = ?;
    """, (name[0][0],name[0][1]))
    try:
        query_result = database_cursor.fetchone()
        person_id = int(query_result[0])
    except TypeError:
        person_id = -1
    
    return person_id

def Insert_person_to_database(database_cursor:sqlite3.Cursor, name, gender, party):

    if(not person_in_database(database_cursor, name)):
        database_cursor.execute("""
                INSERT INTO PERSON ( last_name, first_name, last_name_furigana, first_name_furigana, gender, party) VALUES(?, ? ,? ,?, ?, ?);
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

        roles_html = get_roles_raw_from_html(member)
        roles_clean = get_clean_roles_from_html(roles_html)
    
        members_with_role_in_shuffle_clean.append([name_clean, roles_clean])
    return members_with_role_in_shuffle_clean

def get_roles_raw_from_html(roles_html):
    roles_raw = regex.findall("<li>.+?</li>", roles_html, flags=regex.DOTALL)
    if len(roles_raw) <= 0:
        roles_raw = regex.findall("<th scope=\"row\">.+?</th>", roles_html, flags=regex.DOTALL)
    return roles_raw

def split_cabinett_member_name_in_clean_kanji_furigana(name_raw_html):

    name_clean = name_raw_html.replace("<td>", "")
    name_clean = name_clean.replace("</td>", "")

    if name_clean.find("alt=") >= 0:
        real_name_ind = name_clean.find("alt=\"")
        name_clean= name_clean[real_name_ind:]

    name_clean = name_clean.replace("\"", "")
    name_clean = name_clean.replace("alt=", "")
    name_clean = name_clean.replace(">", "")
    name_clean = name_clean.replace("<br", "")
    name_clean = name_clean.replace("※", "")
    name_clean = name_clean.replace("　", " ")
    name_clean:str = name_clean.replace("＊", "")
    name_clean:str = name_clean.replace("）", "")    
    name_clean = name_clean.split("（")
    try:
        name_furigana_clean = name_clean[1].split(" ")
        name_kanji_clean = name_clean[0].split(" ")
    except IndexError:
        name_furigana_clean = ["", ""]
        name_kanji_clean = name_clean[0].split(" ")
    if len(name_kanji_clean) != 2:
        if(CORRECTION_MODE):
            print("error with name: "+ name_kanji_clean + ". please help with correction")
            last_name = input("please input LAST name:\t")
            first_name = input("please input FIRST name:\t")
            name_kanji_clean = [last_name, first_name]
        else:
            name_kanji_clean = [name_kanji_clean[0], name_kanji_clean[0]]
    if len(name_furigana_clean) != 2:
        name_furigana_clean = ["", ""]
        

    return [name_kanji_clean, name_furigana_clean]



def get_clean_roles_from_html(roles_raw_html):
    roles_clean = []
    for role_html in roles_raw_html:
        if not is_cabinett_role_faulty(role_html):
            clean_role = cleanup_role_name(role_html)
            roles_clean.append(clean_role)
    return roles_clean


def cleanup_role_name(role_raw_html):
    clean_role:str = role_raw_html.replace("<li>" ,"")
    clean_role = clean_role.replace("</li>" ,"")
    clean_role = clean_role.replace("<br>" ,"")
    clean_role = clean_role.replace("</th>" ,"")
    if clean_role.find("（") == 0:
        clean_role = clean_role[1:]
    if clean_role.find("）") == len(clean_role)-1:
        clean_role = clean_role[:len(clean_role)-2]
    
    clean_role = clean_role.replace("" ,"")
    clean_role = clean_role.replace("▲" ,"")
    clean_role = clean_role.replace("<th scope=\"row\">" ,"")
    return clean_role


def is_cabinett_role_faulty(role_html):
    filter_role = regex.findall(".{3,5}年\d{1,2}月\d{1,2}日", role_html)
    return len(filter_role)>0


def populate_database_with_cabinett_data(database_connection:sqlite3.Connection, cabinett_site:str):
    cabinett_number = get_cabinett_number_from_html(cabinett_site)
    cabinett_shuffles = get_cabinett_shuffles_from_html(cabinett_site)

    log("CABINETT: " + cabinett_number)

    insert_new_cabinett_into_database(database_connection.cursor(), cabinett_number, cabinett_shuffles)
    database_connection.commit()

def insert_new_cabinett_into_database(database_cursor:sqlite3.Cursor, number, shuffles):
    
    for i in range(len(shuffles)):
        try:
            database_cursor.execute("""
                INSERT INTO CABINETT (cabinett_number, cabinett_reshuffle, start_date) VALUES(?, ?, ?)
            """, (str(number), str(i), str(shuffles[i]))  )
        except sqlite3.IntegrityError:
            #log("ALREADY EXISTING")
            pass
    
def get_cabinett_number_from_html(cabinett_site:str):
    cabinett_number:str = regex.findall("第\d{1,3}代",cabinett_site)[0]
    cabinett_number = cabinett_number.replace("第", "")
    cabinett_number = cabinett_number.replace("代", "")
    return cabinett_number

def get_cabinett_shuffles_from_html(cabinett_site):
    shuffles_raw = regex.findall("<p class=\"module-detail-text module-text--note\">.{3,5}年\d{1,2}月\d{1,2}日.+?</p>",cabinett_site )
    clean_shuffles = clean_cabinett_shuffle_htmltext_dates(shuffles_raw)
    return clean_shuffles

def clean_cabinett_shuffle_htmltext_dates(dates:list):
    clean_dates = dates
    for i in range(len(dates)):
        clean_dates[i] = cleanup_shuffle_date(dates[i])
    return clean_dates

def cleanup_shuffle_date(date:str):
    clean_date:str = regex.findall(">.{3,5}年\d{1,2}月\d{1,2}日", date)[0]
    clean_date = clean_date.replace(">", "")
    return clean_date

def get_cabinett_page_link_list_from_index_page(index_page_html):
    links = regex.findall("/jp/rekidainaikaku/\d{1,3}.html\"", index_page_html)
    clean_links = cleanup_links_to_cabinett_site(links)
    return clean_links
    
    
def cleanup_links_to_cabinett_site(links):
    clean_links = []
    for link in links:
        clean_link:str = link.replace("<a href=\"", "")
        clean_link = clean_link.replace("\"","")
        clean_link = clean_link.replace(" ","")
        clean_link = "https://www.kantei.go.jp" + clean_link
        clean_links.append(clean_link)

    return clean_links    

def get_html_text(url:str):
    log("fetching data from: " + url)
    html = urllib.request.urlopen(url).read()
    decoded_html = html.decode("utf8")
    log("got data from: " + url)
    return decoded_html
        

def get_html_text_from_file(path:str):
    try:
        html_file = open(path, encoding="utf8", errors="surrogateescape")
        html_text = html_file.read()
        html_file.close()
        return html_text
    except FileNotFoundError:
        log("file cannot be found")
        return None
    
def fill_database_with_cabinett_data_from_website(index_site_html, database_connection):
    links = get_cabinett_page_link_list_from_index_page(index_site_html)
    for link in links:
        cabinett_site_html = get_html_text(link)
        populate_database_with_cabinett_data(database_connection, cabinett_site_html)
        populate_database_with_cabinett_members(database_connection, cabinett_site_html)



 

def get_kantei_website():
    index_site_html = None
    while index_site_html == None:
        site_to_be_analyzed = input("input url to kantei site:\t")
        if site_to_be_analyzed == "":
            return get_html_text(DEFAULT_KANTEI_INDEX)
        index_site_html = get_html_text(site_to_be_analyzed)

if __name__ == "__main__":

    
    database_path = base_tools.get_path_for_new_file("filename for new databse:\t")    
    index_site_html = get_kantei_website()
    CORRECTION_MODE = base_tools.get_bool_input("do you want to MANUALLY correct mistakes if they are found during the populating process?\n Type number to select:\n 0:NO \t 1:YES")
    
    database_connection = sqlite3.connect(database_path)

    log("setting up database...")
    setup_database(database_connection.cursor())
    database_connection.commit()
    log("done!")


    log("filling database with data...")
    fill_database_with_cabinett_data_from_website(index_site_html, database_connection)
    log("Done!")