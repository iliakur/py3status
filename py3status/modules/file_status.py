# -*- coding: utf-8 -*-
"""
Display if files or directories exists.

Configuration parameters:
    cache_timeout: refresh interval for this module (default 10)
    format: display format for this module
        (default '\?color=paths [\?if=paths ●|■]')
    format_path: format for paths (default '{basename}')
    format_path_separator: show separator if more than one (default ' ')
    path: specify a string or a list of paths to check (default None)
    thresholds: specify color thresholds to use
        (default [(0, 'bad'), (1, 'good')])

Format placeholders:
    {format_path} format for paths
    {paths} number of paths, eg 1, 2, 3

format_path placeholders:
    {basename} basename of pathname
    {pathname} pathname

Color options:
    color_bad: files or directories does not exist
    color_good: files or directories exists

Color thresholds:
    format:
        paths: print a color based on the number of paths

Examples:
```
# add multiple paths with wildcard or with pathnames
file_status {
    path = ['/tmp/test*', '~user/test1', '~/Videos/*.mp4']
}

# colorize basenames
file_status {
    path = ['~/.config/i3/modules/*.py']
    format = '{format_path}'
    format_path = '\?color=good {basename}'
    format_path_separator = ', '
}
```

@author obb, Moritz Lüdecke, Cyril Levis (@cyrinux)

SAMPLE OUTPUT
{'color': '#00FF00', 'full_text': u'\u25cf'}

missing
{'color': '#FF0000', 'full_text': u'\u25a0'}
"""

from glob import glob
from os.path import basename, expanduser

STRING_NO_PATH = 'missing path'
DEFAULT_FORMAT = u'\?color=paths [\?if=paths \u25cf|\u25a0]'


class Py3status:
    """
    """
    # available configuration parameters
    cache_timeout = 10
    format = DEFAULT_FORMAT
    format_path = u'{basename}'
    format_path_separator = u' '
    path = None
    thresholds = [(0, 'bad'), (1, 'good')]

    class Meta:
        deprecated = {
            'rename': [
                {
                    'param': 'format_available',
                    'new': 'icon_available',
                    'msg': 'obsolete parameter use `icon_available`'
                },
                {
                    'param': 'format_unavailable',
                    'new': 'icon_unavailable',
                    'msg': 'obsolete parameter use `icon_unavailable`'
                },
            ],
        }

    def post_config_hook(self):
        if not self.path:
            raise Exception(STRING_NO_PATH)

        # deprecation
        self.on = getattr(self, 'icon_available', None)
        self.off = getattr(self, 'icon_unavailable', None)
        if self.format == DEFAULT_FORMAT and (self.on or self.off):
            self.format = u'\?if=paths {}|{}'.format(self.on or u'\u25cf', self.off or u'\u25a0')
            new_format = u'\?color=paths [\?if=paths {}|{}]'
            self.format = new_format.format(self.on or u'\u25cf', self.off or u'\u25a0')
            msg = 'DEPRECATION: you are using old style configuration '
            msg += 'parameters you should update to use the new format.'
            self.py3.log(msg)

        # convert str to list + expand path
        if not isinstance(self.path, list):
            self.path = [self.path]
        self.path = list(map(expanduser, self.path))

        self.init = {'format_path': []}
        if self.py3.format_contains(self.format, 'format_path'):
            self.init['format_path'] = self.py3.get_placeholders_list(self.format_path)

    def file_status(self):
        # init datas
        paths = sorted([files for path in self.path for files in glob(path)])
        count_path = len(paths)
        format_path = None
        icon = None

        # format icon
        if self.py3.format_contains(self.format, 'icon'):
            if count_path > 0:
                icon = self.on
            else:
                icon = self.off

        # format paths
        if self.init['format_path']:
            new_data = []
            format_path_separator = self.py3.safe_format(
                self.format_path_separator)

            for pathname in paths:
                path = {}
                for key in self.init['format_path']:
                    if key == 'basename':
                        value = basename(pathname)
                    elif key == 'pathname':
                        value = pathname
                    else:
                        continue
                    path[key] = self.py3.safe_format(value)
                new_data.append(self.py3.safe_format(self.format_path, path))

            format_path = self.py3.composite_join(
                format_path_separator, new_data
            )

        if self.thresholds:
            self.py3.threshold_get_color(count_path, 'paths')

        return {
            'cached_until':
            self.py3.time_in(self.cache_timeout),
            'full_text': self.py3.safe_format(
                self.format, {
                    'paths': count_path,
                    'format_path': format_path,
                    'icon': icon
                }
            )
        }


if __name__ == "__main__":
    """
    Run module in test mode.
    """
    from py3status.module_test import module_test
    module_test(Py3status)
