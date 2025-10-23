## TODO: load `wiki_movie_plots.json` from `input` folder
# Be careful : the file size is big so don't display it totally.


# TODO: write a function to select only British movies


# TODO: Save your python object in a new JSON file located in the `output`folder. 

import json


def load_movie_list():
    with open("../input/wiki_movie_plots.json", "r", encoding="utf-8") as file:
        return json.load(file)

       

def classify(movies, origin="British"):
    return [movie for movie in movies if movie.get("Origin").get("Ethnicity") == origin]


def save_movie_list(movies):
    with open("../output/british_movies.json", "w", encoding="utf-8") as f:
        json.dump(movies, f)

def main():
    movies = load_movie_list()
    british_movies = classify(movies, "British")
    save_movie_list(british_movies)
    print(f"{len(british_movies)} films britanniques sauvegardés dans '../output/british_movies.json'")

if __name__ == "__main__":
    main()