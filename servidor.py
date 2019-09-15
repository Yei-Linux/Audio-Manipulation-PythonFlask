from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy

from pydub import AudioSegment;
from pydub.utils import  make_chunks;

import os
import numpy as np
import matplotlib.pyplot as plt
import librosa.display

#----------------------------#
#------SETTINGS OF FLASK-----#
#----------------------------#

__author__ = 'ibininja'
app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:''@localhost/audiobd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

target=os.path.join(APP_ROOT,'static/')

#----------------------------#
#------------MODELS----------#
#----------------------------#

#----------------------------#
#--------ENTITY USER---------#
#----------------------------#

class usuario(db.Model):

    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(30))
    contrasena=db.Column(db.String(30))
    correo=db.Column(db.String(30))

    def __init__(self,nombre,contrasena,correo):
        self.nombre=nombre
        self.contrasena=contrasena
        self.correo=correo

#----------------------------#
#--------ENTITY AUDIO--------#
#----------------------------#

class audio2(db.Model):

    id=db.Column(db.Integer,primary_key=True)
    archivo = db.Column(db.String(200))
    nombre=db.Column(db.String(30))

    def __init__(self,archivo,nombre):
        self.archivo=archivo
        self.nombre=nombre

#----------------------------#
#--------CREATING BD---------#
#----------------------------#

db.create_all()

#----------------------------#
#--------ADDING DATA---------#
#----------------------------#

admin=usuario('admin','admin','admin@hotmail.com')
guest=usuario('user','user','user@gmail.com')

db.session.add(admin)
db.session.add(guest)
db.session.commit()

#----------------------------#
#---------CONTROLLERS--------#
#----------------------------#

#----------------------------#
#------------INDEX-----------#
#----------------------------#

@app.route("/")
def main2():
        return render_template("login.html", title="data")

@app.route("/registrar")
def registrar():

    return render_template("index.html", title="data")

#----------------------------#
#-----------SIGN UP----------#
#----------------------------#

@app.route("/signUp", methods=["POST"])
def signUp():

    username = str(request.form["user"])
    password = str(request.form["password"])
    email = str(request.form["email"])

    data = usuario(username,password,email)
    db.session.add(data)
    db.session.commit()

    return redirect(url_for("login"))

#----------------------------#
#-----------SIGN IN----------#
#----------------------------#

@app.route("/login")
def login():

    return render_template("login.html", title="data")

#----------------------------#
#------VALIDATE SIGNIN-------#
#----------------------------#

@app.route("/checkUser", methods=["POST"])
def checkUser():

    username = str(request.form["user"])
    password = str(request.form["password"])

    newData=usuario.query.filter_by(nombre=username,contrasena=password).first()

    if newData:

        print(target)
        return render_template("upload.html")

    else:

        return render_template("login.html", title="data")

#----------------------------#
#------CONVERT MP3-WAV-------#
#----------------------------#

@app.route("/upload", methods=["GET","POST"])
def upload():


    #this is to verify that folder to upload to exists.

    music="";

    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    print(request.files.getlist("file"))

    for upload in request.files.getlist("file"):

        global filename

        print("{} is the file name".format(upload.filename))
        filename = upload.filename

        # GETTING THE EXTENSION OF FILE
        ext = os.path.splitext(filename)[1]

        if (ext == ".mp3") or (ext == ".wav"):

            print("File supported moving on...",filename)

            print(target+filename);

            src=target+filename;

            #SETTING WAV INTO MP3 FILENAME
            dst = src.replace(".mp3", ".wav")
            archivo=filename.replace(".mp3",".wav");

            #GET THE PURE SOUND
            sound = AudioSegment.from_mp3(src);

            #EXPORT INTO THIS DIRECTORY IN FORMAT WAV
            sound.export(dst, format="wav");

            # EXPORT INTO SERVER DIRECTORY IN FORMAT WAV
            sound.export("C:\\xampp\\htdocs\\"+archivo, format="wav");

            print("Accept incoming file:", archivo)
            print("Save it to:", dst)


            upload.save(dst)

            # ADD DATA
            file = request.files['file'];

            newFile = audio2(archivo=src, nombre=file.filename);
            db.session.add(newFile);
            db.session.commit();

            audio_data=audio2.query.all();

            for audio in audio_data:
                music=audio.nombre;

            #THE LAST REGISTER(COLUMN 'NAME')
            print(music);

            #SENDING ROUTE TO THE TEMPLATE
            music='/static/'+music;

        else:
            render_template("Error.html", message="Files uploaded are not supported...")

    return render_template("upload.html",music=music,duracion=255)

