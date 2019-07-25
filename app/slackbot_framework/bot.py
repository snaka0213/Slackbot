#!/usr/bin/env python3
import settings
from flask import Flask
from slackclient import SlackClient
from slackeventsapi import SlackEventAdapter
from slackbot_framework.manager import PluginsManager
from slackbot_framework.dispatcher import MessageDispatcher

class Bot(object):
    def __init__(self):
        self._app = Flask(__name__)
        self._client = SlackClient(settings.SLACK_BOT_TOKEN)
        self._adapter = SlackEventAdapter(
            settings.SIGINING_SECRET, "/events", self._app
        )
        self._plugins = PluginsManager()
        self._dispatcher = MessageDispatcher(
            self._app, self._client, self._adapter, self._plugins
        )

    def run(self):
        self._plugins.init_plugins()
        self._dispatcher.run(settings.PORT)

# TODO: make use of flags, regular expression
def listen_to(command: str, flags = 0):
    def wrapper(func):
        PluginsManager.commands['listen_to'][command] = func
        return func
    return wrapper

def respond_to(command: str, flags = 0):
    def wrapper(func):
        PluginsManager.commands['respond_to'][command] = func
        return func
    return wrapper

def interactive_message(type: str):
    def wrapper(func):
        PluginsManager.commands['interactive_message'][type] = func
        return func
    return wrapper

def slash_command(path: str):
    def wrapper(func):
        PluginsManager.commands['slash_command'][path] = func
        return func
    return wrapper

# TODO: make use of this
def default_reply(*args, **kwargs):
    invoked = bool(not args or kwargs)
    matchstr = kwargs.pop('matchstr', r'^.*$')
    flags = kwargs.pop('flags', 0)

    if not invoked:
        func = args[0]

    def wrapper(func):
        PluginsManager.commnads['default_reply'][
            re.compile(matchstr, flags)] = func
        return func

    return wrapper if invoked else wrapper(func)
