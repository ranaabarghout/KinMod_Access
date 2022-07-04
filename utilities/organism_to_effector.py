import mysql.connector
from mysql.connector import errorcode
import json
import os
import sys


## Connecting to MySQL server (USE VPN)

with open("./key.json") as jsonfile:
    data = json.load(jsonfile)
    try:
        cnx = mysql.connector.connect(user=data["user"],password=data["password"],host=data["host"],database=data["database"])
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        sys.exit()


## Passing query to MySQL
cursor          = cnx.cursor()
query = "call LMSE.organism_to_effector(%s)"  # stored procedure: goes from organism to regulator
parameters=('escherichia coli',) # Can do for loop for multiple organisms (can't pass list)
res = [] # Pandas df storing the query results
try:
    if not parameters:
        cursor.execute(query)
    else: 
        cursor.execute(query, parameters)
    row         = cursor.fetchone()
    while row  != None:
        res.append(row)
        row     = cursor.fetchone()
except Exception as a:
    delim = '\n'
    error = "Something is wrong in the query:"
    print(error , a, cursor._fetch_warnings(), sep=delim)
    error = error +delim+ str(a) +delim+ str(cursor._fetch_warnings())
    print("executed query:")
    print(cursor._executed)
cnx.close()

# print(res)
# %% Creating Dataframe from the 'res' raw dataframe
import pandas as pd
import numpy as np

column_names = ['Organism', 'EC Number', 'Regulators', 'Regulator IID', 'Regulator SMILES', 'Regulator INCHIKEY', 'KEGG ID', 'Inhibitor?', 'Activator?', 'Ki Value']

df = pd.DataFrame(np.zeros((5305, 10)), columns=column_names)

rows = range(0,10)

for i in range(len(res)):
    row = res[i]
    row_i = []
    for j in rows:
        row_i.append(row[j])
    df.iloc[i] = row_i
    
        

#%% Filtering data with regulator available ONLY -> might not need to do this as long as SMILES is available 

selected_rows = df[~df['Ki Value'].isnull()] ## This is required
regulator_available = selected_rows[~selected_rows['Regulator SMILES'].isnull()] ## Can switch this to ['Regulator SMILES'] or ['Regulators']

#%% Importing sequence to EC number data for E. coli

ecnum_seq = pd.read_csv('ecnumber-sequence-ECOLI.csv')
ecnum_seq.columns.values[0] = 'EC Number'
ecnum_seq.columns.values[1] = 'Sequence'
ecnum_seq.columns.values[2] = 'Organism'


ecnum_grouped = ecnum_seq.groupby('EC Number')['Sequence'].apply(list)
ecnum_grouped = ecnum_grouped.to_frame()
ecnum_grouped.reset_index(inplace=True)

#%% Merging the regulator df with the sequence df to get a combined df

left_df = regulator_available
right_df = ecnum_grouped

new_df = left_df.merge(right_df, on='EC Number', how='left')
new_df = new_df.explode('Sequence') # Exploding the sequence data to ensure 1 regulator is matched to 1 sequence

# Splitting the Ki values
for i in range(len(new_df)):
    ki_values = new_df['Ki Value'].iloc[i]
    split = ki_values.split(',')
    split = [float(x) for x in split]
    new_df['Ki Value'].iloc[i] = split


new_df = new_df.explode('Ki Value') # Exploding the ki values to ensure each regulator is matched to 1 Ki value and 1 sequence
no_zeros_ki = new_df.sort_values(by=['Ki Value'])
no_zeros_ki.reset_index(inplace=True)
no_zeros_ki.drop(columns='index', inplace=True)
no_zeros_ki = no_zeros_ki[no_zeros_ki['Ki Value']>0].dropna()

final_df = no_zeros_ki[~no_zeros_ki['Sequence'].isnull()] # Filtering regulators with no available sequence data

#%% Removing any duplicate rows
bool_series = final_df.duplicated(keep='first')
edited_final_df = final_df[~bool_series]


edited_final_df.to_csv('ECOLI_seq_reg.csv')