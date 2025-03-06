# attempting to get environment variables working w/ Github Secrets
# from dotenv import load_dotenv, find_dotenv
# import os, base64, json

# load_dotenv(find_dotenv()) # loads environment variables from the .env file 
# encoded_service_account_key = os.getenv("SERVICE_ACCOUNT_KEY")
# SERVICE_ACCOUNT_JSON = json.loads(base64.b64decode(encoded_service_account_key).decode('utf-8'))
# deprecated code, now using SQL


import sqlite3

remote = sqlite3.connect('database.db')

cursor = remote.cursor()

# cursor.execute('''CREATE TABLE users (name varchar(100))''')
cursor.execute('''INSERT INTO users (name) VALUES ('hello')''')

remote.commit()

cursor.close()

