""""""
"""
Version:
--------
0.1 11th May 2020

Usage:
------
Script to handle indexing of QnA datasets into Elasticsearch for downstream finetuning and serving
- Define index schema using elasticsearch_dsl classes
- Connect and upload Documents to Elasticsearch
"""
from datetime import datetime
from elasticsearch_dsl import Index, Document, InnerDoc, Date, Nested, Keyword, Text, Integer, connections
from argparse import ArgumentParser
import pandas as pd 
import streamlit as st

def trigger_upload(url, csv_file, index_name):
    index = Index(index_name)
   
    index.settings = {"number_of_shards": 1,
                  "number_of_replicas": 0}
    
    # index schema
    class QA(InnerDoc):
        ans_id = Integer()
        ans_str = Text(fields={'raw': Keyword()})
        query_id = Integer()
        query_str = Text()
        
    @index.document
    class Doc(Document):
        doc = Text()
        created_at = Date()
        qa_pair = Nested(QA)

        def add_qa_pair(self, ans_id, ans_str, query_id, query_str):
            self.qa_pair.append(QA(ans_id=ans_id, ans_str=ans_str, query_id=query_id, query_str=query_str))

        def save(self, **kwargs):
            self.created_at = datetime.now()
            return super().save(**kwargs)
        
    # connect to ES instance and start indexing
    connections.create_connection(hosts=[url])
    qa_pairs = pd.read_csv(csv_file).fillna('nan').to_dict('records')
    print('uploading docs')
    counter = 0
    st.markdown('Progress Bar')
    progress_bar = st.progress(0)
    qa_pairs_len = len(qa_pairs)
    chunks = 1 / qa_pairs_len
    print(chunks)
    for i, pair in enumerate(qa_pairs): 
        first = Doc(doc=pair['ans_str'])
        print(first)
        first.add_qa_pair(pair['ans_id'], pair['ans_str'], pair['query_id'], pair['query_str'])
        first.save()
        counter += 1 
        chunks = chunks + (i/10)
        if (chunks > 1):
            progress_bar.progress(chunks - 1)
            progress_bar.progress(100)
            break
        progress_bar.progress(chunks)
    print("indexing finished")
    print(f'indexed {counter} documents')
    return 'Done'

