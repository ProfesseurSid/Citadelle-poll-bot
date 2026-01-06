#!/usr/bin/env python3
# coding: utf-8
from __future__ import unicode_literals

import sys
import os
import json
import samples_common  # Common bits used between samples
import logging
import datetime

from urllib import parse, request

from markdown2 import Markdown
from getpass import getpass

from matrix_client.client import MatrixClient
from matrix_client.room import Room
from matrix_client.api import MatrixHttpApi, MatrixRequestError
from requests.exceptions import MissingSchema

from random import randrange

request_prefix = "!giphy "
client = ""
matrix = ""
room_id = ""
api_key = ""

def send_markdown(self, text):
    self.send_html(Markdown().convert(text))

setattr(Room, 'send_markdown', send_markdown)

# Called when a message is recieved.
def on_message(room, event):
    global request_prefix

    #if event['type'] == "m.room.member":
    #    if event['membership'] == "join":
    #        print("{0} joined".format(event['content']['displayname']))
    #el
    if event['type'] == "m.room.message":
        if event['content']['msgtype'] == "m.text":
            print("{0}: {1}".format(event['sender'], event['content']['body'].encode('ascii', 'ignore')))
            if event['content']['body'].startswith(request_prefix):
                query = event['content']['body'][len(request_prefix):],
                handle_alpsys_bot(room, query, event['sender'])
    else:
        print(event['type'])


def handle_alpsys_bot(room, query, sender):
    global request_prefix
    global matrix
    global client
    global room_id
    global api_key
    
    if (query == "help"):
        display_help()
    else:
        url = "http://api.giphy.com/v1/gifs/search"
        count = 5
        params = parse.urlencode({
          "q": query,
          "api_key": api_key,
          "limit": count
        })

        with request.urlopen("".join((url, "?", params))) as response:
            data = json.loads(response.read())
            gifurl = data["data"][randrange(0, len(data["data"])-1)]["images"]["original"]["url"]
        
            with request.urlopen(gifurl) as gifBytes:
                mxurl = client.upload(gifBytes.read(),'image/gif')
                matrix.send_content(room_id, mxurl, (''.join(query) + '.gif').replace(' ','_'), 'm.image', {"mimetype": "image/gif", "thumbnail_info": {"mimetype": "image/png"}, "thumbnail_url": mxurl})

def display_help(room):
    room.send_text("Giphy Bot is running\nSyntax:\n\t!giphy <Command>\nCommand:\n\t<search content>\n\t\t\t\tSearches giphy for a gif\n\tdate\t\t\t\tSend server time\n\thelp\t\t\t\tDisplays this help")

def main():
    global client
    global matrix
    global room_id
    global api_key

    room_id = os.environ.get('ROOM')
    api_key = os.environ.get('GIPHY_API_KEY')
    bot_pwd=os.environ.get('BOT_PWD')
    bot_user=os.environ.get('BOT_USER')
    citadel_url=os.environ.get('CITADEL_URL');

    if bot_pwd is None:
        bot_pwd=getpass(prompt='Bot ('+bot_user+') password : ')

    client = MatrixClient(citadel_url)
    mxtoken = client.login(username=bot_user,password=bot_pwd)
    matrix = MatrixHttpApi(citadel_url, mxtoken)
    
    try:
        room = client.join_room(room_id)
    except MatrixRequestError as e:
        print(e)
        if e.code == 400:
            print("Room ID/Alias in the wrong format")
            sys.exit(11)
        else:
            print("Couldn't find room.")
            sys.exit(12)

    room.add_listener(on_message)
    print("Starting listener thread, bot ready")
    client.start_listener_thread()

    while True:
        msg = samples_common.get_input()
        if msg == "/quit":
            break
        else:
            room.send_text(msg)


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)

    main()
