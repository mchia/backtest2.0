import os
from dotenv import load_dotenv

load_dotenv()

DATABASE: str = os.getenv(key='DATABASE')