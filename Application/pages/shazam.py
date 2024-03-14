import streamlit as st
from ShazamAPI import Shazam
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
from streamlit_extras.switch_page_button import switch_page
import json
import pickle
import spotipy
import pickle
from spotipy.oauth2 import SpotifyClientCredentials
import json
import pandas as pd
import numpy as np
import random

def fusionner_json(fichier1, fichier2):
    # Chargement des données JSON
    with open(fichier1, 'r') as f:
        data1 = json.load(f)
    with open(fichier2, 'r') as f:
        data2 = json.load(f)
    data_fusionnee = fusionner_dictionnaires(data1, data2)
    return data_fusionnee

def fusionner_dictionnaires(d1, d2):
    for key, value in d2.items():
        if key in d1:
            if isinstance(value, dict) and isinstance(d1[key], dict):
                fusionner_dictionnaires(d1[key], value)
            elif isinstance(value, list) and isinstance(d1[key], list):
                d1[key].extend(value)
            else:
                pass
        else:
            d1[key] = value
    return d1

def load_data_and_classify(json_filename, nombre_derniers_artistes=5):
    # Charger les données JSON
    with open(json_filename, 'r') as json_file:
        data = json.load(json_file)
    
    artistes_preferes = data['artistes_preferes']
    genres_artistes = {}
    

    # Obtenir les genres pour chaque artiste
    for artiste in artistes_preferes:
        if artiste in genres_artistes:
            # Si l'artiste existe déjà, le retirer de la liste pour le réinsérer à la fin
            genres = genres_artistes.pop(artiste)
            if genres is None:
                genres = ""
            genres_artistes[artiste] = genres
        else:
            genres = get_artist_genres(artiste)
            if genres is None:
                genres = ""
            genres_artistes[artiste] = genres
    
    # Charger le dataframe brut à partir du fichier CSV
    df_brute = pd.read_csv('database.csv', index_col=0)
    available_genres = list(df_brute.columns)
    

    # Créer une DataFrame pour stocker les données binaires
    binary_data = pd.DataFrame(index=genres_artistes.keys(), columns=available_genres)
    binary_data = binary_data.fillna(0)

    # Remplir les données binaires
    for artiste, genres in genres_artistes.items():
        for genre in genres:
            if genre.lower() in binary_data.columns:
                binary_data.loc[artiste, genre.lower()] = 1
    
    
    # Charger les modèles sauvegardés
    # Initialiser le dictionnaire model_save
    model_save = {'etape0': [], 'etape1': [], 'etape2': []}
    # Charger les fichiers pickle et stocker dans model_save
    with open('Piickle/pca.pickle', 'rb') as f:
        model_save['etape0'].append(pickle.load(f))

    with open('Piickle/Kmeans1.pickle', 'rb') as f:
        model_save['etape1'].append(pickle.load(f))

    with open('Piickle/Kmeans_c1.pickle', 'rb') as f:
        model_save['etape2'].append(pickle.load(f))

    with open('Piickle/Kmeans_c2.pickle', 'rb') as f:
        model_save['etape2'].append(pickle.load(f))

    with open('Piickle/Kmeans_c3.pickle', 'rb') as f:
        model_save['etape2'].append(pickle.load(f))
    
    # Transformation PCA
    step_1 = model_save['etape0'][0]
    data_pca = step_1.transform(binary_data)
    data_pca = pd.DataFrame(data_pca)
    
    # Prédiction du premier cluster
    step_2 = model_save['etape1'][0]
    cluster_step1 = step_2.predict(data_pca)
    
    # Renommer les colonnes
    data_pca.rename(columns={0: 'PC1', 1: 'PC2'}, inplace=True)
    data_pca['Clusters'] = 22
    
    # Prédiction des classes finales
    for i in range(binary_data.shape[0]):
        step_3 = model_save['etape2'][cluster_step1[i]]
        data_pca.iloc[i, 2] = cluster_step1[i]
        data_pca.rename(columns={0: 'PC1', 1: 'PC2'}, inplace=True)
        data_pca_reshaped = data_pca.loc[i].values.reshape(1, -1)
        classe_finale = step_3.predict(data_pca_reshaped)
        
    # Charger les données des voisins les plus proches
    neighbors_data_last_five = {}

    last_indices = range(binary_data.shape[0]-nombre_derniers_artistes, binary_data.shape[0])  # Indices des dernières lignes

    for i in last_indices:
        step_3 = model_save['etape2'][cluster_step1[i]]
        data_pca.iloc[i, 2] = cluster_step1[i]
        data_pca_reshaped = data_pca.loc[i].values.reshape(1, -1)
        classe_finale = step_3.predict(data_pca_reshaped)

        # Obtenir les indices des points dans la classe prédite
        class_indices = np.where(cluster_step1 == classe_finale)[0]

        # Sélectionner aléatoirement cinq individus du cluster
        random_cluster_members = select_random_cluster_members(class_indices, i)

        # Stocker les indices des cinq individus aléatoires dans le dictionnaire
        neighbors_data_last_five[i] = random_cluster_members

    # Retourner le vecteur de classe
    return neighbors_data_last_five, binary_data

