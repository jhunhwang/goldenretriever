"""
Streamlit app

Sample usage:
note the empty double flag --  to input app arguments, as opposed to streamlit arguments
https://github.com/streamlit/streamlit/issues/337
---------------------------------------------------
    streamlit run app/streamlit/main.py -- --url <url for API endpoints>

"""
import streamlit as st
import requests
import argparse
import SessionState
from urllib.parse import quote
from automate_finetune import run_finetune
from automate_index_extract import main_index_extract
from automate_index_encode import main_index_encode
import time

def app():
    # API arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', 
                        default="http://127.0.0.1:8000/",
                        help="GoldenRetriever's API endpoint to query / feddback to")

    args = parser.parse_args()
    APP_URL = args.url
    if not APP_URL.endswith('/'): APP_URL = APP_URL+'/'


    # SessionState
    # Init per-session persistent state variabless
    # by default in streamlit, when one checkbox is click, the others reset
    # SessionState solves that by retaining persistent variables in the session
    state = SessionState.get(
        fetch=False, 
        prediction=[],      
        query_id='',           
        k0=False,k1=False,k2=False,k3=False,k4=False,
    )

    # header and info
    # 1. INTRODUCTION AND INFO
    st.title('GoldenRetriever')
    st.header('This Information Retrieval demo allows you to query FAQs, T&Cs, or your own knowledge base in natural language.')
    st.markdown('View the source code [here](https://github.com/aimakerspace/goldenretriever)!')
    st.markdown('Visit our [community](https://makerspace.aisingapore.org/community/ai-makerspace/) and ask us a question!')

    # fetch logic and query string
    query_string = st.text_input(label='Input query here') 
    if st.button('Fetch', key='fetch'):
        state.fetch = True
        res = requests.post(APP_URL + 'query', 
                                json = {"query": query_string, "k": 5})
        if res.status_code == 200:
            res = res.json()
            state.prediction = res['resp']
            state.query_id = res['query_id']
        else:
            st.markdown(res.status_code)
            st.markdown(res.json())

    checkbox_list = [st.empty() for i in range(5)]

    # feedback logic
    if state.fetch:        

        for ansnum, result in enumerate(state.prediction):
            if checkbox_list[ansnum].checkbox(result, key=f"checkbox{ansnum}"):
                setattr(state, f'k{ansnum}', True)

        submit_button = st.empty()
        if submit_button.button('Feedback relevant answers'):
            feedbacks = [int(getattr(state,f"k{i}")) for i in range(5)]
            feedback_res = requests.post(APP_URL + 'feedback', 
                                        json={"query_id":state.query_id, 
                                            "is_correct": feedbacks
                                            })
            if feedback_res.json()['resp'] == 'updated': 
                st.text("Feedback received!")
            else:
                st.text(f"unexpected response: {feedback_res.json()}")

            # reset states
            state.fetch=False
            state.prediction=[]
            for i in range(5):
                checkbox_list[i].empty()
            submit_button.empty()

    st.markdown(
    """
    <details><summary>Sample sentences</summary>
    <strong>COVID-19</strong>
    <p>Why are schools still continuing with CCAs and PE lessons?</p>
    <strong>PDPA</strong>
    <p>How long can an organisation retain its customers' personal data?</p>
    <strong>HDB resale terms and conditions</strong>
    <p>Do I need to pay back CPF?</p>
    <strong>AIAP</strong>
    <p>What will be covered during the program?</p>
    <strong>Raw text </strong><a href="https://www.straitstimes.com/asia/east-asia/china-wants-centralised-digital-currency-after-bitcoin-crackdown" target="_blank">China Digital Currency</a><i> (Select all, copy, and paste into raw text box)</i>
    <p>Which electronic payment gateways support the currency?</p>
    </details>"""
    , unsafe_allow_html=True)
    
    st.markdown('# Tuning and Training the Model')
    st.markdown('Click the button below to update your new data into the model!')
    status_text = st.empty()
    
    if st.button('Train!'):
        start_time = time.time()
        print(f'Time has started!: {start_time}')
        try:
            st.markdown('Progress Bar')
            progress_bar = st.progress(0)
            run_finetune()
            progress_bar.progress(30)
            main_index_extract('duke_hr', 'sample_duke_hr', './test_hr')
            progress_bar.progress(60)
            main_index_encode('./data/sample_duke_hr.csv', 'model_artefacts', 'duke_hr', 'USEEncoder', './test_finetune/model_duke_hr/USE/best/0')
            progress_bar.progress(100)
            status_text.text("--- Training has been completed in %s seconds ---" % (time.time() -start_time))
        except:
            status_text.text("Please try again :D")
            raise st.ScriptRunner.StopException
