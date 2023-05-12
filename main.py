import urllib.error
import datetime as dt
import pytz
from character import Character
from character_list import characters
from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS, cross_origin
from flask_caching import Cache

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'  # Key = function inputs, Value = response

cache = Cache()
cache.init_app(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

character_objects = {}


# Fetch APIs on startup and anytime the Update button is pressed
def update_characters():
    for key in characters:
        update_character(key)


# @cache.cached(timeout=1209600, key_prefix='update')  # store cache for 2 weeks
def update_character(name):
    char_object = Character(name)

    central_time = pytz.timezone('US/Central')
    now = dt.datetime.now(central_time)
    current_time = now.strftime('%#m/%#d/%Y %#I:%M%p')

    character_objects[name] = [char_object, current_time]
    print(char_object.name)


update_characters()


@app.route('/')
@cross_origin()
def home():
    return redirect(url_for('stats', character='finito'))


@app.route('/stats/<character>')
@cross_origin()
def stats(character):
    return render_template('index.html', character=character_objects[character][0],
                           time=character_objects[character][1],
                           character_list=characters)


@app.route('/stats/<character>/update')
@cross_origin()
def update(character):
    try:
        update_character(character)
    except (urllib.error.URLError, EOFError):
        pass
    return redirect(url_for('stats', character=character, time=character_objects[character][1]))


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
