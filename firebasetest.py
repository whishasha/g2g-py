# attempting to get environment variables working w/ Github Secrets
from dotenv import load_dotenv, find_dotenv
import os, base64, json

load_dotenv(find_dotenv()) # loads environment variables from the .env file 
encoded_service_account_key = os.getenv("SERVICE_ACCOUNT_KEY")
SERVICE_ACCOUNT_JSON = json.loads(base64.b64decode(encoded_service_account_key).decode('utf-8'))

#setting up firebase
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials


# Use a service account.
cred = credentials.Certificate(SERVICE_ACCOUNT_JSON)

app = firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.collection("users").document("apamil")
doc_ref.set({"first": "Akhil", "last": "Pamillion", "born": 2007})
print('Record has been created!')