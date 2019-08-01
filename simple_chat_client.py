#!/usr/bin/env python3
# coding: utf-8
from __future__ import unicode_literals

import sys
import os
import samples_common  # Common bits used between samples
import logging
import datetime

from markdown2 import Markdown

from matrix_client.client import MatrixClient
from matrix_client.room import Room
from matrix_client.api import MatrixRequestError
from requests.exceptions import MissingSchema

sondages = {}
pollname = ""

def send_markdown(self, text):
    self.send_html(Markdown().convert(text))

setattr(Room, 'send_markdown', send_markdown)

# Called when a message is recieved.
def on_message(room, event):
    if event['type'] == "m.room.member":
        if event['membership'] == "join":
            print("{0} joined".format(event['content']['displayname']))
    elif event['type'] == "m.room.message":
        if event['content']['msgtype'] == "m.text":
            print("{0}: {1}".format(event['sender'], event['content']['body']))
            if event['content']['body'].startswith( "!poll" ):
                handle_alpsys_bot(room, event['content']['body'], event['sender'])
    else:
        print(event['type'])


def handle_alpsys_bot(room, msg, sender):
    global sondages
    global pollname
    cmd = msg.split()
    if len(cmd) <= 1:
        display_help(room)
    else:
        #ASKING 4 HELP#
        if cmd[1].lower() == "help":
            display_help(room)
            
        #ASKING 4 DATE#
        elif cmd[1].lower() == "date":
            room.send_text("Current server time: %s" % datetime.datetime.now())

        #POLL CREATION#
        elif cmd[1].lower() == "create":
            #For now, only 1 poll is handled#
            if sondages and len(sondages) > 0:
                room.send_markdown("Poll **{0}** currently open. Multi-polls will be handled in later versions.".format(pollname))

            #Named poll#
            elif len(cmd) >= 3:
                trash,pollname = msg.split("create ",1)
                sondages["name"] = pollname
                sondages["{0}".format(pollname)] = {}
                room.send_markdown("Poll **{0}** created.".format(pollname))

            #Anonymous poll#
            else:
                room.send_text("No poll name given. Anonymous polls will be handled in later versions.")

        #VOTES#
        elif cmd[1].lower() == "vote":
            if not sondages or len(sondages) == 0:
                room.send_text("No poll created...")
            elif len(cmd) >= 3:
                trash,vote = msg.split("vote ",1)

                #Yes#
                if vote.lower() == "yes":
                    sondages[pollname][sender] = 1
                    results=count(sondages[pollname])
                    room.send_markdown("Poll **{0}**:\nScores are now {1} for, {2} against.".format(pollname, results["yes"], results["no"]))

                #No#
                elif vote.lower() == "no":
                    sondages[pollname][sender] = 0
                    results=count(sondages[pollname])
                    room.send_text("Scores are now {1} for, {2} against.".format(pollname, results["yes"], results["no"]))

                #Unknown#
                else:
                    room.send_text("{0} not understood. Please use yes or no.".format(vote))
            else:
                room.send_text("No vote value given.")

        #ASKING 4 SCORES#
        elif cmd[1].lower() == "score" or cmd[1].lower() == "scores":
            if not sondages or len(sondages) == 0:
                room.send_text("No poll created...")
            results=count(sondages[pollname])
            room.send_markdown("Scores for **{0}** poll:\nScores are {1} for, {2} against.".format(pollname, results["yes"], results["no"]))

        #POLL CLOSING#
        elif cmd[1].lower() == "close":
            results=count(sondages[pollname])
            room.send_markdown("Closing **{0}** poll.\nResults are {1} for, {2} against.".format(pollname, results["yes"], results["no"]))
            sondages={}
        else:
            room.send_text("Unknown command {0}. Try \"!poll help\" for help.".format(cmd[1]))
        
def count(sondage):
    yes=0
    no=0
    
    for user in sondage:
        yes += sondage[user]
        no += (1+sondage[user]) % 2

    return {"yes":yes,"no":no}

def display_help(room):
    room.send_text("Poll Bot is running\nCommand:\n\tclose\t\t\t\tClose current poll and display results\n\tcreate <pollname>\tCreate the poll\n\tdate\t\t\t\tSend server time\n\thelp\t\t\t\tDisplays this help\n\tscore\t\t\t\tDisplay scores of current poll\n\tvote <yes/no>\t\tVote for current poll")


def main():
    client = MatrixClient(os.environ.get('BASE_URL'), token=os.environ.get('TOKEN'), user_id=os.environ.get('USER_ID'))

    # try:
    #     client.login_with_password(username, password)
    # except MatrixRequestError as e:
    #     print(e)
    #     if e.code == 403:
    #         print("Bad username or password.")
    #         sys.exit(4)
    #     else:
    #         print("Check your sever details are correct.")
    #         sys.exit(2)
    # except MissingSchema as e:
    #     print("Bad URL format.")
    #     print(e)
    #     sys.exit(3)

    try:
        room = client.join_room(os.environ.get('ROOM_ID'))
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
    # host, username, password = samples_common.get_user_details(sys.argv)

    # if len(sys.argv) > 4:
    #     room_id_alias = sys.argv[4]
    # else:
    #     room_id_alias = samples_common.get_input("Room ID/Alias: ")

    main()