#----------------------------#
#---SPLIT IN EQUALS PARTS----#
#----------------------------#

@app.route("/upload2", methods=["POST"])
def upload2():

    cantidad=request.form['cantidad'];
    #fichero=request.form['archivo'];

    audio_data = audio2.query.all();
    for audio in audio_data:
        music = audio.nombre;

    fichero = target+music;

    print (fichero);

    dst = fichero.replace(".mp3", ".wav")

    sound = AudioSegment.from_file(dst)

    chunk_length_ms = (int(255) * 1000) / int(cantidad);
    chunks = make_chunks(sound, (chunk_length_ms));

    music2 = music.replace(".mp3", "")

    for i, chunk in enumerate(chunks):
        if (i != int(cantidad)):
            chunk_name = (music2+"{0}.wav").format(i);
            print("exporting", chunk_name);
            chunk.export(chunk_name, format="wav");
        else:
            break;

    return render_template("upload.html")


# ----------------------------#
# ------SPLIT BY SECONDS------#
# ----------------------------#

@app.route("/upload3", methods=["POST"])
def upload3():

    start = request.form['start1'];
    start2 = request.form['start2'];
    end = request.form['end1'];
    end2 = request.form['end2'];

    audio_data = audio2.query.all();
    for audio in audio_data:
        music = audio.nombre;

    fichero = target + music;

    dst = fichero.replace(".mp3", ".wav")

    sound = AudioSegment.from_file(dst)

    extract = sound[(int(start) * 1000):(int(end) * 1000)];
    extract2 = sound[(int(start2) * 1000):(int(end2) * 1000)];

    extract.export("1"+music, format="wav");
    extract2.export("2"+music, format="wav");

    return render_template("upload.html")

#----------------------------#
#--------CHANGE SPEED--------#
#----------------------------#

@app.route("/upload4", methods=["POST"])
def upload4():


    audio_data = audio2.query.all();
    for audio in audio_data:
        music = audio.nombre;

    fichero = target + music;
    cantidad=request.form['cantidad'];

    print(cantidad)

    l2 = cantidad.lstrip("X")
    src = fichero;
    sound = AudioSegment.from_file(src)
    l3 = float(l2)

    def speed_change(sound, speed=l2):
        sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * speed)
        })
        return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

    music2 = music.replace(".mp3", "")

    audio = speed_change(sound, l3)
    audio.export(target+music2 + "_aumentado.wav", format="wav")
    f = open(target+music2 + "_aumentado.wav", 'rb')
    f.read()

    param="/static/"+music2 + "_aumentado.wav";

    return render_template("upload.html",music=param)

#----------------------------#
#-PUT NOISE AT THE BEGINNING-#
#----------------------------#
@app.route("/upload5", methods=["POST"])
def upload5():

    audio_data = audio2.query.all();
    for audio in audio_data:
        music = audio.nombre;

    fichero =target + music;
    sound1 = AudioSegment.from_mp3(target+"explosion.mp3")
    sound2 = AudioSegment.from_mp3(fichero)

    music = music.replace(".mp3", "")

    combined_sounds = sound1 + sound2
    combined_sounds.export(target+music+"_beginningnoise.wav", format="wav")

    param = "/static/" +music+"_beginningnoise.wav";

    return render_template("upload.html",music=param)

#----------------------------#
#----PUT NOISE AT THE END----#
#----------------------------#

@app.route("/upload6", methods=["POST"])
def upload6():

    audio_data = audio2.query.all();
    for audio in audio_data:
        music = audio.nombre;

    fichero = target + music;
    sound1 = AudioSegment.from_mp3(target+"explosion.mp3")
    sound2 = AudioSegment.from_mp3(fichero)

    music = music.replace(".mp3", "")

    combined_sounds = sound2 + sound1;
    combined_sounds.export(target+music+"_endnoise.wav", format="wav")

    param = "/static/" + music+"_endnoise.wav";

    return render_template("upload.html",music=param)

