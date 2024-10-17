import os
import boto3
from dotenv import load_dotenv
# Get the path to the .env file, two levels up
dotenv_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "config", ".env"))

load_dotenv(dotenv_path)

# Database constants
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_URI = os.getenv("DATABASE_URI")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# setup s3 client 
s3 = boto3.client('s3')