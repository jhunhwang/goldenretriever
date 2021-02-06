import streamlit as st
import pandas as pd 
import sqlite3
from sqlite3 import Error
from datetime import datetime
from automate_upload import trigger_upload

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        return conn
    except Error as e:
        print(e)
    
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        print('Table has been created successfully!')
    except Error as e:
        print(e)
        
def main_db_setup(conn):
    create_data_table = 'CREATE TABLE IF NOT EXISTS qnadata (id integer PRIMARY KEY, query_id integer NOT NULL, query_str text NOT NULL, ans_id integer NOT NULL, ans_str text NOT NULL);'
    # create tables
    if conn is not None:
        # create data table
        create_table(conn, create_data_table)
    else:
        print("Error! cannot create the database connection.")
    
def insert_data(conn, qna_data):
    
    if conn is not None:
        sql_statement = ''' INSERT INTO qnadata(query_id, query_str, ans_id, ans_str)
              VALUES(?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql_statement, qna_data)
        conn.commit()
        return f"You have successfully inserted the data into the database! The row id is {cur.lastrowid}!"
    
def check_number_of_rows_in_db(conn):
       
    if conn is not None:
        sql_statement = 'SELECT COUNT(*) FROM qnadata'
        cur = conn.cursor()
        cur.execute(sql_statement)
        rows = cur.fetchall()
        print(rows[0][0])
        return rows[0][0]
        
def app():
    conn = create_connection('qna_data.db')
    main_db_setup(conn)
    st.title('GoldenRetriever')
    st.header('This front end application allows you to easily enter new data in a simple and clear interface.')
    st.markdown('View the source code [here](https://github.com/aimakerspace/goldenretriever)!')
    st.markdown('Visit our [community](https://makerspace.aisingapore.org/community/ai-makerspace/) and ask us a question!')
    st.markdown('Remember to **CLICK** ``Page Refresh button`` after every ``input reset``.')
    st.button('Page Refresh!')
    qn_text = st.empty()
    ans_text = st.empty()
    value = " "
    if st.button('Reset Input Value'):
        value = ""

    question = qn_text.text_area('Input question here', value) 
    answer = ans_text.text_area('Input answer here', value)
       
    if (st.button("Submit Data")):
        if (question.strip() == '' or answer.strip() == ''):
            st.text('Please enter your question or answer again!')
        else:
            row_nums = int(check_number_of_rows_in_db(conn))
            qna_data = (row_nums + 1, question, row_nums + 1, answer)
            result = insert_data(conn, qna_data)
            st.text(result)
       
        
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