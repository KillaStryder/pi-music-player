import pygame
import glob, os
import tweepy
import smtplib
from bottle import route, run, response, view
from mutagen.id3 import ID3


GMAIL_USER = 'YOUR EMAIL'
GMAIL_PASS = 'YOUR PASSWORD'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587


ihost = '10.0.0.109'
gui = """<html>
	<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
	
	<title>Pi Music Player</title>
	<center/>
    <header id="head">
            <h1> <u><i>Pi Music Player<i> </h1>
	</header>
	<body style = "border: 2px solid red; height:500; width :350;">
			<div id=musicplayer >
				<div style="border-style: groove; border:1px solid black;background-color:powderblue; width = 200;"> """
songTitles = []
musiclist = []
volume = 0.5
indx = 0
direct = "/home/pi/PiMusicPlayer/Music/*.mp3"
musiclist = glob.glob(direct)

def send_email(recipient, subject, text):
    smtpserver = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(GMAIL_USER,GMAIL_PASS)
    header = "To:" + recipient + "\n"+ "From: " + GMAIL_USER
    header = header + "\n" + "Subject:" +  subject + "\n"
    msg = header + "\n" + text + "\n\n"
    smtpserver.sendmail(GMAIL_USER, recipient, msg)
    smtpserver.close()

def get_api(cfg):
  auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
  auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
  return tweepy.API(auth)
  

def getSongNames():
    global gui
    htmllist =""
    i = 1
    for music in musiclist:
        song = ID3(music)
        songinfo = song['TIT2'].text[0]
        songTitles.append(songinfo)
        htmllist += "<li style = \"list-style-type: none;\">  Track " + str(i) + " - " + songinfo  + "</li>"
        i+= 1
    gui += "<ul style = \"text-align: left;\">" + htmllist + """</ul></u>
        </div >
				<br>
				<div style = "background-color: orange">
				<button id = "prev" onclick = "window.location = '/prev'">
                                    <i class="material-icons">skip_previous</i>
				</button>
				<button id = "pause" onclick = "window.location.href = '/pause'">
                                    <i class="material-icons">pause</i>
				</button>	
				<button id = "stop" onclick = "window.location.href = '/stop'">
                                    <i class="material-icons">stop</i>
				</button>
				<button id = "resume" onclick = "window.location.href = '/play'">
                                    <i class="material-icons">play_circle_outline</i>
                                </button>
				<button id = "play" onclick = "window.location.href = '/play'">
                                    <i class="material-icons">play_arrow</i>
                                </button>
				<button id = "next" onclick = "window.location.href = '/next'">
                                    <i class="material-icons">skip_next</i>
				</button>
				</div>
				<br/>
				<button id = "volup" onclick = "window.location.href = '/volup'"><b>+</b></button>
				<button id = "tweet" onclick = "window.location.href= '/tweet'"><i class="fa fa-twitter">Tweet song</i></button>
                                <button id = "playlist" onclick = "window.location.href= '/playlist'"><b>Playlist</b></button>
                                <button id = "voldown" onclick = "window.location.href= '/voldown'"><b>-</b></button>
			</div>
	</body>
    </html>"""
		    
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.load(musiclist[indx])
    
    


@route('/tweet')
def tweet():
  cfg = { 
    "consumer_key"        : "CONSUMER KEY",
    "consumer_secret"     : "CONSUMER SECRET",
    "access_token"        : "ACCESS_TOKEN",
    "access_token_secret" : "ACCESS TOKEN SECRET " 
    }

  api = get_api(cfg)
  tweet = "Hi there, I am listening to " + songTitles[indx] + "on my Raspberry pi"
  status = api.update_status(status=tweet)
@route('/play')
def playSong():
    global indx
    global gui
    global musiclist
    pygame.mixer.music.play(-1)
    email = "Now Playing: " + songTitles[indx] + """

    sent via Pi Music Player"""
    send_email('marczuze@gmail.com', 'Now Playing:', email)
    return gui       
    
@route('/')
def index():
    global gui
    getSongNames()
    playSong()
    return gui

@route('/prev')
def prevSong():
    
    global indx
    if indx == 0:
        indx = len(musiclist) - 1
    else:
        indx -= 1
    pygame.mixer.music.load(musiclist[indx])
    if (indx == len(songTitles) -1):
        pygame.mixer.music.queue(musiclist[0])
    else:
        pygame.mixer.music.queue(musiclist[indx + 1])
    playSong()
    return gui
    
    
@route('/next')
def nextSong():
    global indx
    if indx == (len(musiclist) - 1):
        indx = 0
    else:
        indx += 1
    pygame.mixer.music.load(musiclist[indx])
    if (indx == len(songTitles) -1):
        pygame.mixer.music.queue(musiclist[0])
    else:
        pygame.mixer.music.queue(musiclist[indx + 1])
    playSong()
    return gui
    
@route('/stop')
def stopSong():
    pygame.mixer.music.stop()
    return gui
    
@route('/pause')
def pauseSong():
    pygame.mixer.music.pause()
    return gui
    
@route('/resume')    
def unPauseSong():
    pygame.mixer.music.unpause()
    return gui

@route('/volup')
def incVolume():
    global volume
    if volume < 1.0:
        volume += 0.1
        pygame.mixer.music.set_volume(volume)
    return gui


@route('/voldown')
def decVolume():
    global volume
    if volume > 0.0:
        volume -= 0.1
        pygame.mixer.music.set_volume(volume)
    return gui

@route('/playlist')
def sendPlaylist():
    playlist = ""
    for song in songTitles:
        playlist += song + "\n"
    email = "Here is your current music playlist available on your pi:" "\n\n" + playlist + "\n\n" + "sent via Pi Music Player"
    send_email('marczuze@gmail.com', 'Pi Playlist', email)
    return gui

run(host=ihost, port=60)

