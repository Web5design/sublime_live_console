
import os
import os.path
import json
import zipfile

import sublime
import sublime_plugin

from .sublime_live import UpdateLiveViewCommand, LiveEventListener
from .sublime_live import LiveView, LiveRegion


class LiveConsole(LiveView):
    def __init__(self, config):
        super().__init__(name=config['name'])

        package_name = os.path.basename(os.path.dirname(
                                            os.path.abspath(__file__)))
        package_name = package_name if not package_name.endswith(
                            '.sublime-package') else package_name[:-16]
        path = 'Packages/%s/live_console.tmTheme' % package_name
        settings = {
            'color_scheme': path
        }
        settings.update(config)
        del settings['layout']
        del settings['name']
        self.apply_settings(settings)

        self.config = config
        self.draw()

    def draw(self):
        items = self.config['layout']
        self.run_command('update_live_view',
                                {'data': self.config['name'] + '\n'})

        for item in items:
            if isinstance(item, str):
                self.run_command('update_live_view',
                                 {'data': item, 'start': self.size()})
            elif isinstance(item, dict):
                if item.get('hr'):
                    self.run_command('update_live_view',
                                {'data': '-' * item.get('width', 50),
                                                'start': self.size()})
                elif item.get('caption'):
                    start = self.size()
                    self.run_command('update_live_view',
                                            {'data': item['caption'],
                                                'start': self.size()})
                    if 'command' in item:
                        end = self.size()
                        def process(command, args, scope, scope_clicked):
                            def inner_process(live_region):
                                if scope_clicked is not None:
                                    live_region = self.get_regions(live_region.key)[0]
                                    self.erase_regions(live_region.key)
                                    self.add_regions('LiveRegion%s' % id(live_region),
                                                                [live_region], scope_clicked, '',
                                                                sublime.DRAW_NO_OUTLINE)
                                live_region.live_view.window().run_command(command, args)
                                if scope_clicked is not None:
                                    def call():
                                        self.erase_regions(live_region.key)
                                        self.add_regions('LiveRegion%s' % id(live_region),
                                                                         [live_region], scope, '',
                                                                         sublime.DRAW_NO_OUTLINE)
                                    sublime.set_timeout_async(call, 200)
                            return inner_process
                        scope = item.get('scope', self.config.get('default_command_scope',
                                                                                    'button.grey'))
                        process = process(
                            item['command'],
                            item.get('args', {}),
                            scope,
                            item.get('scope_clicked', self.config.get('scope_clicked', None))
                        )
                        kwargs = {'process': process}
                        live_region = LiveRegion(start, end, **kwargs)
                        self.add_regions('LiveRegion%s' % id(live_region), [live_region], scope,
                                                                    '', sublime.DRAW_NO_OUTLINE)
                if item.get('break'):
                    self.run_command('update_live_view', {'data': '\n' * item.get('count', 1),
                                                                            'start': self.size()})


class LiveConsoleCommand(sublime_plugin.WindowCommand):
    """
    List all consoles or load if only one:
    window.run_command('live_console')
    Load this console:
    window.run_command('live_console', {'file_name': 'User.sublime-console'})
    List all consoles from this package, or load if only one:
    window.run_command('live_console', {'package_name': 'User'})
    Load this console from this package:
    window.run_command('live_console', {'file_name': 'User.sublime-console', 'package_name': 'User'})
    """
    def get_configs_from_packages(self):
        configs = {}
        for packages_path in [sublime.installed_packages_path(), sublime.packages_path()]:
            for package_name in os.listdir(packages_path):
                package_path = os.path.join(packages_path, package_name)
                configs.update(self.get_configs_from_package(package_path))
        configs.update(self.get_configs_from_package('User'))
        return configs

    def get_configs_from_package(self, package_path):
        if not os.path.exists(package_path):
            tmp_package_path = os.path.join(sublime.packages_path(), package_path)
            if not os.path.exists(tmp_package_path):
                tmp_package_path = os.path.join(sublime.installed_packages_path(), package_path)
            package_path = tmp_package_path
        configs = {}
        if os.path.exists(package_path):
            if os.path.isdir(package_path):
                configs.update(self.get_configs_from_package_folder(package_path))
            elif package_path.endswith('.sublime-package'):
                configs.update(self.get_configs_from_package_zip(package_path))
        return configs

    def get_configs_from_package_folder(self, package_path):
        configs = {}
        for item in os.listdir(package_path):
            item_path = os.path.join(package_path, item)
            if os.path.isfile(item_path) and item_path.endswith('.sublime-console'):
                with open(item_path, 'r') as config_file:
                    configs[item[:-16]] = json.load(config_file)
        return configs

    def get_configs_from_package_zip(self, package_path):
        configs = {}
        with zipfile.ZipFile(package_path) as package_file:
            for item in package_file.namelist():
                if item.endswith('.sublime-console') and (not '/' in item or not '\\' in item):
                    configs[item[:-16]] = json.loads(package_file.read(item).decode('utf8'))
        return configs

    def run(self, file_name=None, package_name=None):
        if file_name is not None and file_name.endswith('.sublime-console'):
            file_name = file_name[:-16]
        if package_name is None:
            configs = self.get_configs_from_packages()
        else:
            configs = self.get_configs_from_package(package_name)
        if file_name is not None and file_name in configs:
            LiveConsole(configs[file_name])
        elif len(configs) == 1:
            LiveConsole(configs.popitem()[1])
        elif not configs:
            sublime.message_dialog('No console configurations found.')
        else:
            console_names = ['%s (%s)' % (v['name'], n)  for n ,v in configs.items()]
            console_names.sort()
            self.configs = [x for x in configs.values()]
            self.window.show_quick_panel(
                console_names,
                self.on_done
            )

    def on_done(self, selected):
        if selected == -1:
            return
        config = self.configs[selected]
        LiveConsole(config)
