import urllib.error
import datetime as dt
from character import Character
from character_list import characters
from flask import Flask, render_template, redirect, url_for


app = Flask(__name__)

character_objects = {}
current_time = ""


# Fetch APIs on startup and anytime the Update button is pressed
def update_characters():
    global current_time

    now = dt.datetime.now()
    current_time = now.strftime('%#m/%#d/%Y %#I:%M%p')
    for key in characters:
        char_object = Character(key)
        character_objects[key] = char_object
        print(char_object.name)


update_characters()


@app.route('/')
def home():
    return redirect(url_for('stats', character='bontoto'))


@app.route('/stats/<character>')
def stats(character):
    return render_template('index.html', character=character_objects[character], time=current_time)


@app.route('/update')
def update():
    try:
        update_characters()
    except urllib.error.URLError:
        pass
    return redirect(url_for('stats', character='bontoto', time=current_time))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
