import os

HOST = "irc.chat.twitch.tv"
PORT = 6667
NICK = os.environ.get('NICK')
PASS = os.environ.get('PASS')
CHANNEL = ""
SAVE_TIME = 30
CLIENT_ID = os.environ.get('CLIENT_ID')
BACKUP_DEEPNESS = 2 # 3 backup files
token = os.environ.get('TOKEN')
