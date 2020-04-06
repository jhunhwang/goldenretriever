import requests
import datetime
import pyodbc
import numpy as np
import pandas as pd
import pandas.io.sql as pds
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, PublicAccess
import tarfile

from db_handler import get_last_insert_ids, extract_qa_pair_based_on_idx, get_kb_id_ref, get_permissions, ensure_connection
from exceptions import InvalidUsage

def upload_knowledge_base_to_sql(request, conn, cursor, get_kb_dir_id, get_kb_raw_id, permissions, kbh):
    """
    Receive knowledge bases from users
    
    args:
    ----
        hashkey: (str, optional) identification; intended to be their hashkey 
                                 to manage exclusive knowledge base access.
        kb_name: (str) Name of knowledge base to save as
        kb: (dict) contains the responses, queries and mappings
                   where mapping maps the indices of (question, answer)


    Sample json body & sample kb:
        {
         'hashkey': HASHKEY,
         'kb_name':'test1',
         'kb':{'responses': ["I'm 21 years old", 
                             "I hate mondays"],
               'contexts': ["Bob", "Gary"],
               'queries': ["What do you not love?", 
                           "How old are you?"],
               'mapping': [(0,1), (1,0)]
              }
        } 
    """
    def parse_req(request, conn, cursor):

        request_timestamp = datetime.datetime.now()
        request_dict = request.get_json()
        conn, cursor = ensure_connection(conn, cursor)
        
        # verify that required arguments are inside
        if not all([key in request_dict.keys() for key in ['hashkey','kb_name', 'kb']]):
            raise InvalidUsage(message="knowledge_base endpoint requires arguments: hashkey, kb_name, kb")
        
        return request_dict, request_timestamp

    def save_kb_name_in_kb_dir_kb_raw(cursor, user_id, kb_name):
        """
        Load the knowledge base
        """
        # 1a. load to kb_directory
        cursor.execute('INSERT INTO dbo.kb_directory VALUES ( ?, ?, ?)', 
                        [request_timestamp, kb_name, user_id])
        cursor.commit()

        # 1b. get kb_directory index to load into kb_raw
        kb_dir = pds.read_sql("""
                            SELECT * from dbo.kb_directory 
                            WHERE user_id = (?)
                            AND dir_name = (?)
                            """,
                            conn,
                            params = [user_id, kb_name],
                            )
        kb_dir_idx = kb_dir.id.iloc[-1]

        # 2a. load into kb_raw
        # https://stackoverflow.com/questions/41973933/invalid-parameter-type-numpy-int64-when-inserting-rows-with-executemany
        # kb_dir_idx has to be integer typed
        cursor.execute('INSERT INTO dbo.kb_raw VALUES ( ?, ?, ?, ?)', 
                        [None, kb_name, 'user_uploaded', int(kb_dir_idx)])
        cursor.commit()

    def save_responses(kb, cursor):
        # 3. load into kb_clauses
        responses = kb['responses']
        
        context_strings = kb.get('contexts', [])
        context_strings = ['']*len(responses) if len(context_strings)==0 else context_strings
        if len(context_strings) != len(responses):
            raise InvalidUsage(message="contexts should either have the same number of strings as responses or excluded")

        list_of_clauses = [[kb_raw_dir_idx, clause_ind, context_string, raw_string, context_string + '\n' + raw_string, request_timestamp]
                            for clause_ind, (context_string, raw_string) in enumerate(zip(context_strings, responses))
                            ]

        cursor.executemany('INSERT INTO dbo.kb_clauses VALUES ( ?, ?, ?, ?, ?, ?)', 
                            list_of_clauses)
        cursor.commit()
        idx_of_inserted_clauses = get_last_insert_ids(cursor, list_of_clauses)

        return idx_of_inserted_clauses
    
    
    def save_query_and_mappings(kb, idx_of_inserted_clauses):
        # print(kb.keys())
        if all(key_ in kb.keys() for key_ in ['queries', 'mapping']):
            if (len(kb['queries'])>0) & (len(kb['mapping'])>0):

                print("loading labels")

                # 4. load into query_db
                cursor.executemany('INSERT INTO dbo.query_db VALUES (?)', 
                                    [[query_] for query_ in kb['queries']])
                cursor.commit()
                idx_of_inserted_queries = get_last_insert_ids(cursor, kb['queries'])
        
                # 5. load into query_labels
                #    query labels have the following columns
                #    query_id, clause_id, span_start, span_end, created_at
                mapped_query_ids = pd.Series(idx_of_inserted_queries).iloc[extract_qa_pair_based_on_idx(kb['mapping'], idx=0)]
                mapped_clause_ids = pd.Series(idx_of_inserted_clauses).iloc[extract_qa_pair_based_on_idx(kb['mapping'], idx=1)]

                list_of_query_labels = [[mapped_query_id, mapped_clause_id , None, None, request_timestamp]
                                        for mapped_query_id, mapped_clause_id
                                        in zip(mapped_query_ids,mapped_clause_ids )
                                        ]

                cursor.executemany('INSERT INTO dbo.query_labels VALUES (?, ?, ?, ?, ?)', 
                                    list_of_query_labels)
                cursor.commit()

    request_dict, request_timestamp = parse_req(request, conn, cursor)

    # get and validate arguments
    HASHKEY = request_dict.get('hashkey', '')
    kb_name = request_dict["kb_name"]
    kb = request_dict["kb"]

    try:
        user_id = permissions.loc[HASHKEY].user_id.iloc[-1]
    except:
        print(f"ERROR: Tried to retrieve user id from {HASHKEY}")
        print( permissions.loc[HASHKEY] )
        raise InvalidUsage(message="Hashkey not recognized")

    save_kb_name_in_kb_dir_kb_raw(cursor, user_id, kb_name)

    get_kb_dir_id, get_kb_raw_id = get_kb_id_ref(conn)
    permissions = get_permissions(conn)
    kb_raw_dir_idx = get_kb_raw_id[kb_name]

    idx_of_inserted_clauses = save_responses(kb, cursor)
    save_query_and_mappings(kb, idx_of_inserted_clauses)

    return kb_name