import os

from dotenv import load_dotenv

load_dotenv(".env")

CLIENT_ID = os.environ["CLIENT_ID"]
HOST = os.environ["HOST"]
SECRET_KEY = os.environ["SECRET_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]
