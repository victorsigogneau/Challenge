import streamlit as st
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from streamlit_extras.switch_page_button import switch_page
# Initialisation de l'API Spotify

# Initialisation de l'API Spotify
client_credentials_manager = SpotifyClientCredentials(client_id='b6d0752f35624904aa09b8ab4c06d5b1', client_secret='debdca7f8ec94ebf922263bfa071db9d')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Configuration de la page
st.set_page_config(page_title="shazam", initial_sidebar_state="collapsed")

if st.button("Accueil"):
    switch_page("accueil")

if st.button("Voir les sons recommandés"):
    switch_page("Similarité")

# Charger les données JSON
with open('recommandation.json', 'r') as file:
    data = json.load(file)
# Interface utilisateur

# Interface utilisateur
st.title("Système de recommandation d'artistes")

# Sélection de l'artiste
selected_artist = st.selectbox("Sélectionnez un artiste :", data['artiste_aime'])

# Trouver les recommandations pour l'artiste sélectionné
artist_index = data['artiste_aime'].index(selected_artist)
recommendations = data['recommandation'][artist_index]

# Afficher les recommandations
if recommendations:
    st.subheader("Recommandations :")
    for recommendation in recommendations:
        # Recherche de l'artiste dans l'API Spotify
        artist_info = sp.search(q=recommendation, type='artist', limit=1)
        if artist_info['artists']['items']:
            artist = artist_info['artists']['items'][0]
            # Afficher le nom de l'artiste
            st.write(f"Nom de l'artiste : {artist['name']}")
            # Afficher l'image de l'artiste s'il y en a
            if artist['images']:
                st.image(artist['images'][0]['url'], caption=f"Image de {artist['name']}")
            else:
                st.write("Aucune image disponible pour cet artiste.")
            # Afficher le profil Spotify de l'artiste s'il existe
            if artist['external_urls'] and 'spotify' in artist['external_urls']:
                st.write(f"Profil Spotify : [{artist['name']}]({artist['external_urls']['spotify']})")
            else:
                st.write("Aucun profil Spotify disponible pour cet artiste.")
            
            # Obtenir les top 5 chansons de l'artiste
            top_tracks = sp.artist_top_tracks(artist['id'], country='US')['tracks']
            if top_tracks:
                st.subheader("Top 5 des chansons :")
                for track in top_tracks[:5]:
                    st.write(f"- {track['name']} ({track['album']['name']})")
                    # Ajouter l'extrait de prévisualisation de la chanson
                    if track['preview_url']:
                        st.audio(track['preview_url'], format='audio/ogg', start_time=0)
                    else:
                        st.write("Aucun extrait de prévisualisation disponible pour cette chanson.")
            else:
                st.write("Aucune chanson populaire disponible pour cet artiste.")
else:
    st.write("Aucune recommandation disponible pour cet artiste.")


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
