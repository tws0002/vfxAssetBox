"""
HostManager reads the plugins directory, loads all plugins, and registers
their actions.
"""
import os
import imp
from assetbox.base.plugins.host import BaseHost
from assetbox.base.plugins import actions


PROJECT_FOLDER = os.path.dirname(os.path.dirname(__file__))


def find_plugins():
    """Query the plugin folder for plugins to load. Yields found locations."""
    plugins_folder = os.path.join(PROJECT_FOLDER, 'plugins').replace('\\', '/')

    if os.path.isdir(plugins_folder):
        plugins = os.listdir(plugins_folder)

        if plugins:
            for plugin in plugins:
                yield os.path.join(plugins_folder, plugin).replace('\\', '/')


class HostManager(object):
    """Primary hostmanager class, loads and stores all plugins."""

    def __init__(self):
        """Initialise the class, load the plugins."""

        plugins = find_plugins()
        self.host_app = None
        self.host_actions = actions.register_actions()
        self.host_filetypes = []

        for p in plugins:
            try:
                host_path = os.path.join(p, 'host.py').replace('\\', '/')
                name, ext = os.path.splitext(host_path)

                host = imp.load_source(name, host_path)
                host_app = host.HostApp()

                if host_app.inhost:
                    self.host_app = host_app
                    self.host_filetypes = self.host_app.filetypes

                    try:
                        action_path = os.path.join(p, 'actions.py').replace('\\', '/')
                        name, ext = os.path.splitext(action_path)
                        action = imp.load_source(name, action_path)
                        self.host_actions += action.register_actions()
                    except IOError:
                        print 'HostManager:IOError -- No actions found'

            except IOError, ioe:
                print 'HostManager:IOError -- ', ioe

            except ImportError, ime:
                print 'HostManager:ImportError -- ', ime

    def get_hostapp(self):
        """Return the host application."""
        if not self.host_app:
            self.host_app = BaseHost()
        return self.host_app

    def get_actions(self):
        """Return the actions associated with this host."""
        return self.host_actions

    def get_filetypes(self):
        """Return what filetypes this host supports."""
        return self.host_filetypes
