import streamlit as st
import sqlite3
from sqlite3 import Error
import pandas as pd 
from datetime import datetime
from automate_upload import trigger_upload

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def delete_data(conn, data_id):
    sql_statement = ''' DELETE FROM qnadata WHERE query_id=? '''
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql_statement, data_id)
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
    st.header('This front end application allows you to easily delete existing data in a simple and clear interface.')
    st.markdown('View the source code [here](https://github.com/aimakerspace/goldenretriever)!')
    st.markdown('Visit our [community](https://makerspace.aisingapore.org/community/ai-makerspace/) and ask us a question!')
    st.button('Page Refresh!')
    data_id = st.empty()
    value = " "
    if st.button('Reset Input Value'):
        value = ""
    
    DATA_ID = data_id.text_input('Input the existing question id or answer id here', value)
    
    if st.button('Delete Data'):
        if (DATA_ID.strip() == ''):
            st.text('Please enter your data id!')
        elif (int(DATA_ID) not in check_id_exists(conn)):
            st.text('The data id does not exist in the database!')
        else:
            delete_data(conn, [DATA_ID])
            
            
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