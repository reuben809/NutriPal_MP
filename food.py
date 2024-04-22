import langchain
import streamlit as st
from streamlit_lottie import st_lottie 
import secrets
from pymongo import MongoClient
# from dotenv import load_dotenv
import os
import getpass
import base64
import time
import json
import requests


from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Qdrant
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.schema.document import Document
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.llms import HuggingFaceEndpoint


from transformers import pipeline


# load_dotenv()


st.set_page_config(
    page_title="Kalpana Project Phase",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

no_sidebar_style = """
    <style>
        div[data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(no_sidebar_style, unsafe_allow_html=True)


st.title(' :red[NutriPal] - Your AI-Powered Nutrition Coach')

mongo_key = st.secrets['mongokey']


@st.cache_resource
def init_mongo_connection():
    connection_string = f"mongodb+srv://atifshaik538:{mongo_key}@nutripalcluster.vq56uyq.mongodb.net/?retryWrites=true&w=majority&appName=nutripalcluster"
    return MongoClient(connection_string)


client = init_mongo_connection()

db = client.nutripaldb 
collection = db.nutripalcluster
st.session_state['collection'] = collection

url = requests.get( 
    "https://lottie.host/3675d60a-37e0-4c26-8476-e662a4067e08/9juUlYZEnf.json") 

url_json = dict() 
  
if url.status_code == 200: 
    url_json = url.json() 
else: 
   st.sidebar.error('Error in generating animations')

with st.sidebar:
    st_lottie(url_json, speed=2, height=200, quality='high', width=190)


def generate_user_id():
    random_bytes = secrets.token_bytes(nbytes=16)
    user_id = random_bytes.hex() 
    return user_id


def log_sign(user):
    if user == 'Login':
        st.write('Login Page')
        username_log = st.text_input('Username')
        password_log = st.text_input('Password', type='password')
        if st.button('Login') and username_log and password_log:
            if collection.find_one({"Username":username_log, "Password":password_log}):
                st.success('Login Successful')
                st.session_state['logged'] = username_log+'isloggedin'
                st.rerun()

            else:
                st.error('Invalid Credentials/No User found')
                return
            
    else:
        st.write('Signup Page')
        email = st.text_input('Email')
        username_sign = st.text_input('Username')
        password1 = st.text_input('Password', type='password')
        password2 = st.text_input('Confirm Password', type='password')

        if password1 != password2:
            st.write('Passwords do not match')

        elif email=='' or username_sign=='' or password1=='' or password2=='':
            st.write('Please fill all the fields')

        elif st.button('Signup') and password1==password2 and username_sign and email:
            if collection.find_one({"Username":username_sign}):
                st.error('Username already exists. Please choose another one.')
                return
                
            unique_user_id = generate_user_id()
            info_to_insert = {"ID":unique_user_id, "Email":email, "Username":username_sign, "Password":password1, "history":"", "food_history":""}

            try:
                collection.insert_one(info_to_insert)
                st.success('Signup Successful! Please login to continue.')

            except Exception as e:
                st.error('Something went wrong. Please try again.')
                print(e)
                return


@st.cache_resource
def load_img_cls_model(image):
    pipe = pipeline("image-classification", model="Kaludi/food-category-classification-v2.0")
    img_classify = pipe(image)
    return img_classify

    

def nutripalpage():
    img = st.file_uploader('Upload Your Image', type=['jpg', 'jpeg', 'png'])
    toggle = st.toggle('Proceed without image')
    ingredients = []
    if img is not None or toggle:
        if img is not None:
            img_data = img.read()
            base64_encoded_img = base64.b64encode(img_data).decode("utf-8")
            st.image(img_data, width=400)
            img_classify = load_img_cls_model(base64_encoded_img)
            # st.write('Ingredients Found', '\n')
            st.markdown(f"<h4 style='text-align: center; color:#15db4d'><b>Ingredients Found</b></h4>", unsafe_allow_html=True)
            i = 1

            for ing in img_classify:
                st.text(f"{i}- {ing['label']}")
                ingredients.append(ing['label'])
                i+=1

        st.markdown("<hr>", unsafe_allow_html=True)

        user_health = st.text_input("Before we dive into the culinary symphony, let's address any hidden challenges in your health or daily life. Unveiling these could unlock the perfect recipe for well-being. Any health concerns we should consider before we begin?", placeholder="I am experiencing mild fever, sinus issues, and difficulty sleeping.")
        kitchen_ingredients = st.text_input('Want to add some ingredients you found in your kitchen to your recipe?', placeholder="In my kitchen, I have ripe tomatoes, fresh basil, garlic cloves, olive oil, chicken breast")

        # don't forget to ask user preferences what he likes and dislikes
        
        st.write("")
        water_footprint = st.checkbox("Want to reduce Water Footprint")
        st.expander("What is Water Footprint?", expanded=water_footprint).write("The water footprint of a product is the volume of freshwater used to produce the product, measured at the place where the product was actually produced. It is a measure of the direct and indirect water use along the entire supply chain of a product.")
        
        ignore_health = st.checkbox("Want to only focus on Environmental friendly dish by ignoring your Health ?")

        col1, col2, col3 = st.columns(3)

        with col2:
            dish = st.button('Generate Dish')

        if dish:
            st.text('Preparing dish...')
            if user_health:
                existing_history = collection.find_one({"Username": st.session_state['logged'].split('isloggedin')[0]})["history"]
                new_history = existing_history + ".\n" + user_health
                filter_= {"Username":st.session_state['logged'].split('isloggedin')[0]}
                update = {"$set": {"history": new_history}}
                collection.update_one(filter_, update)

            existing_history = collection.find_one({"Username":st.session_state['logged'].split('isloggedin')[0]})

            def get_text_chunks_langchain(text):
                text_splitter = CharacterTextSplitter(chunk_size=50, chunk_overlap=20)
                docs = [Document(page_content=x) for x in text_splitter.split_text(text)]
                return docs
            

            docs = get_text_chunks_langchain(existing_history["history"])

            # embeddings = HuggingFaceEmbeddings()
            # embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key="")
            embeddings = HuggingFaceInferenceAPIEmbeddings(api_key=st.session_state['apikey'] , model_name="sentence-transformers/all-MiniLM-l6-v2")


            qdrant = Qdrant.from_documents(
                docs,
                embeddings,
                location=":memory:",
                collection_name="my_documents",
            )

            llm_mistral = HuggingFaceEndpoint(
                repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", max_length=1024, temperature=0.5, huggingfacehub_api_token=st.session_state['apikey'] 
            )

            qa = RetrievalQA.from_chain_type(
                llm=llm_mistral,
                chain_type="stuff",
                retriever=qdrant.as_retriever()
            )

            # st.text('Preparing dish...')

            if not ignore_health and not water_footprint:
                prompt = f"""
                Create a detailed recipe using all available ingredients, considering my health conditions as a top priority. Ensure that the dish not only includes all ingredients but also contributes positively to my well-being in line with my health objectives.

                AVAILABLE INGREDIENTS: {kitchen_ingredients} {' '.join(ingredients)}.

                MY HEALTH: {existing_history['history']}.

                Please craft a recipe with the available ingredients. If any ingredients might be harmful due to my health conditions, please indicate so and skip them. You have the freedom to remove any harmful ingredients and adjust the recipe accordingly. Additionally, feel free to incorporate ingredients that could benefit my health, but kindly specify them before providing the recipe instructions.

                In case there isn't enough information, please create a generalized method for ingredients and health condition and try to give a generalized recepie.

                \n Before Giving Recipe do give me a list of selected ingredients, rejected ingredients and additional ingredients. Also Give a catchy DISH name !
                """

            elif water_footprint and not ignore_health:
                prompt = f"""
                        AVAILABLE INGREDIENTS: {kitchen_ingredients} {' '.join(ingredients)}.\n
                        MY HEALTH: {existing_history['history']}.\n  

                        Use the available ingredients to create a recipe that not only aligns with my health objectives but also has a low water footprint. 
                        Please ensure that the dish is not only healthy but also environmentally friendly. 
                        If any ingredients have a high water footprint, please avoid them, even if it's beneficial for my health history. 
                        You have the freedom to remove any high water footprint consuming ingredients and adjust the recipe accordingly. 
                        Additionally, feel free to incorporate ingredients that could benefit my health as well as it has low water footprint, 
                        but kindly specify them before providing the recipe instructions.\n

                        If you wanna do trade off between health and water footprint, "Choose Water Footprint" and specify the trade off and the reason for the trade off.    

                """
                st.info('Generated dish might not be fully beneficial for health, but it will be beneficial for the environment')


            else:
                prompt = f"""
                        AVAILABLE INGREDIENTS: {kitchen_ingredients} {' '.join(ingredients)}.\n

                        Use the available ingredients to create a recipe that has a low water footprint. 
                        Please ensure that the dish is highly environmentally friendly. 
                        If any ingredients have a high water footprint, please avoid them. 
                        You have the freedom to remove any high water footprint consuming ingredients and adjust the recipe accordingly. 
                        Additionally, feel free to incorporate ingredients that could benefit Environment if it has low water footprint, 
                        but kindly specify them before providing the recipe instructions.\n
                        Additionally before giving me recipe do give me a list of rejected ingredients and reason for it!
                """
                st.info('Generated dish will be Eco-Friendly')

            # st.text(prompt)
            prepared_dish = qa.run(prompt)
            # st.text(prompt)
            st.write('')
            st.write('')
            st.markdown(prepared_dish, unsafe_allow_html = True)
            st.session_state['recepie'] = prepared_dish



st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")

# st.sidebar.markdown("<hr>", unsafe_allow_html=True)
user_choice = st.sidebar.selectbox("**Login/Signup**", ['Login', 'Signup'])
# st.sidebar.markdown("<hr>", unsafe_allow_html=True)
if 'logged' not in st.session_state:
    log_sign(user_choice)


# with st.sidebar.popover('Enter HuggingFace API key', help='Authentication Required'):
#     openai_key = st.text_input('API Key', type='password')
#     if openai_key:
#         st.session_state['apikey'] = openai_key
hugapikey = st.secrets['huggingfaceapikey']
st.session_state['apikey'] = hugapikey


st.sidebar.markdown("<hr>", unsafe_allow_html=True)

st.sidebar.page_link("pages/next_food.py", label="Predict next Food", icon="🍜")
st.sidebar.page_link("pages/nutrition.py", label="Get Nutritional Info", icon="📊")



if 'apikey' in st.session_state and 'logged' not in st.session_state:
    placeholder = st.empty()
    start_time = time.time()
    while (time.time() - start_time) < 2:
        placeholder.info('**Please Login to get personalized recommendation**', icon="🔑")

    placeholder.empty()


if 'apikey' in st.session_state and 'logged' in st.session_state:
    nutripalpage()



