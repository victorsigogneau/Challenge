import streamlit as st

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


import streamlit as st
from chatbotte import Chatbot  # Supposons que votre classe Chatbot est dans un fichier chatbot.py
from streamlit_extras.switch_page_button import switch_page

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
            json.dump(json_data, json_file)

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
