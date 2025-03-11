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


def fetch(author,title):
	album = network.get_album(author, title)
	cover = album.get_cover_image()
	return cover
	

def display(cover):
	response = requests.get(cover)
	img = Image.open(BytesIO(response.content))
	# img.show()
	return img
	
