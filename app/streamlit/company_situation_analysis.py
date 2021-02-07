import streamlit as st
import sqlite3
from sqlite3 import Error
import pandas as pd 
from datetime import datetime
from automate_upload import trigger_upload
import os 
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def app():
    conn = create_connection('qna_data.db')
    st.title('GoldenRetriever')
    st.header('This front end application allows you to easily know about what the employees are talking about!')
    st.markdown('View the source code [here](https://github.com/aimakerspace/goldenretriever)!')
    st.markdown('Visit our [community](https://makerspace.aisingapore.org/community/ai-makerspace/) and ask us a question!')
    df = pd.read_sql_query("SELECT * FROM userinput", conn)
    st.header('Database Preview')
    st.write(df)
    st.markdown('# Word Cloud')
    # Create stopword list:
    stopwords = set(STOPWORDS)
    word_cloud_data = " ".join(query for query in df.query_str)
     # Generate a word cloud image
    wordcloud = WordCloud(stopwords=stopwords, background_color="white").generate(word_cloud_data)
    word_counts = WordCloud().process_text(word_cloud_data)
    print(word_counts)
    word_count_df = pd.DataFrame([[k, v]for k, v in word_counts.items()], columns=['Unique Word', 'Occurrence'])
    # Display the generated image:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    st.pyplot()
    st.markdown('# Table Format of WordCloud')
    st.write(word_count_df)