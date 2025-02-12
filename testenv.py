# attempting to get environment variables working w/ Github Secrets
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv()) # loads environment variables from the .env file 

print(f'SERIVCE_ACCOUNT_KEY => {os.getenv("SERVICE_ACCOUNT_KEY")}')