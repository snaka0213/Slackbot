#!/usr/bin/env python3
import os
import settings
from glob import glob
from importlib import import_module
from importlib.util import find_spec

class PluginsManager(object):
    commands = {
        'listen_to': {},
        'respond_to': {},
        'slash_command': {},
        'default_reply': {},
        'interactive_message': {}
    }

    def __init__(self):
        pass

    def init_plugins(self):
        plugins = None
        if hasattr(settings, 'PLUGINS'):
            plugins = settings.PLUGINS

        for plugin in plugins:
            self._load_plugins(plugin)

    def _load_plugins(self, plugin):
        module_list = [plugin]
        path_name = find_spec(plugin)
        try:
            path_name = path_name.submodule_search_locations[0]
        except TypeError:
            path_name = path_name.origin

        if not path_name.endswith('.py'):
            module_list = glob('{}/[!_]*.py'.format(path_name))
            module_list = ['.'.join((plugin, os.path.split(f)[-1][:-3])) for f in module_list]

        for module in module_list:
            import_module(module)

    def get_plugins(self, category):
        for matcher in self.commands[category]:
            yield self.commands[category][matcher], matcher
