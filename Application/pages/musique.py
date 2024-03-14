import streamlit as st
from PIL import Image
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json

class SpotifyAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.sp = self.authenticate_spotify()

    def authenticate_spotify(self):
        auth_manager = SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        return sp

    def get_artist_genres(self, artist_name):
        results = self.sp.search(q='artist:' + artist_name, type='artist')
        if results['artists']['items']:
            genres = results['artists']['items'][0]['genres']
            return genres
        else:
            return None
        
#initialisation spotify
spotify = SpotifyAPI(client_id='b6d0752f35624904aa09b8ab4c06d5b1', client_secret='debdca7f8ec94ebf922263bfa071db9d')

with open("./data.json", "r") as json_file:
    # Charge les données JSON depuis le fichier
    preferences = json.load(json_file)
    
# Récupérer les noms des artistes préférés (supposant qu'ils soient séparés par des virgules)
artistes = str(preferences['artistes_preferes']).split(', ')

# Parcourir chaque artiste et afficher les genres
for artiste in artistes:
    # Récupérer les données pour l'artiste spécifié
    resultats = spotify.get_artist_genres(artiste)
    
    # Imprimer les résultats
    st.text(f"Genres pour {artiste}: {resultats}")















# def afficher_info_musique(nom, titre, album):
#     st.write(f"Nom : {nom}")
#     st.write(f"Titre : {titre}")
#     st.write(f"Album : {album}")

# donnees_musiques = [
#     {"nom": "Musique 1", "titre": "Titre 1", "album": "Album 1", "image": "./image1.jpg"},
#     {"nom": "Musique 2", "titre": "Titre 2", "album": "Album 2", "image": "image2.jpg"},
#     {"nom": "Musique 3", "titre": "Titre 3", "album": "Album 3", "image": "image3.jpg"}
# ]

# # Interface utilisateur
# st.title("Sélection de musique")

# # Affichage des boutons avec des images
# for musique in donnees_musiques:
#     image = musique["image"]
#     nom = musique["nom"]
#     titre = musique["titre"]
#     album = musique["album"]
#     if st.button(f"Cliquez pour {nom}"):
#         afficher_info_musique(nom, titre, album)
#         st.image(image, caption=f"{titre} - {album}", use_column_width=True)
