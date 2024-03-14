import streamlit as st
from streamlit_extras.switch_page_button import switch_page



st.set_page_config(page_title="accueil", initial_sidebar_state="collapsed")

st.title("Bienvenue sur notre app !")

# Description de l'application
st.write("""
        Préparez vos oreilles et ajustez vos enceintes, car notre projet va révolutionner votre playlist comme jamais auparavant! Oubliez le casse-tête de chercher la prochaine perle rare. 

Alors, êtes-vous prêts à laisser un algorithme décider de vos futurs coups de cœur musicaux ? Attention, risque élevé de devenir accro! 😊 
            """)

# Boutons pour naviguer vers d'autres pages
st.write("🤖 Besoin d'un ami virtuel ? Cliquez ici ! ")
if st.button("Chatbot"):
    switch_page("chatbot")

st.write("♫ Envie de swinguer ? Téléchargez vos rythmes préférés !")
if st.button("Shazam"):
    switch_page("shazam")


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
