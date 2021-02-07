import streamlit as st
import sqlite3
from sqlite3 import Error
import pandas as pd 
from datetime import datetime
from automate_upload import trigger_upload
import os 

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def update_data(input_condition, conn, updated_data):
    sql_statement = ''' UPDATE qnadata SET '''
    if conn is not None:
        sql_statement += input_condition
        cur = conn.cursor()
        cur.execute(sql_statement, updated_data)
        conn.commit()
        
def check_id_exists(conn):
    if conn is not None:
        sql_statement = ''' SELECT DISTINCT(query_id) FROM qnadata '''
        cur = conn.cursor()
        cur.execute(sql_statement)
        rows = cur.fetchall()
        return [row[0] for row in rows]
        
def app():
    conn = create_connection('qna_data.db')
    st.title('GoldenRetriever')
    st.header('This front end application allows you to easily update existing data in a simple and clear interface.')
    st.markdown('View the source code [here](https://github.com/aimakerspace/goldenretriever)!')
    st.markdown('Visit our [community](https://makerspace.aisingapore.org/community/ai-makerspace/) and ask us a question!')
    st.markdown('Note that you are able to update ``either question or answer`` or ``both`` at the same time!')
    st.button('Page Refresh!')
    data_id = st.empty()
    qn_text = st.empty()
    ans_text = st.empty()
    value = " "
    if st.button('Reset Input Value'):
        value = ""
    
    DATA_ID = data_id.text_input('Input the existing question id or answer id here (Compulsory)', value)
    question = qn_text.text_area('Input the updated question here (Optional)', value) 
    answer = ans_text.text_area('Input the updated answer here (Optional)', value)
    
    if st.button('Update Data'):
        if (DATA_ID.strip() == ''):
            st.text('Please enter your data id!')
        elif (int(DATA_ID) not in check_id_exists(conn)):
            st.text('The data id does not exist in the database!')
        elif (question.strip() == '' and answer.strip() == ''):
            st.text('Please input at least a question or an answer')
        elif (question.strip() != '' and answer.strip() == ''):
            st.text('You are going to update a question')
            update_data('query_str = ? WHERE query_id = ?', conn, [question, DATA_ID])
        elif (question.strip() == '' and answer.strip() != ''):
            st.text('You are going to update an answer')
            update_data('ans_str = ? WHERE query_id = ?', conn, [answer, DATA_ID])
        elif (question.strip() != '' and answer.strip() != ''):
            st.text('You are going to update both question and answer.')
            update_data('query_str = ?, ans_str = ? WHERE query_id = ?', conn, [question, answer, DATA_ID])

    st.header('Database Preview')
    
    df = pd.read_sql_query("SELECT query_id, query_str, ans_id, ans_str FROM qnadata", conn)
    
    st.write(df)
    
    if (st.button("Export Data")):
        now = datetime.now()
        formatted_date = now.strftime("%d_%m_%Y_%H_%M_%S") 
        display_date = now.strftime("%d/%m/%Y, %H:%M:%S")
        try:
            df.to_csv(f'data/sample_duke_hr.csv')
            result = trigger_upload('http://localhost:9200/', 'data/sample_duke_hr.csv', 'duke_hr')
            st.markdown(f'You have successfully saved your data in the ``data`` folder and also in ``elk`` at {display_date}!')
            print(result)
            st.balloons()
        except Exception as e:
            print(e)
            st.write('An error occured. Please try again!')
    elif (st.button("Reset Database")):
        try:
            os.remove('qna_data.db')
            st.markdown(f'The database has been successfully resetted! Please refresh the website.')
        except FileNotFoundError:
            st.write('The database file does not exist! Please refresh the website!')
        except Exception as e:
            print(e)
            st.write('An error occured. Please try again!')