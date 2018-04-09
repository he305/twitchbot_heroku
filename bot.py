import cfg
import socket
import re
import datetime


class Bot:
    def __init__(self, channel, parent):
        self.channel = channel
        self.parent = parent
        self.running = True
        self.s = socket.socket()

    def read_chat(self):
        self.s.connect((cfg.HOST, cfg.PORT))
        self.s.settimeout(120)
        self.s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
        self.s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
        self.s.send("JOIN #{}\r\n".format(self.channel).encode("utf-8"))

        chat_message = re.compile(r":?\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

        # global ignore_offline
        # if not ignore_offline:
        #     check_online_thread.start()
        while self.running:
            try:
                response = self.s.recv(2048).decode("utf-8")
                if response == "PING :tmi.twitch.tv\r\n":
                    self.s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                else:
                    data = response.splitlines()
                    for res in data:
                        message = chat_message.sub("", res).strip()
                        if re.search(r"\w+", res) is not None:
                            full_message = "{0}: {1}".format(re.search(r"\w+", res).group(0), message)
                            
                            if not "tmi" in full_message:
                                time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                                self.parent.print_message("{0}:{1}".format(time, full_message))
                                self.parent.messages.append("{0}:{1}".format(time, full_message))
            except UnicodeDecodeError as ex:
                print('*'*20)
                print(ex)
                print(self.channel)
                response = 0
                print('*'*20)
            except socket.timeout as ex:
                print('Socket timeout at {}'.format(self.channel))

