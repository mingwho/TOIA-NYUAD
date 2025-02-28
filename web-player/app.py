# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import sys
import pprint

sys.path.insert(0, '/web-player/')
pprint.pprint(sys.path)

import dialogue_manager
import StarMorphModules

import os
app = Flask(__name__)

import click
click.disable_unicode_literals_warning = True

characterModel = {}
currentAvatar = ""
currentSession = None

counter=0


# Home page where you go to select an avatar
@app.route('/')
def home():
    allAvatars = "";
    for filename in os.listdir('static/avatar-garden'):
        if os.path.isdir('static/avatar-garden/'+filename):
            print(filename)
            allAvatars += filename
            allAvatars += ","
    allAvatars = allAvatars[:-1] 
    return render_template('choose_avatar.html', avatars = allAvatars)


# Page where you go to select a language
@app.route('/<avatar>')
def with_avatar(avatar):
    print(avatar);
    return render_template('choose_language.html', avatar=avatar)


# Starting page for each character
@app.route('/<avatar>/<language>')
def with_language(avatar, language):
    global currentSession
    global characterModel
    global counter
    language = str(language).title()
    dialogue_manager.createModel(characterModel, currentSession, language, avatar)
    currentSession = dialogue_manager.create_new_session(avatar, language)
    return render_template('main.html', avatar=avatar, language=language)


@app.route('/<avatar>/<language>/recreate', methods=['POST'])
def recreate(avatar,language):
        currentSession = dialogue_manager.create_new_session(avatar, language)
        return 'OK'
        counter=0


# When avatar page receives a POST request
@app.route('/<avatar>/<language>', methods=['POST'])
def my_form_post(avatar,language):
    global currentSession
    global counter


    print(" querying")
    text = request.form['text']
    processed_text = text
    counter +=1
    response = dialogue_manager.findResponse(processed_text, characterModel[avatar], currentSession, counter)
    print("RESPONSE IS ", response)

    response_video_path = '/static/avatar-garden/' + avatar + '/videos/' + response.videoLink.strip('"');

    # response_subtitle_path = '/static/avatar-subtitle-timestamped/' + os.path.splitext(response.videoLink.strip('"'))[0] + '.vtt'

    response_subtitle_path = '/static/avatar-garden/' + avatar + '/subtitles/' + language + '_' + os.path.splitext(response.videoLink.strip('"'))[0] + '.vtt'

    print(response_subtitle_path);
    
    return render_template('main.html',
                   avatar=avatar,
                   avatar_video_path=response_video_path,
                   avatar_response=response.answer,
                   avatar_subtitle=response_subtitle_path,
                   query_text=processed_text,
                   language=language)


if __name__ == '__main__':
    avatar = ""
    StarMorphModules.read_config("dialogue-manager/CalimaStar_files/config_dana.xml")
    StarMorphModules.initialize_from_file("dialogue-manager/CalimaStar_files/almor-s31.db", "analyze")
    app.run(debug=True,threaded=True)