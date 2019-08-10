#!/usr/bin/env python3
import slack
from slackclient import SlackClient
from slackbot.bot import listen_to
from slackbot.bot import respond_to

@listen_to("bye")
def bye_send(event: dict, client: SlackClient):
    text = "Bye..."

    channel = event["channel"]
    client.api_call("chat.postMessage", channel=channel, text=text)
    return

@respond_to("hello")
def hello_reply(event: dict, client: SlackClient):
    text = "Hello <@{}>! :tada:".format(event["user"])

    channel = event["channel"]
    client.api_call("chat.postMessage", channel=channel, text=text)
    return

