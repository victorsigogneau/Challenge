import streamlit as st

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import HuggingFaceHub
import json
import pickle
import spotipy
import pickle
from spotipy.oauth2 import SpotifyClientCredentials
import json
import pandas as pd
import numpy as np
import random

class Chatbot():
    def __init__(self,huggingfacehub_api_token):
        self.llm = HuggingFaceHub(repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", model_kwargs={"temperature": 0.1, "max_new_token": 500},huggingfacehub_api_token=huggingfacehub_api_token)
        self.huggingfacehub_api_token = huggingfacehub_api_token
        self.iteration = 1
        self.artiste = ''
        self.titre = ''
        self.json_raw = {}
        self.json_clean = {}

    # Prompt de base
    def make_prompt(self):
        prompt_template = """[INST]
        Voici un json je souhaite que tu me retourne uniquement le json
        Réorganise les valeurs des clés, sépare les quand il y a des virgules
        Le JSON doit être sur une seule ligne
        
        JSON1: 
        {"artistes_preferes": "Mozart, Shakira, DJ SNAKE", "titres_preferes": "rzerze et dazdazd"}
        JSON2: 
        {"artistes_preferes": ["Mozart", "Shakira", "DJ SNAKE"], "titres_preferes": ["rzerze", "dazdazd]"}


        JSON 1
        {query}
        [/INST]
        JSON2:
        """

        return prompt_template
    
    # Compte les itérations du chatbot
    def add_ite(self):
        self.iteration= self.iteration+1
    
    # Enregistre les réponses
    def save_answer(self, ans):
        if self.iteration==1:
            self.artiste= ans
        elif self.iteration==2:
            self.titre = ans

    # dada
    def save_json_raw(self):
        data = {
            "artistes_preferes": self.artiste,
            "titres_preferes": self.titre
        }
        json_data = json.dumps(data)  # Convertir le dictionnaire en chaîne JSON
        self.json_raw = json_data

    #get json clean
    def get_json_clean(self):
        return self.json_clean

    # Genere les réponses 
    def generate_response(self, query):
        if self.iteration==0:
            answer='Quels sont vos artistes préférés ?'
            self.add_ite()
        elif self.iteration==1:
            self.save_answer(query)
            self.add_ite()
            answer='Quels sont vos titres préférés ?'

        elif self.iteration==2:
            self.save_answer(query)
            self.save_json_raw()
            promp_rag = PromptTemplate(input_variables=["query"], template=self.make_prompt())
            chain = LLMChain(prompt=promp_rag, llm=self.llm)
            response = chain.invoke({"query": self.json_raw})
            answer = response["text"].split("Réponse:")[1]
            debut_json = answer.find('{')
            json_texte = answer[debut_json:]
            answer = json.loads(json_texte)
            self.json_clean = answer
            answer = 'Vous pouvez observer les resultats dans un autre onglet'
            self.add_ite()
        else:
            answer = 'Vous nous avez deja partagé vos artistes et titres préférés, nous vous remercions pour votre confiance !'
        return answer

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
    

import streamlit as st
from chatbotte import Chatbot  # Supposons que votre classe Chatbot est dans un fichier chatbot.py
from streamlit_extras.switch_page_button import switch_page

passer= False
# Configuration de la page
st.set_page_config(page_title="chatbot", initial_sidebar_state="collapsed")

if st.button("Accueil"):
    switch_page("accueil")

huggingfacehub_api_token = "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"

@st.cache_resource
def load_chatbot():
    return Chatbot(huggingfacehub_api_token)

chatbot = load_chatbot()

st.title("🎶 Quels sont vos goûts musicaux ?")
st.caption("❓ Vous ne savez pas quoi écouté ? Demandez à notre chatbot ! 🤖")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Quels sont vos artistes préférés ?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"],avatar='./avatar_bot.png').write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = chatbot.generate_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant",avatar='./avatar_bot.png').write(response)
    if response =='Vous pouvez observer les resultats dans un autre onglet':
        json_data = chatbot.get_json_clean()
        with open("./data.json", "w") as json_file:
            json.dump(json_data, json_file, ensure_ascii=False)
        
        # Exemple d'utilisation
        fichier1 = "data_brute.json"
        fichier2 = "data.json"
        json_a_traiter = fusionner_json(fichier1, fichier2)
        
        passer =True
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
