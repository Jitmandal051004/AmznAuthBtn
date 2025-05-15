from flask import redirect
from dotenv import load_dotenv
import os
load_dotenv()
# Load environment variables from .env file

def redirectToAuth():
    redirect_url = os.getenv("AMZ_AUTH_URL")
    return redirect(redirect_url)
