import streamlit as st
from streamlit_extras.switch_page_button import switch_page



st.set_page_config(page_title="accueil", initial_sidebar_state="collapsed")

st.title("Bienvenue sur notre app !")

# Description de l'application
st.write("""
        Préparez vos oreilles et ajustez vos enceintes, car notre projet va révolutionner votre playlist comme jamais auparavant ! Oubliez le casse-tête de chercher la prochaine perle rare. 

Alors, êtes-vous prêts à laisser un algorithme décider de vos futurs coups de cœur musicaux ? Attention, risque élevé de devenir accro ! 😊 
            """)


st.markdown('''
&nbsp;
''', unsafe_allow_html=True)


# Create two columns with equal width
col1, col2 = st.columns(2)


from PIL import Image
hauteur_cible1 = 123
hauteur_cible2 = 100


############## COL1
# Boutons pour naviguer vers d'autres pages
col1.write("🤖 Besoin d'un ami virtuel ? Cliquez ici ! ")

# Charger l'image avec PIL
image1 = Image.open("chatbot.jpeg")

# Calculer le nouveau rapport de hauteur tout en conservant le rapport aspect
rapport1 = hauteur_cible1 / image1.height
largeur_cible1 = int(image1.width * rapport1)

# Redimensionner l'image
image_redimensionnee1 = image1.resize((largeur_cible1, hauteur_cible1))

# Afficher l'image redimensionnée
col1.image(image_redimensionnee1)
if col1.button("Chatbot"):
    switch_page("chatbot")


    
############## COL2
col2.write("♫ Envie de swinguer ? Téléchargez vos rythmes préférés !")

# Charger l'image avec PIL
image2 = Image.open("shazam.png")

# Calculer le nouveau rapport de hauteur tout en conservant le rapport aspect
rapport2 = hauteur_cible2 / image2.height
largeur_cible2 = int(image2.width * rapport2)

# Redimensionner l'image
image_redimensionnee2 = image2.resize((largeur_cible2, hauteur_cible2))

# Afficher l'image redimensionnée
col2.image(image_redimensionnee2)
if col2.button("Shazam"):
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
