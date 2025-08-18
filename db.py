import os

from dotenv import load_dotenv

load_dotenv()

print(f"Database URL: {os.environ['DATABASE_URL']}")
