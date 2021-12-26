from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from deepface import DeepFace
import cv2
import numpy
import bcrypt
import os
import time

from db import connect_to_db

os.makedirs('uploads', exist_ok=True)

db = connect_to_db()

app = Flask(__name__)
app.secret_key = 'PRERONAAA'
app.config['UPLOAD_FOLDER'] = 'uploads'

default_password = b'123456'
success = 'success'
danger = 'danger'

moods = ['disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
languages = ['hindi', 'english', 'odia']


@app.route('/')
def index():
    if 'user' in session:
        users = db['admins'].find()
        return render_template('index.html',
                               user=session['user'],
                               users=users,
                               moods=moods,
                               languages=languages)
    return redirect(url_for('login'))


@app.route('/add-admin', methods=['POST'])
def add_admin():
    if 'user' not in session: return redirect(url_for('login'))
    try:
        email, name = request.form['email'], request.form['name']
        db['admins'].insert_one({
            'email':
            email.lower(),
            'name':
            name.lower(),
            'password':
            bcrypt.hashpw(default_password, bcrypt.gensalt())
        })
        flash("Admin successfully created.", success)
        return redirect('/')
    except:
        flash("Could not create admin.", danger)
        return redirect('/')


@app.route('/add-song', methods=['POST'])
def add_song():
    if 'user' not in session: return redirect(url_for('login'))
    try:
        name = request.form['name'].strip()
        mood = request.form['mood'].strip()
        language = request.form['language'].strip()
        artist = request.form['artist'].strip()
        lyrics = request.form['lyrics'].strip()
        description = request.form['description'].strip()
        cover = request.files['cover']
        song = request.files['song']

        cover_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            secure_filename(str(time.time()) + cover.filename))
        song_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            secure_filename(str(time.time()) + song.filename))

        db['songs'].insert_one({
            'name': name,
            'mood': mood,
            'language': language,
            'artist': artist,
            'lyrics': lyrics,
            'description': description,
            'cover': cover_path,
            'song': song_path
        })

        cover.save(cover_path)
        song.save(song_path)

        flash("Song successfully added.", success)
    except:
        flash("Could not add song.", danger)

    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        try:
            if request.form['login']:
                email, password = request.form['email'], request.form[
                    'password'].encode('utf-8')
                user = db['admins'].find_one({'email': email})
                if bcrypt.checkpw(password, user['password']):
                    user['_id'] = str(user['_id'])
                    session['user'] = user
                    return redirect('/')
                flash("Invalid Password", danger)
        except TypeError:
            flash("Invalid Email", danger)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        img = cv2.imdecode(
            numpy.fromstring(request.files['image'].read(), numpy.uint8),
            cv2.IMREAD_UNCHANGED)
        return DeepFace.analyze(img)


if __name__ == '__main__':
    app.run(port=8000, debug=True)