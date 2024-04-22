import streamlit as st
from streamlit_lottie import st_lottie 
import requests
from langchain_community.llms import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


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
st.subheader(' :violet[Get Nutritional Information of Recipe and food items]')


url = requests.get( 
    "https://lottie.host/d6fdfdb9-44d5-45de-bc54-9c92bc8f628f/J3YHSrJGMT.json") 

url_json = dict() 
  
if url.status_code == 200: 
    url_json = url.json() 
else: 
   st.sidebar.error('Error in generating animations')

with st.sidebar:
    st_lottie(url_json, speed=2, height=200, quality='high', width=190)


st.sidebar.markdown("<hr>", unsafe_allow_html=True)


@st.cache_resource
def get_recepie(data):
    template = """INGREDIENTS AND INSTRUCTIONS: {ing_nd_ins}.
                \n You are given with ingredients and instructions. 
                \n Additionally feel free to add or remove any ingredient if it alligns with the instructions, but kindly specify a reason before you add or remove ingredients.
                \n Create a detailed recipe using all the ingredients given and strictly follow the instructions given while creating a recipe."""

    repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"

    prompt = PromptTemplate(input_variables=["ing_nd_ins"], template=template)
    final_prompt = prompt.format(ing_nd_ins = data)

    llm = HuggingFaceEndpoint(
        repo_id=repo_id, max_length=1024, temperature=0.5, huggingfacehub_api_token=st.session_state['apikey']
    )

    return llm(final_prompt)



@st.cache_resource
def nut_ask_llm(data):
    template2 = """
            RECIPE: {nutritional}.
            \nYou've been provided with a recipe for a dish. Your task is to extract key nutritional information from the given recipe.

            Extract the amounts of proteins, carbohydrates, and fat content present in the provided recipe.

            Note that you are not allowed to add or remove any ingredients from the recipe, nor manipulate the preparation steps.

            Additionally, extract all the vitamins and minerals content from the recipe.

            Your output should be:
            - Amounts of protein content present in the recipe.
            - Amounts of carbohydrate content present in the recipe.
            - Amounts of fat content present in the recipe.
            - Amounts of vitamins and minerals content present in the recipe.
            - Total calorie content

            Ensure that all nutritional information is accurately calculated and presented.\n
            Output should only be Nutritional content as specified above, \n don't include Instructions and Ingredients in Output
            
            EXAMPLE OF HOW OUTPUT SHOULD LOOK LIKE:
            Ingredients:
        - Beef steak (1 piece, around 200g)
        - Olive oil (1 tbsp)
        - Mozzarella cheese (100g)
        - Apple (1 medium-sized)

        Protein content:
        The beef steak weighs around 200g, and an average beef steak contains around 25g of protein per 100g. So, the protein content in this recipe is around 50g.

        The Mozzarella cheese weighs 100g, and an average mozzarella cheese contains around 12g of protein per 100g. So, the protein content from the cheese is around 12g.

        Total protein content: 50g + 12g = 62g

        Carbohydrate content:
        An average medium-sized apple contains around 25g of carbohydrates.

        Total carbohydrate content: 25g

        Fat content:
        An average olive oil tablespoon contains around 14g of fat.

        The beef steak weighs around 200g, and an average beef steak contains around 8g of fat per 100g. So, the fat content from the beef is around 16g.

        The Mozzarella cheese weighs 100g, and an average mozzarella cheese contains around 8g of fat per 100g. So, the fat content from the cheese is around 8g.

        Total fat content: 14g + 16g + 8g = 38g

        Vitamins and minerals content:
        Beef steak is rich in various vitamins and minerals, including vitamin B12, iron, zinc, and selenium.

        Apple is a good source of vitamin C, fiber, and various B vitamins.

        Olive oil contains monounsaturated fatty acids, vitamin E, and antioxidants.

        Mozzarella cheese is a good source of calcium and vitamin D.
        
        This is just an example change it according to recipe"""

    prompt2 = PromptTemplate(input_variables=["nutritional"], template=template2)

    final_prompt2 = prompt2.format(nutritional=data)

    repo_id2 = "mistralai/Mixtral-8x7B-Instruct-v0.1"

    llm2 = HuggingFaceEndpoint(
        repo_id=repo_id2, max_length=1024, temperature=0.5, huggingfacehub_api_token=st.session_state['apikey']
    )

    return llm2(final_prompt2)



st.markdown("<hr>", unsafe_allow_html=True)


co1, co2, co3 = st.columns(3)

with co2:
    ask_user = st.toggle('Use already created recipe')

st.markdown("<hr>", unsafe_allow_html=True)


if ask_user:
    if 'recepie' in st.session_state:
        nutritional_info = nut_ask_llm(st.session_state['recepie'])
        st.markdown(nutritional_info, unsafe_allow_html=True)

    else:
        st.error('No recipe found. Please create a recipe first from home page')


else:
    nut_ingredients = st.text_input("Enter the ingredients of the recipe")
    nut_instruction = st.text_area("Enter any kind of additional info you wanna add about the recipe")

    nut_button = st.button("Prepare Dish")

    if nut_button and 'apikey' in st.session_state:
        st.write('Cooking your recipe...')
        ins_ing = 'INGREDIENTS :'+nut_ingredients+'.\n INSTRUCTIONS : '+nut_instruction
        nut_recepie = get_recepie(ins_ing)
        st.expander('View Recipe', expanded=False).markdown(nut_recepie, unsafe_allow_html=True)
        st.write('Recipe prepared successfully')
        nutritional_info = nut_ask_llm(nut_recepie)
        st.markdown(nutritional_info, unsafe_allow_html=True)


    elif 'apikey' not in st.session_state:
        st.error('Please enter API key to proceed')