#----------------------------#
#---GETTING THE BACKGROUND---#
#----------------------------#

@app.route("/upload7", methods=["POST"])
def upload7():

    audio_data = audio2.query.all();
    for audio in audio_data:
        music = audio.nombre;

    fichero = target + music;

    myAudioFile = fichero;
    sound_stereo = AudioSegment.from_file(myAudioFile, format="mp3")
    sound_monoL = sound_stereo.split_to_mono()[1]  # left
    sound_monoR = sound_stereo.split_to_mono()[0]  # right

    # Invert phase of the Right audio file
    sound_monoR_inv = sound_monoR.invert_phase()

    # Merge two L and R_inv files, this cancels out the centers(the vocals)
    sound_CentersOut = sound_monoL.overlay(sound_monoR_inv)

    music = music.replace(".mp3", "")

    # Export merged audio file
    myAudioFile_CentersOut = target+music+".wav"
    fh = sound_CentersOut.export(myAudioFile_CentersOut, format="wav")

    param = "/static/" + music+".wav";

    return render_template("upload.html",music=param)

#----------------------------#
#-----GETTING THE VOICE------#
#----------------------------#

@app.route("/upload8", methods=["POST"])
def upload8():

    audio_data = audio2.query.all();
    for audio in audio_data:
        music = audio.nombre;

    fichero = target + music;

    y, sr = librosa.load(fichero, duration=100)

    # And compute the spectrogram magnitude and phase
    S_full, phase = librosa.magphase(librosa.stft(y))

    idx = slice(*librosa.time_to_frames([30, 35], sr=sr))
    plt.figure(figsize=(12, 4))
    librosa.display.specshow(librosa.amplitude_to_db(S_full[:, idx], ref=np.max),
                             y_axis='log', x_axis='time', sr=sr)
    plt.colorbar()
    plt.tight_layout()

    S_filter = librosa.decompose.nn_filter(S_full,
                                           aggregate=np.median,
                                           metric='cosine',
                                           width=int(librosa.time_to_frames(2, sr=sr)))

    S_filter = np.minimum(S_full, S_filter)

    ##############################################
    # The raw filter output can be used as a mask,
    # but it sounds better if we use soft-masking.

    # We can also use a margin to reduce bleed between the vocals and instrumentation masks.
    # Note: the margins need not be equal for foreground and background separation
    margin_i, margin_v = 2, 10
    power = 2

    mask_i = librosa.util.softmask(S_filter,
                                   margin_i * (S_full - S_filter),
                                   power=power)

    mask_v = librosa.util.softmask(S_full - S_filter,
                                   margin_v * S_filter,
                                   power=power)

    # Once we have the masks, simply multiply them with the input spectrum
    # to separate the components

    S_foreground = mask_v * S_full
    S_background = mask_i * S_full

    ##########################################
    # Plot the same slice, but separated into its foreground and background

    # sphinx_gallery_thumbnail_number = 2

    plt.figure(figsize=(12, 8))
    plt.subplot(3, 1, 1)
    librosa.display.specshow(librosa.amplitude_to_db(S_full[:, idx], ref=np.max),
                             y_axis='log', sr=sr)
    plt.title('Full spectrum')
    plt.colorbar()

    plt.subplot(3, 1, 2)
    librosa.display.specshow(librosa.amplitude_to_db(S_background[:, idx], ref=np.max),
                             y_axis='log', sr=sr)
    plt.title('Background')
    plt.colorbar()
    plt.subplot(3, 1, 3)
    librosa.display.specshow(librosa.amplitude_to_db(S_foreground[:, idx], ref=np.max),
                             y_axis='log', x_axis='time', sr=sr)

    # -------VOZ--------#

    music = music.replace(".mp3", "");
    D_foreground = S_foreground * phase
    y_foreground = librosa.istft(D_foreground)
    librosa.output.write_wav(music+"_soloVoz.wav", y_foreground, sr)

    param = "/static/" + music+"_soloVoz.wav";

    return render_template("upload.html",music=param)

#----------------------------#
#---------SEND MUSIC---------#
#----------------------------#

@app.route('/upload/<filename>')
def send_music(dst):
    return send_from_directory("static", dst)

#----------------------------#
#------------MAIN------------#
#----------------------------#

if __name__ == "__main__":
    app.run(port=4555,debug=True)
