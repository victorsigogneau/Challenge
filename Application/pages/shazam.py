import streamlit as st
from ShazamAPI import Shazam
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
from streamlit_extras.switch_page_button import switch_page


# Configuration de la page
st.set_page_config(page_title="shazam", initial_sidebar_state="collapsed")

if st.button("Accueil"):
    switch_page("accueil")

st.title("Reconnaissance de musique")

# Description de l'application
st.write("""
            La magie de reconnaître n'importe quelle chanson en quelques secondes et vous faire les meilleurs recommendations !
            """)

# Créer un bouton de chargement de fichier dans l'interface utilisateur
uploaded_file = st.file_uploader("Choisissez votre musique", type=['mp3'])

if uploaded_file is not None:
    # Lire le contenu du fichier MP3 téléchargé
    mp3_file_content_to_recognize = uploaded_file.read()

    shazam = Shazam(mp3_file_content_to_recognize)
    recognize_generator = shazam.recognizeSong()
    try:
        # Récupérer la première réponse de ShazamAPI
        a = next(recognize_generator)
        music_json = a[1]  # La réponse est un tuple où le second élément contient les données JSON

        # Extraire le titre et l'artiste du JSON
        titre = music_json['track']['title']
        artiste = music_json['track']['subtitle']

        # Key de Spotify
        client_id = 'b6d0752f35624904aa09b8ab4c06d5b1'
        client_secret = 'debdca7f8ec94ebf922263bfa071db9d'

        # Initialiser le gestionnaire de credentials client
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

        # Créer une instance Spotify
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # Recherchez une piste
        track_results = sp.search(q=f'track:{titre} artist:{artiste}', type='track', limit=1)

        # Obtenir l'ID de la piste
        track_id = track_results['tracks']['items'][0]['id']

        #st.write(f"Artiste: {track_id}")

        # Obtenir les détails de la piste, y compris les genres associés
        track_details = sp.track(track_id)

        # Obtenir les artistes associés à la piste
        artist_ids = [artist['id'] for artist in track_details['artists']]

        # Obtenir les détails des artistes
        artists_details = sp.artists(artist_ids)

        liste_genre = []
        artist_genres = {}

        # Récupérer les genres associés à chaque artiste
        for artist in artists_details['artists']:
            print(f"Genres de l'artiste {artist['name']}: {', '.join(artist['genres'])}")
            liste_genre.append(artist['genres'])

            # Construction du dictionnaire
            artist_genres[artist['name'].lower()] = artist['genres']
            
        # Conversion du dictionnaire en JSON string
        artist_genres_json = json.dumps(artist_genres, indent=4)

        st.write(artist_genres_json)


    except StopIteration:
        # Gérer le cas où ShazamAPI ne retourne pas de résultat
        st.error("Aucune correspondance trouvée pour ce fichier audio.")


st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)