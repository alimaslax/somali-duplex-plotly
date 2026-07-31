import os
from distutils.util import strtobool

from dotenv import load_dotenv

load_dotenv()

APP_DEBUG = bool(strtobool(os.getenv("DEBUG", "True")))
NINJAS_API_KEY = os.getenv("NINJAS_API_KEY")
