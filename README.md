# MediaPiler
Music player via Bluetooth and Raspberry Pi

## Overview
MediaPiler is a Python-based project designed to turn a Raspberry Pi into a Bluetooth receiver for streaming music to a Hi-Fi stereo system. It provides a web interface to display the currently playing track, artist, and album cover, and allows basic playback controls (play/pause, next, previous) via physical buttons connected to the Raspberry Pi.

### Features
- **Bluetooth Receiver**: Streams music from a Bluetooth device to the Raspberry Pi.
- **Web Interface**: Displays the current track, artist, and album cover in a browser.
- **Playback Controls**: Physical buttons for play/pause, next, and previous track.
- **Album Cover Fetching**: Retrieves album covers using the Last.fm API.

---

## File Structure
### 1. `API_KEYS.py`
Stores API credentials for Last.fm:
```python
API_KEY = ""  
API_SECRET = ""
username = ""
password = ""
```

### 2. `app_flask.py`
Handles the Flask web server, DBUS integration for Bluetooth media control, and GPIO button handling.

#### Key Components:
- **Flask Web Server**: Serves endpoints for metadata (`/metadata`), album cover image (`/image`), and the main HTML page (`/`).
- **Listener Thread**: Periodically fetches metadata (track, artist, album) and album cover from the Bluetooth media player.
- **Playback Controls**: Configures GPIO buttons to control playback (play/pause, next, previous).

#### Endpoints:
- `/metadata`: Returns the current track and artist as JSON.
- `/image`: Returns the album cover as a PNG image.
- `/`: Displays the web interface with the current track, artist, and album cover.

### 3. `cover_fetcher.py`
Handles fetching album cover images from the Last.fm API.

#### Key Functions:
- `fetch(author, title)`: Retrieves the album cover image for a given artist and album title.
- `display(cover)`: Processes and returns the album cover image.

---

## Setup Instructions
1. **Set Up Raspberry Pi as a Bluetooth Receiver**:
   Follow the guide in the references: [Guide to turn the Pi into a Bluetooth receiver](https://forums.raspberrypi.com/viewtopic.php?t=235519&sid=ab884d8fc6855ef9906ca276cbf843ae).

2. **Install Dependencies**:
   Install the required Python libraries:
   ```sh
   pip install flask pydbus gpiozero requests pillow pylast
   ```

3. **Configure API Keys**:
   Update `API_KEYS.py` with your Last.fm API credentials.

4. **Run the Application**:
   Start the Flask server and listener thread:
   ```sh
   python app_flask.py
   ```

5. **Access the Web Interface**:
   Open a browser and navigate to `http://<raspberry-pi-ip>:5000` to view the current track and album cover.

---

## Usage
- **Bluetooth Streaming**: Pair your Bluetooth device with the Raspberry Pi and start streaming music.
- **Web Interface**: View the current track and album cover in the browser.
- **Playback Controls**: Use the physical buttons connected to the Raspberry Pi to play/pause, skip to the next track, or go to the previous track.

---

## Troubleshooting
- **No Album Cover Displayed**:
  - Ensure the Last.fm API credentials are correct.
  - Check the network connection for the Raspberry Pi.
- **Buttons Not Working**:
  - Verify the GPIO pins are correctly connected.
  - Check the button configuration in `app_flask.py`.

---

## References
[1] [Guide to turn the Pi into a Bluetooth receiver](https://forums.raspberrypi.com/viewtopic.php?t=235519&sid=ab884d8fc6855ef9906ca276cbf843ae)  
[2] [Handle DBUS with pydbus](https://stackoverflow.com/questions/74657226/receiving-audio-data-and-metadata-from-iphone-over-bluetooth-python)  
[3] [Now Playing Project in PHP](https://chorus.fm/features/articles/now-playing-my-raspberry-pi-weekend-project/)

## Next Features to implement
* Potentiometer to change volume
* Digital touch buttons on screen
```