import json
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import requests

# Charger le fichier recommandation.json
with open('C:/Users/ndieng1/Documents/Challenge-IA/Challenge-main/Application/recommandation.json', 'r') as file:
    recommendation_data = json.load(file)

# Initialiser l'API Spotify
client_credentials_manager = SpotifyClientCredentials(client_id='b6d0752f35624904aa09b8ab4c06d5b1', client_secret='debdca7f8ec94ebf922263bfa071db9d')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Dictionnaire pour stocker les informations de base des chansons
songs_info = defaultdict(list)

# Fonction pour obtenir les informations de base d'une chanson (titre et nom de l'artiste)
def get_song_info(song_name, artist_name):
    return song_name, artist_name

# Parcours de chaque artiste recommandé
for artists_list in recommendation_data["recommandation"]:
    for artist_name in artists_list:
        # Recherche des 5 meilleures chansons de l'artiste via l'API Spotify
        results = sp.search(q='artist:' + artist_name, type='track', limit=5)
        
        # Liste pour stocker les informations de base des chansons de l'artiste
        artist_songs_info = []
        
        # Parcours de chaque chanson
        for track in results['tracks']['items']:
            song_name = track['name']
            # Obtention des informations de base de la chanson
            song_info = get_song_info(song_name, artist_name)
            # Stockage des informations de base dans la liste de l'artiste
            artist_songs_info.append(song_info)
        
        # Stockage de la liste des chansons de l'artiste dans le dictionnaire principal
        songs_info[artist_name].extend(artist_songs_info)

# Calculer la similarité entre les chansons en utilisant les informations de base
def calculate_similarity(song_info_dict):
    # Concaténer les informations de base de chaque chanson pour chaque artiste
    concatenated_info = [" ".join([song[0], song[1]]) for songs in song_info_dict.values() for song in songs]
    
    # Vectoriser les informations de base des chansons
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(concatenated_info)
    
    # Calculer la similarité cosinus entre les chansons
    similarity_matrix = cosine_similarity(vectors)
    
    return similarity_matrix

# Calculer la similarité entre les chansons en utilisant les informations de base
similarity_matrix = calculate_similarity(songs_info)


# Trouver les trois chansons les plus similaires pour chaque chanson
top_similar_songs = defaultdict(list)
for artist, songs_info_list in songs_info.items():
    for song_info in songs_info_list:
        # Trouver l'indice de la chanson dans le dictionnaire
        i = list(songs_info.keys()).index(artist)
        # Exclure la similarité de la chanson avec elle-même
        similarities = [(songs_info_list[j], similarity_matrix[i][j]) for j in range(len(songs_info_list)) if i != j]
        # Trier par similarité décroissante et sélectionner les trois premières chansons
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_similar_songs[song_info].extend(similar_info[0] for similar_info in similarities[:3])

# Afficher les résultats
st.title("Top 3 des chansons les plus similaires :")
for song_info, similar_songs in top_similar_songs.items():
    song_name, artist_name = song_info
    st.subheader(f"Chanson : {song_name} (Artiste : {artist_name})")
    for similar_song_info in similar_songs:
        similar_song_name, similar_artist_name = similar_song_info
        st.write(f"- Chanson similaire : {similar_song_name} (Artiste : {similar_artist_name})")