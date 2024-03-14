from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import HuggingFaceHub
import json

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
        prompt_template = """
        Voici un json je souhaite que tu me retourne uniquement le json
        Réorganise les valeurs des clés, sépare les quand il y a des virgules
        Le JSON doit être sur une seule ligne
        

        {query}

        Réponse:
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
