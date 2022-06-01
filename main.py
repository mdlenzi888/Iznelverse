import urllib.error
import datetime as dt
import pytz
from character import Character
from character_list import characters
from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS, cross_origin


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

character_objects = {}
current_time = ""


# Fetch APIs on startup and anytime the Update button is pressed
def update_characters():
    global current_time

    for key in characters:
        char_object = Character(key)
        character_objects[key] = char_object
        print(char_object.name)
    central_time = pytz.timezone('US/Central')
    now = dt.datetime.now(central_time)
    current_time = now.strftime('%#m/%#d/%Y %#I:%M%p')


update_characters()


@app.route('/')
@cross_origin()
def home():
    return redirect(url_for('stats', character='bontoto'))


@app.route('/stats/<character>')
@cross_origin()
def stats(character):
    return render_template('index.html', character=character_objects[character], time=current_time)


@app.route('/update')
@cross_origin()
def update():
    try:
        update_characters()
    except urllib.error.URLError:
        pass
    return redirect(url_for('stats', character='bontoto', time=current_time))


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
