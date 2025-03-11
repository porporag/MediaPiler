import threading
import io
from flask import Flask, Response
from PIL import Image, ImageDraw
import time
from pydbus import SystemBus
from cover_fetcher import fetch, display
from gpiozero import Button
from signal import pause

# Flask app setup
app = Flask(__name__)

# Constants
IMG_WIDTH, IMG_HEIGHT = 400, 200
TEXT_COORDS = {"author": (100, 80), "track": (100, 280)}
UPDATE_INTERVAL = 5

# Shared resource for threads
lock = threading.Lock()
shared_data = {"img": Image.new('RGB', (IMG_WIDTH, IMG_HEIGHT), color='blue'),
                "author": "Author",
                "track": "Track"}

button = Button(2)

class MediaPlayer:
    """Handles interactions with the Bluetooth media player."""

    class DeviceNotFoundError(Exception):
        def __init__(self):
            super().__init__('No Bluetooth device was found.')

    @staticmethod
    def get_handle():
        """Finds and returns the Bluetooth media player handle."""
        bus = SystemBus()
        manager = bus.get('org.bluez', '/')
        for obj in manager.GetManagedObjects():
            if obj.endswith('/player0'):
                return bus.get('org.bluez', obj)
        raise MediaPlayer.DeviceNotFoundError


from PIL import ImageDraw, ImageFont, ImageOps


class Listener(threading.Thread):
    """Updates shared data with metadata and dynamic image."""

    def __init__(self, interval=UPDATE_INTERVAL):
        super().__init__()
        self.interval = interval

    def run(self):
        while True:
            try:
                handle = MediaPlayer.get_handle()
                metadata = handle.Track
                
                status = handle.Status

                author = metadata.get('Artist', 'Unknown Artist')
                title = metadata.get('Album', 'Unknown Album')
                track = metadata.get('Title', 'Unknown Track')

                # Fetch and process the cover image
                cover = fetch(author, title)
                img = display(cover)

                # Resize the image to fit the container
                target_size = (1000,1000)
                img = ImageOps.fit(img, target_size, Image.ANTIALIAS)

    
                # Update the shared resource
                with lock:
                    shared_data["img"] = img
                    shared_data["author"] = author
                    shared_data["track"] = track
                
                def play_pause():
                
                    if status == 'playing':
                        handle.Pause()
                        
                    if status == 'paused':
                        handle.Play()
                        
                
                button.when_pressed = play_pause
                
            except MediaPlayer.DeviceNotFoundError as e:
                print(e)
                time.sleep(self.interval)
            except Exception as e:
                print(f"Unexpected error: {e}")
            finally:
                time.sleep(self.interval)

        
@app.route('/metadata')
def metadata():
    """Returns the current author and track metadata."""
    with lock:
        data = {
            "author": shared_data.get("author", "Unknown Author"),
            "track": shared_data.get("track", "Unknown Track")
        }
    return data



@app.route('/image')
def image():
    """Returns the current dynamic image."""
    with lock:
        img = shared_data["img"]
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return Response(img_io, mimetype='image/png', headers={"Cache-Control": "no-store"})


@app.route('/')
def home():
    """Main HTML page."""
    return '''
        <html>
            <head>
                <title>Now Playing</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #1e1e2f;
                        color: #ffffff;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                    }
                    h1 {
                        font-size: 2.5rem;
                        margin-bottom: 20px;
                        color: #ffffff;
                        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
                    }
                    .image-container {
                        position: relative;
                        width: 1000px;
                        height: 1000px;
                        border: 5px solid #ffffff;
                        border-radius: 15px;
                        overflow: hidden;
                        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.5);
                    }
                    img {
                        width: 100%;
                        height: 100%;
                        display: block;
                        object-fit: cover;
                    }
                    .overlay {
                        position: absolute;
                        bottom: 0;
                        width: 100%;
                        background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
                        padding: 20px;
                        box-sizing: border-box;
                        color: white;
                    }
                    .track-info {
                        font-size: 1.5rem;
                        font-weight: bold;
                        margin: 0;
                    }
                    .author-info {
                        font-size: 1.2rem;
                        margin: 5px 0 0;
                        color: #cccccc;
                    }
                    footer {
                        margin-top: 20px;
                        font-size: 0.9rem;
                        color: #aaaaaa;
                    }
                    footer a {
                        color: #4e91ff;
                        text-decoration: none;
                    }
                    footer a:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <h1>Now Playing</h1>
                <div class="image-container">
                    <img id="dynamic-image" src="/image" alt="Dynamic Album Art">
                    <div class="overlay">
                        <p class="track-info" id="track-info">Track Name</p>
                        <p class="author-info" id="author-info">Author Name</p>
                    </div>
                </div>

                <script>
                    async function updateMetadata() {
                        try {
                            const response = await fetch('/metadata');
                            const metadata = await response.json();
                            document.getElementById('track-info').innerText = metadata.track || 'Unknown Track';
                            document.getElementById('author-info').innerText = metadata.author || 'Unknown Author';
                        } catch (error) {
                            console.error('Error fetching metadata:', error);
                        }
                    }

                    // Refresh metadata every 5 seconds
                    setInterval(() => {
                        updateMetadata();
                    }, 5000);

                    // Fetch metadata on page load
                    updateMetadata();

                    // Refresh the image every 5 seconds
                    setInterval(() => {
                        const img = document.getElementById('dynamic-image');
                        img.src = '/image?ts=' + new Date().getTime(); // Add timestamp to prevent caching
                    }, 5000);
                </script>
            </body>
        </html>
    '''




def run_flask():
    """Runs the Flask server."""
    app.run(debug=True, use_reloader=False)


if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    listener_thread = Listener(interval=UPDATE_INTERVAL)
    listener_thread.start()
    
    #button_thread = Button_listener()
    #button_thread.start()

    flask_thread.join()

