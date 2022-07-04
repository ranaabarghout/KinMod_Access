
"""
Created on Tue May 17 12:22:09 2022

@author: ranam
"""

import pandas as pd 
import sys 
# print(sys.path)

organism_list = pd.read_csv('organism_list.csv')

organism_list_sequences = pd.read_csv('ecnumber-sequence-org.csv')


org_list = []

for i in range(len(organism_list_sequences)):
    # org = (str(organism))
    # org = org[9:]
    orgn = organism_list_sequences.iloc[i, -1]
    orgn = (str(orgn))
    org = orgn.split(' ')
    org = org[0:2]
    org = ' '.join(org)
    # print(len(org))
    org_list.append(org)
    # print(org.dtype)
    # organism_list_sequences.iloc[i, -1] = org

#%%

organism_list_sequences['Organism_Name'] = org_list
organism_list_sequences.drop(columns=['Organism'], inplace=True)
organism_list_sequences.rename(columns={"Organism_Name": "Organism"}, inplace=True)

#%% Need to merge here

merged = pd.merge(organism_list, organism_list_sequences, how='left', on = ['Organism'])
merged.dropna(inplace=True)

#%% Analysis on organisms with sequence data

sequence_organisms = merged.Organism.unique()
seq_per_organisms = merged.Organism.value_counts()
print(seq_per_organisms)
organisms_w_sequences = pd.DataFrame(sequence_organisms, columns=['Organism'])
organisms_w_sequences.to_csv('organisms_w_sequences.csv')