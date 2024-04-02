import streamlit as st
from langchain.llms import OpenAI

# Title of the app
st.title("💬 Rufen's Auto LLM App")

# Sidebar for API key input
openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')

# Sidebar slider for temperature control
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

# Sidebar for selecting the LLM task
task = st.sidebar.selectbox("Choose a task:", ["Generate Code", "Summarization", "Question Answering"])

# Function to generate response based on the selected task
def generate_response(input_text, task):
    # Initialize the OpenAI object with temperature and API key
    llm = OpenAI(temperature=temperature, openai_api_key=openai_api_key)
    
    # Switch for task types
    if task == "Generate Code":
        # Assuming you have a specific prompt structure for SQL generation
        prompt = f"Translate the following natural language query into SQL: {input_text}"
        response = llm(prompt)
    elif task == "Summarization":
        # Prepend 'Summarize this:' for summarization tasks
        prompt = "Summarize this: " + input_text
        response = llm(prompt)
    elif task == "Question Answering":
        # Frame the input as a question for the LLM
        prompt = "Q: " + input_text + " A:"
        response = llm(prompt)
    
    # Display the response in an info box
    st.info(response)

# Using a form for input and submit button
with st.form('my_form'):
    # Text area for user input, adjust placeholder text based on the selected task
    placeholder_text = "Enter your SQL query here" if task == "Generate SQL Code" else "Enter your text here"
    text = st.text_area('Enter text:', placeholder_text)
    
    # Submit button for the form
    submitted = st.form_submit_button('Submit')
    
    # Simple validation for the OpenAI API key
    if submitted:
        if not openai_api_key.startswith('sk-'):
            st.warning('Please enter a valid OpenAI API key!', icon='⚠️')
        else:
            # Generate response based on the input text and selected task
            generate_response(text, task)
