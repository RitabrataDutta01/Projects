from flask import Flask, render_template, send_from_directory, abort
import os
from werkzeug.utils import safe_join

app = Flask(__name__)

musicFolder = os.path.join(os.getcwd(), "music")

@app.route('/')
def index():

    songs = sorted([f for f in os.listdir(musicFolder)])
    return render_template('index.html', songs = songs)

@app.route('/stream/<path:song_name>')
def play(song_name):

    file_path = safe_join(musicFolder, song_name)
    if not file_path or not os.path.isfile(file_path):
        abort(404)

    return send_from_directory(musicFolder, song_name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)