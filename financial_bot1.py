import streamlit as st
from langchain.llms import OpenAI
import langchain
from langchain.document_loaders import WebBaseLoader

import sys
sys.path.append("/Users/rufen/Documents/Github/LLM_Financial_Chatbot/FinNLP")         
sys.path.append("/Users/rufen/Documents/Github/LLM_Financial_Chatbot/FinRL-Meta/")

from finnlp.data_sources.company_announcement.juchao import Juchao_Announcement
#from meta.data_processors.akshare import Akshare
import yfinance as yf

import datetime
from datetime import datetime, timedelta
import pandas as pd
from tqdm.notebook import tqdm

# Title of the app
st.title("💬 Rufen's Investment Advisor")

# Sidebar for API key input
openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')

# Sidebar slider for temperature control
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.5, step=0.1)

# Sidebar for selecting the LLM task
task = st.sidebar.selectbox("Choose a task:", ["Summarization news", "Summarization reports", "Question Answering"])

# Function to fetch text from a URL
def fetch_text(input_url):
    try:
        loader = WebBaseLoader(input_url)
        docs = loader.load()
        return "".join([doc.page_content for doc in docs])
    except Exception as e:
        return f"Error fetching content from the provided URL: {str(e)}"


# announcements prepare for summarize stock reports function 
today = datetime.today()
half_year_delta = timedelta(days=182)

start_date = (today - half_year_delta).strftime("%Y-%m-%d")
end_date = today.strftime("%Y-%m-%d")
max_page = 100  
stock_ticker =     
searchkey = ""       
get_content = True   
save_dir = "./tmp/"  
delate_pdf = True  

downloader = Juchao_Announcement()
downloader.download_date_range_stock(
    start_date,
    end_date,
    stock_ticker,
    max_page,
    searchkey,
    get_content,
    save_dir,
    delate_pdf,
)
announcement_df = downloader.dataframe

# price, also prepare for summarize stock reports function 
time_interval = "daily"
data = yf.download(stock_ticker, start=start_date, end=end_date, interval=time_interval)
data.reset_index(inplace=True)
data['Date'] = pd.to_datetime(data['Date'])
price_df = data


# Using a form for input and submit button
with st.form('my_form'):
    if task == "Summarization news":
        text = st.text_input('Enter URL:', "Enter the URL of the news article here")
    elif task == "Summarization reports":
        stock_ticker = st.text_input('Enter stock ticker:', "Enter the stock ticker (e.g., AAPL): ") 
    elif task == "Question Answering":
        text = st.text_input('Enter URL:', "Enter the URL of the document here")
    submitted = st.form_submit_button('Submit')

    if submitted:
        if not openai_api_key.startswith('sk-'):
            st.warning('Please enter a valid OpenAI API key!', icon='⚠️')
        else:
            llm = OpenAI(temperature=temperature, openai_api_key=openai_api_key)

            if task == "Summarization news":
                news = fetch_text(text)
                if news:
                    prompt = "Please give a brief summary of these news and analyze the possible trend of the stock price of the Company. \
                        Please give trend results based on different possible assumptions." + news
                    response = llm(prompt)
                    st.write("Summarized News:")
                    st.write(response)
                else:
                    st.warning("Please enter a valid URL.")

            elif task == "Summarization reports":
                if stock_ticker is not None and stock_ticker.strip():
                    # Filter the announcement_df based on the stock_ticker
                    stock_announcements = announcement_df[announcement_df['secCode'] == stock_ticker]
                    
                    # Iterate over the filtered announcements
                    for index, row in stock_announcements.iterrows():
                        stock_name = row['secName']
                        open_end = row['announcementTime']
                        
                        open_change = price_df.query("Date <= @open_end ")
                        open_change = (open_change['Open'].pct_change().iloc[-5:]* 100).tolist()
                        open_change = [round(i,2) for i in open_change]
                        
                        prompt = f"Here is an announcement of the company {stock_name}: '{row['Content']}'. \
                         This announcement was released on {open_end}, The open price changes of the company {stock_name} for the last five days before this announcement are {open_change}\
                         First, please give a brief summary of this announcement.\
                         Next, please describe the open price changes in detail then analyze the possible reasons.\
                         Finally, analyze the possible trend of the open price based on the announcement and open price changes of {stock_name}.\
                         Please give trend results based on different possible assumptions.\
                         All results should be in English"
                        
                        response = llm(prompt)
                        st.write(f"Summarized report for {stock_name}:")
                        st.write(response.replace("。", "\n"))
                else:
                    st.warning("Please enter a valid stock ticker.")

            elif task == "Question Answering":
                content = fetch_text(text)
                if content:
                    question = st.text_input("Enter your question:")
                    prompt = "Q: " + question + " A: " + content
                    response = llm(prompt)
                    st.write("Answer:")
                    st.write(response)
                else:
                    st.warning("Please enter a valid URL.")