# attempting to get environment variables working w/ Github Secrets
from dotenv import load_dotenv, find_dotenv
import os, base64, json

load_dotenv(find_dotenv()) # loads environment variables from the .env file 
print(os.getenv("TEST_VAR"))