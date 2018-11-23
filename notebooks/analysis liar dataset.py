# -*- coding: utf-8 -*-
# <nbformat>4</nbformat>

# <markdowncell>

# # Analysing Dataset

# <codecell>

import pandas as pd
import pandas_profiling
import requests
from functional import pseq
import pathlib
import os
import json
import time
import datetime

# <codecell>

directory_liar_dataset = "../liar_dataset"
directory_statements = f"{directory_liar_dataset}/statements"
directory_visualizations = "../visualizations"

# <codecell>

df = pd.concat([pd.read_csv(f"{directory_liar_dataset}/{part}.tsv", sep='\t', header=None) for part in ['train', 'valid']])
df.columns = ['statement_id', 'label', 'statement', 'subject', 'speaker', 'speakers_job_title', 'state_info', 'party_affiliation', 'barely_true_counts', 'false_counts', 'half_true_counts', 'mostly_true_counts', 'pants_on_fire_counts', 'context']

df.statement_id = df.statement_id.apply(lambda x: x[:-5])  # remove .json and get just ID

# <codecell>

df.head(10)

# <codecell>

# form URL from statement ID
def get_URL(statement_id):
    return f"http://www.politifact.com/api/v/2/statement/{statement_id}/?format=json"

# <codecell>

def extract_information(res):
    try:
        author = res['author']

        try:
            if len(author) > 0:
                author = author[0]['name_slug']
            else:
                author = None
        except Exception:
            print(author)

        return {'author_name_slug': author,
                'ruling_date':  res['ruling_date'],
                'statement_date' :res['statement_date'],
                'speaker_current_job': res['speaker']['current_job'],
                'speaker_first_name': res['speaker']['first_name'],
                'speaker_last_name': res['speaker']['last_name'],
                'speaker_home_state': res['speaker']['home_state'],
                'statement_id': res['id']
               }
    except KeyError:
        return {}

# <codecell>

#with requests.Session() as session:
#    additional_information = statement_ids.map(lambda sid: session.get(get_URL(sid)))\
#                                          .filter(lambda r: r.ok)\
#                                          .map(lambda r: r.json())\
#                                          .map(extract_information)\
#                                          .to_pandas()

# <codecell>

def safe_json_read(f):
    try:
        with open(f, 'r') as fc:
            return json.load(fc)
    except json.JSONDecodeError:
        print(f)
        return {}

# <codecell>

additional_information = pseq(pathlib.Path('../liar_dataset/statements/').iterdir())\
                               .map(safe_json_read)\
                               .filter(lambda x: len(x) > 0)\
                               .map(extract_information)\
                               .to_pandas()

df['statement_id'] = pd.to_numeric(df['statement_id'])
df['statement_date'] = pd.to_datetime(df['statement_date'])

df = df.merge(additional_information, on='statement_id', how='left')

# <codecell>

df.loc[df['speaker'] == 'barack-obama', ]['pants_on_fire_counts'].value_counts()

# <codecell>

df[df['speakers_job_title'].str.contains('County') == True].shape

# <codecell>

df['st']

# <codecell>

pandas_profiling.ProfileReport(df)

# <codecell>

# 

# <markdowncell>

# ## One row analysis

# <markdowncell>

# Let's analyse first row, statement with id `1`. What is the information we get there?

# <codecell>

sid = '1'

# <codecell>

df[df.statement_id == sid]

# <codecell>

with open(f"{directory_statements}/{sid}.json", "r") as f:
    data = json.load(f)
data

# <markdowncell>

# Just to visualize JSON hierarchy, run the following cell:

# <codecell>

def go_further(dic, name):
    dict_vis = {"name": name, "children": []}
    for k, v in dic.items():
        if type(v) == str:
            new_el = {"name": k}
        elif type(v) == list:
            if len(v) > 0:
                new_el = go_further(v[0], k)
        elif type(v) == dict:
            new_el = go_further(v, k)
        else:
            new_el = {"name": k}
        dict_vis["children"].append(new_el)
        
    return dict_vis

my_dict = go_further(data, name="statement_info")

with open(f"{directory_visualizations}/data.json", "w") as f:
    json.dump(my_dict, f)

print(f"Checkout visualization by: \n1) cd ../visualizations \n2) python -m http.server \n3) in browser, open: http://localhost:8000/")

# <codecell>

