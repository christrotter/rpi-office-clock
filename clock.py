#!/usr/bin/python
import time
import threading
import datetime
import json
import cStringIO
import pygame
import base64

from MatrixWrapper import MatrixWrapper
from settings import conf
from Singleton import Singleton
from netifaces import interfaces, ifaddresses, AF_INET

@Singleton
class UpdateMatrix:
    def __init__(self):
        self.lock = threading.Lock()

    def message(self, message):
        self.lock.acquire()
        MatrixWrapper.Instance().drawText(message)
        self.lock.release()

    def animation(self, image, loops = 1):
        self.lock.acquire()
        print "Running Animation", loops, "time(s)"
        MatrixWrapper.Instance().drawAnimationFromBase64(image, loops)
        self.lock.release()
    def savedanimation(self, image):
        self.lock.acquire()
        print "Running Presaved Animation ", image
        MatrixWrapper.Instance().drawAnimationFromFile(image)
        self.lock.release()

    def image(self, image, duration = 1000):
        self.lock.acquire()
        MatrixWrapper.Instance().drawImageFromBase64(image, duration)
        self.lock.release()

    def default(self):
        self.lock.acquire()
        redis = conf["r"]
        current_score = redis.get('current_score')
        if current_score is None:
            MatrixWrapper.Instance().drawTime()
        else:
            score_data = json.loads(current_score)
            MatrixWrapper.Instance().drawScore(
                score_data["left"],
                score_data["right"],
                score_data["arrow"],
                (
                    score_data["leftColour"][0],
                    score_data["leftColour"][1],
                    score_data["leftColour"][2]
                ),
                (
                    score_data["rightColour"][0],
                    score_data["rightColour"][1],
                    score_data["rightColour"][2]
                ),
            )
        self.lock.release()

# Define listener thread for redis notifications
class Listener(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.redis = conf["r"]
        self.pubsub = self.redis.pubsub()
        self.pubsub.psubscribe('ch-*')

    def run(self):
        for item in self.pubsub.listen():
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            print st, "- Got Message on", item['channel']

            # Do actual operations on the display
            if item['channel'] == 'ch-messages':
                message = json.loads(item['data'])
                UpdateMatrix.Instance().message(message)
            if item['channel'] == 'ch-images':
                image = json.loads(item['data'])
                UpdateMatrix.Instance().image(image["data"], image["duration"])
            if item['channel'] == 'ch-animation':
                image = json.loads(item['data'])
                UpdateMatrix.Instance().animation(image["data"], image["loops"])
            if item['channel'] == 'ch-audio':
                sound_string = cStringIO.StringIO(base64.b64decode(item['data']))
                pygame.mixer.init()
                pygame.mixer.music.load(sound_string)
                pygame.mixer.music.play()
            if item['channel'] == 'ch-savedanim':
                UpdateMatrix.Instance().savedanimation(item["data"])

if __name__ == "__main__":
    r = conf["r"]
    client = Listener()
    client.daemon = True
    client.start()
    for ifaceName in interfaces():
        addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
        interfaceText = '%s: %s' % (ifaceName, ', '.join(addresses))
        UpdateMatrix.Instance().message([{'text': interfaceText, "colour": (200, 200, 200)}])
    while True:
        UpdateMatrix.Instance().default()
        time.sleep(0.25)

# vim: ts=4 sw=4 expandtab