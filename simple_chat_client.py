#!/usr/bin/env python3

import sys
import samples_common  # Common bits used between samples
import logging
import datetime

from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError
from requests.exceptions import MissingSchema


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
    cmd = msg.split()
    if len(cmd) <= 1:
        display_help()
    else:
        if cmd[1] == "help":
            display_help()
        elif cmd[1] == "date":
            room.send_text("Current server time: %s" % datetime.datetime.now())
        elif cmd[1] == "create":
            if len(cmd) >= 3:
                ,pollname = msg.split("create ",1)
                room.send_text("Create {0} poll attempt : Work in progress...".format(pollname))
            else:
                room.send_text("No poll name given. Anonymous polls will be handled in later versions.")
        elif cmd[1] == "vote":
            if len(cmd) >= 3:
                ,vote = msg.split("vote ",1)
                if vote == "yes":
                    room.send_text("Yes vote attempt : Work in progress...")
                elif vote == "no":
                    room.send_text("No vote attempt : Work in progress...")
                else:
                    room.send_text("{0} not understood. Please use yes or no.".format(vote))
            else:
                room.send_text("No vote value given.")
        else:
            room.send_text("Unknown command {0}. Try !help for help.".format(cmd[1]))
        
def display_help():
    room.send_text("Poll Bot is running\nCommand:\n\tdate\tSend server time")


def main():
    client = MatrixClient("$BASE_URL", token="$TOKEN", user_id="$USER_ID")

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
        room = client.join_room("$ROOM_ID")
    except MatrixRequestError as e:
        print(e)
        if e.code == 400:
            print("Room ID/Alias in the wrong format")
            sys.exit(11)
        else:
            print("Couldn't find room.")
            sys.exit(12)

    room.add_listener(on_message)
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
