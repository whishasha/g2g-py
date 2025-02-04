
import os
from dotenv import load_dotenv

load_dotenv()
secret = os.getenv('TEST_VAR')

print(secret)