def select_random_cluster_members(cluster_indices, current_index, n=5):
    # Exclure l'indice de l'élément actuel
    cluster_indices = [index for index in cluster_indices if index != current_index]
    # Sélectionner aléatoirement n individus du cluster
    random_members = random.sample(cluster_indices, min(n, len(cluster_indices)))
    return random_members

def get_artist_genres(artist_name):
    results = sp.search(q='artist:' + artist_name, type='artist')
    if results['artists']['items']:
        genres = results['artists']['items'][0]['genres']
        return genres
    else:
        return None
    

passer=False

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


        # Création du dictionnaire avec les données
        donnees = {
            "artistes_preferes": [artiste],
            "titres_preferes": [titre]
        }

        # Enregistrement dans un fichier JSON
        with open('data.json', 'w', encoding='utf-8') as fichier:
            json.dump(donnees, fichier, ensure_ascii=False, indent=4)


        ##########
        ## PARTIE VICTOR
        #########

        passer=True
        # Exemple d'utilisation
        fichier1 = "data_brute.json"
        fichier2 = "data.json"
        json_a_traiter = fusionner_json(fichier1, fichier2)
        
        pd.set_option('display.max_columns', None)
        client_id = 'b6d0752f35624904aa09b8ab4c06d5b1'
        client_secret = 'debdca7f8ec94ebf922263bfa071db9d'

        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        #sauvegarder json
        with open("json_a_traiter.json", 'w') as f:
            json.dump(json_a_traiter, f, ensure_ascii=False)
        
        recommandationn ={'artiste_aime':[],'recommandation':[]}

        fichier2 = "data.json"
        with open(fichier2, 'r') as f:
            data1 = json.load(f)
        nombre_artiste = len(data1['artistes_preferes'])


        neighbors_indices, dataframe_inde = load_data_and_classify('json_a_traiter.json', nombre_derniers_artistes=nombre_artiste)
        dataframe_inde['index_artiste'] = range(len(dataframe_inde))

        for prems, artiste in neighbors_indices.items():
            artiste_aime = dataframe_inde['index_artiste'].index[prems]
            recommandation = dataframe_inde['index_artiste'].index[artiste].tolist()
            print(artiste_aime)
            print(recommandation)
            recommandationn['artiste_aime'].append(artiste_aime)
            recommandationn['recommandation'].append(recommandation)
        with open("recommandation.json", "w") as fichier_json:
            json.dump(recommandationn, fichier_json, ensure_ascii=False)

        ######
        # fin victor
        ####
            
        #st.write(recommandationn)


    except StopIteration:
        # Gérer le cas où ShazamAPI ne retourne pas de résultat
        st.error("Aucune correspondance trouvée pour ce fichier audio.")


if st.button('Recommandation') and passer ==True:
    switch_page("recommandation")

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


