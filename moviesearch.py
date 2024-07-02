import os
from dotenv import load_dotenv
import requests
import datetime
import socket
import json
import random
import ast

load_dotenv()

options = ["Release year", "Vote"]
advanced_options = ["Language", "Vote threshold"]

DEFINITIONS = {
    "Release year": "searches for movies with an initial release in the given year - Default current year",
    "Language": "searches for movies with dialogue in the given language - Default English",
    "Vote threshold": "minimum amount of user votes for ratings - Default 2500",
    "Vote": "minimum voter rating score - Default 8.0"
}

DEFAULT_YEAR = str(datetime.datetime.now().year)
DEFAULT_LANGUAGE = "en"
VOTE_COUNT_THRESHOLD = "2500"
VOTE_SCORE = "8"

users = {}


def main():
    # displays the application title and instructions
    intro()

    # gets user login info
    user_name = login()

    # Repeats searches until user ends program
    search = True
    while search:
        # Displays currently enables options and search instructions
        define_search()

        get_user_choice(user_name)

        # Gets user input for each enabled option
        for option in options:
            get_option(option)

        # Retrieves movies from API using user options
        get_movies(user_name)

        # Prompts user to search again
        user_choice = input("What you like to initiate another search? Y/N: ")
        if user_choice.upper() == "N":
            search = False
            print("\nThank you for using Top Movie Finder! Goodbye!")


def get_user_choice(user_name):
    """
    Prompts user to select a menu option and calls the appropriate functions to display choice.

    :param user_name: string name of logged-in user
    :return: none
    """
    user_choice = input("Input A for advanced features, W to see watchlist, or hit enter to continue:")
    # Displays advanced menu options
    if user_choice.isalpha() and user_choice.upper() == 'A':
        advanced_search()
        define_search()
    # Retrieves current user's watch list from microservice
    elif user_choice.isalpha() and user_choice.upper() == 'W':
        retrieve_watch_list(user_name)


def get_option(option):
    """
    Calls function to get user input for enabled option.

    :param option: string option name
    :return: function call for desired option
    """
    match option:
        case "Release year":
            return get_year()
        case "Language":
            return get_language()
        case "Vote threshold":
            return get_threshold()
        case "Vote":
            return get_vote()


def get_movies(user_name):
    """
    Retrieves list movies from The Movie Database API using selected user options or default values.

    :param user_name: string name of logged-in user
    :return: none
    """
    global DEFAULT_YEAR
    global DEFAULT_LANGUAGE
    url = (f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1"
           f"&primary_release_year={DEFAULT_YEAR}&sort_by=vote_average.desc&vote_average.gte={VOTE_SCORE}"
           f"&vote_count.gte={VOTE_COUNT_THRESHOLD}&with_original_language={DEFAULT_LANGUAGE}")

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv('API_KEY')}"
    }

    response = requests.get(url, headers=headers)

    movies = response.json()

    # Displays search parameters and list of movies from API
    print(f"\nSearch query - Year: {DEFAULT_YEAR} Language: {DEFAULT_LANGUAGE} Vote Threshold: {VOTE_COUNT_THRESHOLD}"
          f" Rating: {VOTE_SCORE}\n")
    for index, movie in enumerate(movies["results"]):
        print(f"{index+1}. {movie['title']}")

    # Prompts user to add movies to watch list
    add_watch_list(user_name, movies["results"])


