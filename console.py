import requests
from cfg import CLIENT_ID, token
from time import sleep
import os
import threading
from bot import Bot
import datetime
import dropbox


class Page():
    def __init__(self, channel, stream_data):
        self.channel = channel
        self.running = True
        self.messages = []

        self.bot = Bot(self.channel, self)
        self.paste_stream_start(stream_data)

        self.bot_thread = threading.Thread(target=self.run)
        self.bot_thread.start()

        self.save_thread = threading.Thread(target=self.save_messages)
        self.save_thread.start()
        self.viewers = ""
        self.game = ""

    def run(self):
        self.bot.read_chat()

    def close_tab(self):
        self.bot.running = False
        self.running = False
        self.bot_thread.join()
        print("{} bot stopped".format(self.channel))
        self.save_thread.join()

        dbx = dropbox.Dropbox(token)

        with open("channels/{}/{}_{}.txt".format(self.channel, self.channel, self.time), "rb") as f:
            dbx.files_upload(f.read(), '/channels/{}/{}_{}.txt'.format(self.channel, self.channel, self.time))

        os.remove("channels/{}/{}_{}.txt".format(self.channel, self.channel, self.time))

    def paste_stream_start(self, stream_data):
        d = datetime.datetime.strptime(stream_data[0]['started_at'], '%Y-%m-%dT%H:%M:%SZ')
        d = d.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
        self.time = d.strftime("%Y-%m-%d %H-%M-%S")

        message = "{0}:{1}: {2}".format(self.time, "he305bot", "Stream started")

        try:
            os.mkdir('channels/' + self.channel)
        except FileExistsError:
            print('Folder {} already exists'.format(self.channel))

        if not os.path.isfile("channels/{}/{}_{}.txt".format(self.channel, self.channel, self.time)):
            with open("channels/{}/{}_{}.txt".format(self.channel, self.channel, self.time), 'w',
                      encoding='utf8') as fp:
                fp.write(message)

    def print_message(self, message):
        pass
        # try:
        #     print(message + '\n')
        # except Exception:
        #     print("Some exception while printing out")

    def save(self):
        with open("channels/{}/{}_{}.txt".format(self.channel, self.channel, self.time), 'a', encoding='utf8') as fp:
            for msg in self.messages:
                try:
                    fp.write('\n'+msg)
                except Exception as ex:
                    print(msg + " CAN'T BE WRITTEN")
                    print(ex)

            fp.write("\n{}:{}: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"), "Viewer_counter", self.viewers))
            fp.write("\n{}:{}: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"), "Game_name", self.game))
        print("{}: SAVED {} MESSAGES FROM {}".format(datetime.datetime.now().strftime('%H:%M:%S'), len(self.messages), self.channel))

    def save_messages(self):
        while self.running:
            if len(self.messages) != 0:
                self.save()
                self.messages = []

            sleep(60)


class App:
    def __init__(self):
        self.streamers = []
        self.overwatch_thread = threading.Thread(target=self.overwatch)
        #self.overwatch_thread.daemon = True
        self.bots = []

        if os.path.isfile('streamers.txt'):
            self.load_data('streamers.txt')

    def load_data(self, fname):
        with open(fname, 'r', encoding="utf8") as f:
            self.streamers = [s.strip() for s in f.readlines()]
        print("Overwatched streams:\n" + '\n'.join(self.streamers))

        try:
            os.mkdir('channels')
        except FileExistsError:
            print('Folder already exists')

        self.overwatch_thread.start()

    def overwatch(self):
        headers = {
            'Client-ID': CLIENT_ID,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }

        while True:
            for streamer in self.streamers:
                stream_data = requests.get(
                    "https://api.twitch.tv/helix/streams?user_login=" + streamer.replace('_live', ''),
                    headers=headers).json()
                if 'error' in stream_data:
                    sleep(20)
                    continue

                if not stream_data['data'] and '_live' in streamer:

                    print("{} finished streaming, starting process stop".format(streamer.replace('_live', '')))
                    for b in self.bots:
                        if b.channel == streamer.replace('_live', ''):
                            finded = b
                            b.close_tab()
                            break
                    self.bots.remove(finded)

                    print("{} finished streaming".format(streamer.replace('_live', '')))
                    self.streamers[self.streamers.index(streamer)] = streamer.replace('_live', '')

                if stream_data['data'] and '_live' not in streamer:
                    print("{} stream is starting".format(streamer))

                    p = Page(streamer, stream_data['data'])
                    p.viewers = stream_data['data'][0]['viewer_count']

                    game_data = requests.get(
                        "https://api.twitch.tv/helix/games?id={}".format(stream_data['data'][0]['game_id']), \
                        headers=headers).json()
                    p.game = game_data['data'][0]['name']
                    self.bots.append(p)

                    self.streamers[self.streamers.index(streamer)] = streamer + '_live'

                if stream_data['data'] and '_live' in streamer:
                    for p in self.bots:
                        if p.channel == streamer.replace('_live', ''):
                            p.viewers = stream_data['data'][0]['viewer_count']
                            game_data = requests.get(
                                "https://api.twitch.tv/helix/games?id={}".format(stream_data['data'][0]['game_id']), \
                                headers=headers).json()
                            p.game = game_data['data'][0]['name']
                            break

            print("Last check: {}".format(datetime.datetime.now().strftime('%H:%M:%S')))
            sleep(60)

