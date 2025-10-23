import json

def load():
    with open ("../input/wiki_movie_plots.json", "r", encoding="utf-8") as f:
        return json.load(f)
    

def classify(movies, origin):
    return [m for m in movies if m.get("Origin").get("Ethnicity") == origin ]

def save(movies):
    with open ("../output/british_movies.json","w",encoding="utf-8") as f:
        json.dump(movies, f)

def main():
    movies=load()
    british_movies=classify(movies, "British")
    save(british_movies)

if __name__ == "__main__":
    main()


    
