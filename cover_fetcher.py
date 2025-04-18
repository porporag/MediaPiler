from API_KEYS import API_KEY,API_SECRET,username,password

API_KEY = API_KEY
API_SECRET = API_SECRET

import pylast
from threading import Thread
import requests
from PIL import Image, ImageDraw
from io import BytesIO

username = username
password_hash = pylast.md5(password)

network = pylast.LastFMNetwork(
    api_key=API_KEY,
    api_secret=API_SECRET,
    username=username,
    password_hash=password_hash,
)


def fetch(author, title):
    try:
        album = network.get_album(author, title)
        if not album:  # Album not found
            return None
        cover = album.get_cover_image()
        response = requests.get(cover)
        if response.status_code < 200 or response.status_code >= 300:
            raise Exception(f"Failed to load cover image ({response.status_code})")
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        print(f"Error fetching cover image: {e}")
        return None

def display(cover):
    try:
        response = requests.get(cover)
        if not response.ok:  # Not OK status code
            raise Exception("Failed to load cover image")
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        print(f"Error displaying cover image: {e}")
        return None
	
