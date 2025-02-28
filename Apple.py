from flask import Flask, render_template, request, redirect, session
import requests
import urllib.parse

#the Apple music portion of the code designed to pull user playlist and track info
#set up intro variables



#initialize a new home page / route for Apple

app = Flask(__name__)


@app.route('/apple_login')
def apple_home():
    return 'This is the apple login page!'


@app.route('/applecallback')
def apple_callback():
    return redirect('apple_playlists')

@app.route('/apple_playlists')
def show_apple_playlists():
    pass

def get_playlist_info():
    pass

def get_track_info():
    pass
