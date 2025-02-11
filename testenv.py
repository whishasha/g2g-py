# attempting to get environment variables working w/ Github Secrets
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv()) # loads environment variables from the .env file 

print(f'TEST_VAR => {os.getenv("TEST_VAR")}')