def get_movie(movie_id):
    """
    Retrieves a movie from The Movie Database API using TMDB ID number.

    :param movie_id:  integer TMDB ID
    :return: none
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv('API_KEY')}"
    }

    response = requests.get(url, headers=headers)

    return response.json()


def add_watch_list(user_name, movie_list):
    """
    Adds a movie to the watchlist for a given user.

    :param user_name: string name of current user
    :param movie_list: list of movies
    :return: none
    """
    print("Would you like to add any of these movies to your watchlist?")
    answer = input("Please input movie number or press enter to continue: ")
    while answer:
        store_movie(user_name, movie_list, int(answer)-1)
        print("Would you like to add another movie to your watchlist?")
        answer = input("Please input movie number or press enter to continue: ")


def store_movie(user_name, movie_list, movie_index):
    """
    Sends a store movie request to list microservice.

    :param user_name: string name of current user
    :param movie_list: list of movies
    :param movie_index: index of movie to store
    :return:
    """
    for index, movie in enumerate(movie_list):
        if index == movie_index:
            store_list(user_name, movie)


def intro():
    """
    Prints application ascii title

    :return: none
    """
    title = ("******************************************************************************\n"
             "* _    _      _                            _          _   _                  *\n"
             "*| |  | |    | |                          | |        | | | |                 *\n"
             "*| |  | | ___| | ___ ___  _ __ ___   ___  | |_ ___   | |_| |__   ___         *\n"
             "*| |/\\| |/ _ \\ |/ __/ _ \\| '_ ` _ \\ / _ \\ | __/ _ \\  | __| '_ \\ / _ \\        *\n"
             "*\\  /\\  /  __/ | (_| (_) | | | | | |  __/ | || (_) | | |_| | | |  __/        *\n"
             "* \\/  \\/ \\___|_|\\___\\___/|_| |_| |_|\\___|  \\__\\___/   \\__|_| |_|\\___|        *\n"
             "*                                                                            *\n"
             "*                                                                            *\n"
             "* _____            ___  ___           _       ______ _           _           *\n"
             "*|_   _|           |  \\/  |          (_)      |  ___(_)         | |          *\n"
             "*  | | ___  _ __   | .  . | _____   ___  ___  | |_   _ _ __   __| | ___ _ __ *\n"
             "*  | |/ _ \\| '_ \\  | |\\/| |/ _ \\ \\ / / |/ _ \\ |  _| | | '_ \\ / _` |/ _ \\ '__|*\n"
             "*  | | (_) | |_) | | |  | | (_) \\ V /| |  __/ | |   | | | | | (_| |  __/ |   *\n"
             "*  \\_/\\___/| .__/  \\_|  |_/\\___/ \\_/ |_|\\___| \\_|   |_|_| |_|\\__,_|\\___|_|   *\n"
             "*          | |                                                               *\n"
             "*          |_|                                                               *\n"
             "******************************************************************************\n")

    print(title)
    print("This application is intended to locate the best movies released in a given year\nand display "
          "them in order of popularity, so that you can work your way through\nall the top hits!\n")


def login():
    """
    Logs in already existing user or adds new user to user list.

    :return: name current user's name
    """
    name = input("What is your username?")
    print(f"Welcome, {name}! Your watch list has been loaded.")
    if name not in users:
        while True:
            user_id = random.randint(1, 1000)
            if user_id not in users.values():
                break
        users[name] = user_id

    return name


def define_search():
    """
    Displays the current enabled search options.

    :return: none
    """
    print("The following default search options are currently enabled:\n")
    num = 1
    for option in options:
        print(f"{num})  {option} - {DEFINITIONS[option]}")
        num += 1

    print("\nTo enable advanced search options input 'A' at the menu screen. Be advised that enabling custom\n"
          "search options could negatively impact the quality of search results. Options currently include\n"
          "Language selection and Vote threshold.\n")


def advanced_search():
    """
    Displays the advanced search option menu.

    :return: none
    """
    # Prints advanced options menu
    print("******************************************************************************")
    print("Advanced Search Options")
    num = 1
    for option in advanced_options:
        print(f"{num})  {option} - {DEFINITIONS[option]}")
        num += 1
    print("******************************************************************************\n")

    # Prompts users to enable menu options
    user_choice = True
    while user_choice:
        print("Input the number of the option you would like to enable or disable or hit enter to continue:")
        print(f"Currently enabled options {options}")
        user_choice = input()

        # Adds and removes options from currently enabled option list
        if user_choice:
            if advanced_options[int(user_choice) - 1] in options:
                options.remove(advanced_options[int(user_choice) - 1])
            else:
                options.append(advanced_options[int(user_choice) - 1])


def retrieve_watch_list(name):
    """
    Retrieves current user's watch list from microservice and prints watch list.

    :param name: string name of current user
    :return: none
    """
    # Creates a UDP socket to communicate with microservice
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        message = json.dumps({"user_ID": users[name]})

        sock.sendto(message.encode(), ('127.0.0.1', 12345))

        response, server = sock.recvfrom(1024)

        answer = response.decode().split()

        # Prints user's watch list to terminal
        if answer[0] == '"User':
            print("Watch list is empty.")
        else:
            print("Watch list:")
            for movie_id in ast.literal_eval(response.decode())["WATCH"]:
                print(get_movie(movie_id)["title"])
    finally:
        sock.close()


def store_list(name, movie):
    """
    Sends a store movie to watch list request to microservice for current user.

    :param name: string name of current user
    :param movie: int ID of movie
    :return: none
    """
    print(f"Adding {movie['title']} to your watch list.")

    # Creates a UDP socket to communicate with microservice
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        message = json.dumps({"user_ID": users[name], "LIST": 'WATCH', "movie_ID": movie['id']})

        sock.sendto(message.encode(), ('127.0.0.1', 12345))

        response, server = sock.recvfrom(1024)

        answer = response.decode().split()
    finally:
        sock.close()


def get_year():
    """
    Prompts for user input for search year parameter and updates global variable.

    :return: none
    """
    global DEFAULT_YEAR
    year = input("Please enter the year would you like to see the top movies from:")
    DEFAULT_YEAR = str(year)


def get_language():
    """
    Prompts for user input for search language parameter and updates global variable.

    :return: none
    """
    global DEFAULT_LANGUAGE
    print("Language options are in two letter language codes i.e. English-en, French-fr, Spanish-es")
    language = input("Please enter the language would you like to see the top movies from:")
    DEFAULT_LANGUAGE = language


def get_threshold():
    """
    Prompts for user input for search threshold parameter and updates global variable.

    :return: none
    """
    global VOTE_COUNT_THRESHOLD
    print("Input a positive integer for the user vote threshold for ratings or press enter to continue.")
    threshold = input("Please enter the vote threshold would you like to see the top movies starting from:")
    if threshold:
        VOTE_COUNT_THRESHOLD = threshold


def get_vote():
    """
    Prompts for user input for search vote score parameter and updates global variable.

    :return: none
    """
    global VOTE_SCORE
    print("Input a positive integer for the user score threshold for ratings or press enter to continue.")
    vote = input("Please enter the user score would you like to see the top movies starting from:")
    if vote:
        VOTE_SCORE = vote


def load_data():
    """
    Loads calorie data history from data.json file. Creates new file if one does not exist.

    :return: none
    """
    global users
    try:
        with open("data.json") as infile:
            users = json.load(infile)
    except FileNotFoundError:
        with open("data.json", "w") as outfile:
            json.dump({}, outfile)


def save_data():
    """
    Saves calorie history in data.json file.

    :return: none
    """
    global users
    with open("data.json", "w") as outfile:
        json.dump(users, outfile)


if __name__ == "__main__":
    load_data()
    main()
    save_data()
