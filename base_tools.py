#a collection of basic tools
import os.path
       

def get_path_for_existing_file(message:str) -> str:
    database_path = None
    while database_path == None:
        database_path = input(message)
        if(not os.path.isfile(database_path)):
            print("file does not exists, please chose an existing file")
            database_path = None
    return database_path

def copy_tuple_to_list(tuple:tuple) -> list:
    final_list = []
    for element in tuple:
        final_list.append(element)
    return final_list

def get_path_for_new_file(message:str) -> str:
    database_path = None
    while database_path == None:
        database_path = input(message)
        if(os.path.isfile(database_path)):
            print("file already exists, please chose a different name")
            database_path = None
    return database_path

def get_int_input(message, upper_limit = 1, lower_limit = 0) -> int:
    answer = None
    while answer == None:
        user_input = input(message)
        try:
            input_number = int(user_input)
            if input_number < lower_limit or input_number > upper_limit:
                print("number is not within boundaries, please try again")
                answer = None
            else:
                answer = input_number
        except ValueError:
            print("Input does not contain a number, please try again")
            answer = None
    return answer

def get_bool_input(message:str) -> bool:
    yes_options = ["y", "yes"]
    no_options = ["n", "no"]

    user_input = input(message)
    answer = None
    user_input = user_input.lower()
    user_input = user_input.strip()
    while answer == None:
        if user_input in yes_options:
            answer = True
        elif user_input in no_options:
            answer = False
        else:
            print("Answer is incorrect format")
            answer = None
    return answer