# def main():
#
#     if os.path.isfile('streamers.txt'):
#         with open('streamers.txt', mode='r', encoding='utf8') as f:
#             streamers = [s.strip() for s in f.readlines()]
#
#     print("Overwatched streamers:")
#     for streamer in streamers:
#         print(streamer)
#
#     headers = {
#         'Client-ID': CLIENT_ID,
#         'Accept': 'application/vnd.twitchtv.v5+json'
#     }
#
#     tabs = []
#     while True:
#         for streamer in self.streamers:
#             stream_data = requests.get(
#                 "https://api.twitch.tv/helix/streams?user_login=" + streamer.replace('_live', ''),
#                 headers=headers).json()
#             if 'error' in stream_data:
#                 sleep(20)
#                 continue
#
#             if not stream_data['data'] and '_live' in streamer:
#
#                 print("{} finished streaming, starting process stop".format(streamer.replace('_live', '')))
#                 for i, p in enumerate(tabs):
#                     if p.channel == streamer.replace('_live', ''):
#                         self.frames.forget(i)
#                         finded = p
#                         p.close_tab()
#                         break
#                 tabs.remove(finded)
#
#                 print("{} finished streaming".format(streamer.replace('_live', '')))
#                 self.streamers[self.streamers.index(streamer)] = streamer.replace('_live', '')
#
#             if stream_data['data'] and not '_live' in streamer:
#                 print("{} stream is starting".format(streamer))
#
#                 p = Page(streamer, stream_data['data'], self.frames)
#                 p.viewers['text'] = "Viewers: {}".format(stream_data['data'][0]['viewer_count'])
#
#                 game_data = requests.get(
#                     "https://api.twitch.tv/helix/games?id={}".format(stream_data['data'][0]['game_id']), \
#                     headers=headers).json()
#                 p.game['text'] = "Game: {}".format(game_data['data'][0]['name'])
#                 self.frames.add(p, text=streamer.replace('_live', ''))
#                 tabs.append(p)
#
#                 self.streamers[self.streamers.index(streamer)] = streamer + '_live'
#
#             streamers_str = '\n'.join(self.streamers)
#             self.streamers_label['text'] = "Overwatched streams:\n" + streamers_str
#
#             if stream_data['data'] and '_live' in streamer:
#                 for i, p in enumerate(tabs):
#                     if p.channel == streamer.replace('_live', ''):
#                         p.viewers['text'] = "Viewers: {}".format(stream_data['data'][0]['viewer_count'])
#                         game_data = requests.get(
#                             "https://api.twitch.tv/helix/games?id={}".format(stream_data['data'][0]['game_id']), \
#                             headers=headers).json()
#                         p.game['text'] = "Game: {}".format(game_data['data'][0]['name'])
#                         break
#
#         print("Last check: {}".format(datetime.datetime.now().strftime('%H:%M:%S')))
#         self.update_status['text'] = "Last check: {}".format(datetime.datetime.now().strftime('%H:%M:%S'))
#         sleep(60)

if __name__ == "__main__":
    a = App()