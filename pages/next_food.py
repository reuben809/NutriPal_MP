import streamlit as st
from streamlit_lottie import st_lottie 
from langchain_community.llms import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import requests


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
st.subheader(' :violet[Predict your next]')

url = requests.get( 
    "https://lottie.host/561e66a9-5d47-42c4-ae0a-53ae0f9b31dc/1YI1SYCjX5.json") 

url_json = dict() 
  
if url.status_code == 200: 
    url_json = url.json() 
else: 
   st.sidebar.error('Error in generating animations')

with st.sidebar:
    st_lottie(url_json, speed=2, height=200, quality='high', width=190)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)



@st.cache_resource
def ask_llm(data):
    template = """Food Consumption History: {quest}

    .\nYou are given data of Food consumption history of a person. You have to predict the next meal of the person based on the data given.
    Even if information provided is less for next meal predition do create a generalized prediction of next meal.
    \n Prediction depends upon, food items consumed in order and frequency of food items's consumed. Like a Sequential task.
    \nYou're free to add new meal as well as recommend some old meal.
    \n Output should be a meal name or a list of meal names.
    \n First answer which meal would be next meal and then proceed with your response"""

    prompt = PromptTemplate(input_variables=["quest"], template=template)

    final_prompt = prompt.format(quest = data)

    repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"

    llm = HuggingFaceEndpoint(
        repo_id=repo_id, max_length=1024, temperature=0.5, huggingfacehub_api_token=st.session_state['apikey']
    )
    # llm_chain = LLMChain(prompt=prompt, llm=llm)

    return llm(final_prompt)


def repeatfood():
    st.write("Let's start with your daily food intake. Please enter the details below.")
    st.info('Better to enter food items in order of consumption. Eg: Breakfast, Lunch, Snacks, Dinner')
    eating_habits = st.text_area('What did you eat today?')

    # st.write(st.session_state['apikey'])

    if eating_habits:
        existing_food_history = st.session_state['collection'].find_one({"Username":st.session_state['logged'].split('isloggedin')[0]})["food_history"]
        new_food_history = existing_food_history + ".\n" + eating_habits
        filter_food= {"Username":st.session_state['logged'].split('isloggedin')[0]}
        update_food = {"$set": {"food_history": new_food_history}}
        st.session_state['collection'].update_one(filter_food, update_food)

        st.write('Your food intake has been recorded successfully. You can now proceed to the next step.')

        predict_next_meal = st.button('Predict my next meal')
        if predict_next_meal:
            data = st.session_state['collection'].find_one({"Username":st.session_state['logged'].split('isloggedin')[0]})["food_history"]
            response_llm = ask_llm(data)
            st.write("Predicted Meal: \n")
            st.write(response_llm)



if 'apikey' in st.session_state and 'logged' in st.session_state:
    repeatfood()

else:
    st.error("Please login to access this page")

