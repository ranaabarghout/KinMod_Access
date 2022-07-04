# this code generates username and password
# needed for connecting to ice server.
# it will store keys in ../Input/key.json file.
# %%
import json
import os
from os.path import dirname, abspath

input_folder = "\Input\\"
file_name = "key.json"
dump_dir = dirname(dirname(abspath(__file__))) +input_folder
dump_file = dump_dir + file_name

if not os.path.exists(dump_dir):
    os.makedirs(dump_dir)

try:
    os.path.isdir(dump_dir)
except:
    print("directory does not exist")
    exit()

print("Please input following information to connect to the SQL database on the remote server")
# key1 = input("Please input the username?")
key1 = "LMSE_RO"
# key2 = input("please input the passwprd?")
key2 = '5673'
# key3 = input("please input the host URL?")
key3 = 'ice.biozone.utoronto.ca'
# key4 = input("please input the database name?")
key4 = 'LMSE'
mysql_connection ={'user':key1,'password':key2,'host':key3,'database':key4}

with open(dump_file, 'w') as fp:
    json.dump(mysql_connection,fp)

print("key.json is generate in the input folder")

# %%
