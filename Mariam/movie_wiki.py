# TODO: load `wiki_movie_plots.json` from `input` folder
# Be careful : the file size is big so don't display it totally.


# TODO: write a function to select only British movies


# TODO: Save your python object in a new JSON file located in the `output`folder. 
import json

def main():
        def load_movie_list():
                with open("../input/wiki_movie_plots.json","r", encoding="utf-8") as fichier:
                        m = json.load(fichier)
                return m 

        def classify(o):
                fichier = load_movie_list()
                existe = False
                for film in fichier:
                        if film["Origin"]["Ethnicity"] == o:
                                print(film["Title"])
                                existe = True
                if not existe:
                        print(f"Aucun film dont l'origine est {o}")
        
        def save_movie_list(n):
                fichier = load_movie_list()
                fichier_dictionnaire =[]
                for film in fichier:
                        if film["Origin"]["Ethnicity"] == n:
                                fichier_dictionnaire.append(film)
                with open("../output/nouveau_fichier.json", "w", encoding="utf-8") as f:
                        json.dump(fichier_dictionnaire, f, ensure_ascii=False, indent=4)
        q = "British"
        movie = classify(q)
        nouveau_fichier = save_movie_list(q)

if __name__ == "__main__":
    main()