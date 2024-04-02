import streamlit as st
from langchain.llms import OpenAI
import pandas as pd
import matplotlib.pyplot as plt

# Assuming additional functions for executing SQL/Python and generating insights are defined:
# execute_code(code, language) -> Executes the given code and returns the result
# generate_insight(dataframe) -> Analyzes the dataframe and returns an insight

# Title of the app
st.title("💬 Rufen's Auto LLM App")

# Sidebar for API key input
openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')

# Sidebar slider for temperature control
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

# Sidebar for selecting the LLM task
task = st.sidebar.selectbox("Choose a task:", ["Summarization", "Q&A", "Data Interaction"])

if task == "Data Interaction":
    uploaded_file = st.sidebar.file_uploader("Upload your data file", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        if uploaded_file.type == "text/csv":
            dataframe = pd.read_csv(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            dataframe = pd.read_excel(uploaded_file)
        # Display the uploaded DataFrame
        st.write("Uploaded Data:")
        st.dataframe(dataframe)
    else:
        dataframe = None 

def generate_response(input_text, task):
    llm = OpenAI(temperature=temperature, openai_api_key=openai_api_key)
    
    if task == "Data Interaction":
        # Here, you'd define how you want to interpret the natural language to SQL/Python for data interaction
        # This is a simplified example that assumes the input text explicitly states the desired code generation language
        if "generate SQL" in input_text:
            prompt = f"Translate the following into SQL: {input_text}"
            language = "SQL"
        elif "generate Python code" in input_text:
            prompt = f"Translate the following into Python code: {input_text}"
            language = "Python"
        else:
            st.error("Please specify whether to generate SQL or Python code in your request.")
            return
        
        response = llm(prompt)
        code = response  # Assuming the LLM returns code directly
        
        # Execute the code and retrieve the result
        result = execute_code(code, language)
        
        if language == "SQL":
            # Assuming result is a DataFrame for simplicity
            dataframe = result
        elif language == "Python":
            # If Python code returns a DataFrame
            dataframe = result
        
        # Display the DataFrame
        st.dataframe(dataframe)
        
        # Generate and display insight
        insight = generate_insight(dataframe)
        st.write("Insight:", insight)
        
        # Visualize the DataFrame
        fig, ax = plt.subplots()
        dataframe.plot(ax=ax)  # This is a generic plot. Customize as needed.
        st.pyplot(fig)

    elif task == "Summarization":
        # Prepend 'Summarize this:' for summarization tasks
        prompt = "Summarize this: " + input_text
        response = llm(prompt)
        st.info(response)
    elif task == "Question Answering":
        # Frame the input as a question for the LLM
        prompt = "Q: " + input_text + " A:"
        response = llm(prompt)
        st.info(response)
        

# Form for input and submit button
with st.form('my_form'):
    placeholder_text = "Describe what you would like to do with the data:" if task == "Data Interaction" else "Enter your text here"
    text = st.text_area('Enter text:', placeholder_text)
    submitted = st.form_submit_button('Submit')
    
    if submitted:
        if not openai_api_key.startswith('sk-'):
            st.warning('Please enter a valid OpenAI API key!', icon='⚠️')
        else:
            generate_response(text, task)
