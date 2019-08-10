#!/usr/bin/env python3
import json
import settings
import urllib.parse as url_parse
from flask import Flask, request, make_response, Response

class MessageDispatcher(object):
    def __init__(self, app, client, adapter, plugins):
        self._app = app
        self._client = client
        self._adapter = adapter
        self._plugins = plugins

    def run(self, port):
        app = self._app
        client = self._client
        adapter = self._adapter
        plugins = self._plugins

        # for test
        @app.route("/test")
        def hello():
            return "Hello there!"

        # for verify
        @app.route("/events", methods=['POST'])
        def index():
            payload = request.form
            type = payload["type"]
            if type and type == "url_verification":
                challenge = payload["challenge"]
                result = jsonify({"challenge": challenge})
                response = make_response(result, 200)
                response.headers["content-type"] = "application/json"
                return response
            return make_response('', 200)

        # interactive_message
        @app.route("/interactive", methods=['POST'])
        def interactive():
            url = request.get_data()
            url_utf8 =  url_parse.unquote(url.decode(encoding="utf-8"))
            data = url_utf8.lstrip("payload=")
            payload = json.loads(data)
            self._my_interactive(payload)
            return make_response('', 200)

        # slash_command
        @app.route("/commands/<command_name>", methods=['POST'])
        def slash_command(command_name):
            payload = request.form
            func = plugins.commands['slash_command'][command_name]
            func(payload, client)
            return make_response('', 200)
        

        # respond_to, default_reply
        @adapter.on("app_mention")
        def respond_message(event_data: dict):
            event = event_data["event"]
            subtype = event.get("subtype")
            if subtype is None:
                self._my_respond(event)

        # listen_to
        @adapter.on("message")
        def listen_message(event_data: dict):
            event = event_data["event"]
            subtype = event.get("subtype")
            if subtype is None:
                self._my_speach(event)

        app.run(host='0.0.0.0', port=port, debug=True)

    def _my_interactive(self, payload: dict):
        client = self._client
        plugins = self._plugins

        for func, type in plugins.get_plugins('interactive_message'):
            if payload["type"] == type:
                func(payload, client)

    def _my_respond(self, event: dict):
        client = self._client
        plugins = self._plugins

        if not self._dispatch_handler('respond_to', event):
            self._default_reply(event)

        else:
            text = event.get("text")
            if text:
                for func, command in plugins.get_plugins('respond_to'):
                    if command in text:
                        func(event, client)

    def _my_speach(self, event: dict):
        client = self._client
        plugins = self._plugins

        text = event.get("text")
        if text:
            for func, command in plugins.get_plugins('listen_to'):
                if command in text:
                    func(event, client)

    def _default_reply(self, event: dict):
        client = self._client
        text = settings.DEFAULT_REPLY

        # TODO: make ErrorMessage better (e.g. list up all available commands)
        if text is None:
            try:
                received_command = event["text"].split()[1]
            except IndexError:
                received_command = ' '

            text = 'Bad command "{}"'.format(received_command)

        channel = event["channel"]
        client.api_call("chat.postMessage", channel=channel, text=text)

    def _dispatch_handler(self, category: str, event: dict) -> bool:
        plugins = self._plugins

        for func, command in plugins.get_plugins(category):
            if func and command in event["text"]:
                return True

        else:
            return False
