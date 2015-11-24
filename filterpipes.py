# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This is not an official Google product.

"""FilterPipes Library.

This module abstracts many of the details for dealing with the
SublimeText API. Several generic commands are provided, which can
be further customized for additional behavior.

Part of the FilterPipes SublimeText Plugin.
github.com/tylerl/FilterPipes

"""

__author__ = 'Tyler Larson [github.com/tylerl/]'
__version__ = '1.1.0'
__license__ = 'Apache 2'
__copyright__ = 'Copyright 2015, Google Inc.'

import subprocess
import sublime
import sublime_plugin
import sys
import re

###############################################################
# Python/Sublime version compatibility
if sys.version_info[0] == 2:   # Python 2.x specific (ST2)
    PYTHON2=True
    def is_str(obj):
        return isinstance(obj, basestring)
else:  # Python 3.x
    PYTHON2=False
    def is_str(obj):  # Python 3.x specific (ST3)
        return isinstance(obj, str)
###############################################################


class FilterPipesCommandBase(sublime_plugin.TextCommand):
    """Generic base for function-based filter commands.

    This class is not used directly, but rather inherited to build
    a filter plugin that actually does something. Selection and
    text replacement logic are handled by this class.

    Override filter(self, data) to perform text filter operation.
    """
    use_selections = True
    errors_on_statusbar = True
    report_success = True
    report_failure = True
    report_nochange = True

    def filter(self, data):
        """Perform transformation on document text.

        Args:
          data: string containing selected text.

        Returns:
          string containing the desired replacement, or None to
          indicate no operation.

        """
        return None

    def success_message(self):
        """Message to display on status bar if success."""
        return 'FilterPipes: success'

    def failure_message(self):
        """Message to display on status bar if unsuccessful."""
        return 'FilterPipes: command failed'

    def nochange_message(self):
        """Message to display on status bar if replacement matches original."""
        return 'FilterPipes: No change'

    def do_replacements(self, edit):
        self.success = False
        self.replaced = False
        replacements = []
        for r in self._regions():
            replacement = self._get_replacement(r)
            if replacement is None:
                continue
            if replacement:
                replacements.append(replacement)
        # replace in reverse order to avoid overlap complications
        for replacement in reversed(replacements):
            self._commit_replacement(edit, replacement)
        msg = None
        if not self.success:
            if self.report_failure:
                msg = self.failure_message()
        elif not self.replaced:
            if self.report_nochange:
                msg = self.nochange_message()
        else:
            if self.report_success:
                msg = self.success_message()
        if msg:
            sublime.status_message(msg)

    def post_init(self):
        """Hook for doing some post-init reconfiguration.

        See the IntToInt filter for an example of how this
        can be useful.
        """
        pass

    def apply_settings(self, settings):
        for k, v in settings.items():
            setattr(self, k, v)

    def run(self, edit, **settings):
        try:
            self.apply_settings(settings)
            self.post_init()
            self.do_replacements(edit)
        except Exception as ex:
            if self.errors_on_statusbar:
                sublime.status_message(str(ex))
            raise

    def _get_replacement(self, region):
        existing = self.view.substr(region)
        filtered = self.filter(existing)
        if filtered is None:
            return None
        self.success = True
        if filtered == existing:
            return None
        self.replaced = True
        return (region, filtered)

    def _commit_replacement(self, edit, replacement):
        region, text = replacement
        self.view.replace(edit, region, text)

    def _regions(self):
        regions = None
        if self.use_selections:
            regions = [r for r in self.view.sel() if not r.empty()]
        if not regions:
            regions = [sublime.Region(0, self.view.size())]
        return regions


class FilterPipesProcessCommand(FilterPipesCommandBase):
    """Generic base for Process-based filter commands.

    Override self.command or self.getcommand() to specify which command to run,
    or pass in at run time as a configuration parameter. Set "shell" to true to
    execute as a shell command instead of direct process invocation.
    """
    command = []
    use_selections = True
    shell = False
    report_failure = False  # we do our own failure reporting
    expected_returns = [0]
    subprocess_args = {}

    def _execute_raw(self, command, text):
        """Executes a command and returns stdout, stderr, and return code."""
        args = self.subprocess_args or {}
        args['shell'] = self.shell
        cmd = subprocess.Popen(command,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, **args)
        (stdout, stderr) = cmd.communicate(text.encode('UTF-8'))
        return (stdout, stderr, cmd.returncode)

    def _expect_success(self, command, text):
        try:
            stdout, stderr, status = self._execute_raw(command, text)
            if not self.expected_returns or status in self.expected_returns:
                return stdout.decode('UTF-8')
        except OSError as e:
            stdout, stderr, status = (None, str(e), e.errno)

        if self.errors_on_statusbar:
            sublime.status_message(
                'Error %i executing command [%s]: %s' %
                (status, self.get_command_as_str(), stderr))
        print(
            'Error %i executing command [%s]:\n%s\n' %
            (status, self.get_command_as_str(False), stderr))
        return None

    def filter(self, existing):
        return self._expect_success(self.get_command(), existing)

    def get_command(self):
        return self.command

    def get_command_as_str(self, short=True):
        c = self.get_command()
        if is_str(c):
            return c
        if short:
            return c[0]
        return ' '.join(c)

    def success_message(self):
        return 'Filtered through: %s' % (self.get_command_as_str())


class FilterPipesTranslateCommand(FilterPipesCommandBase):
    """Translates characters from one set to another.

    Like the tr shell command.

    """
    before = None
    after = None

    def filter(self, data):
        if not self.before or not self.after:
            return None
        if PYTHON2:
            trans = dict(zip([ord(c) for c in self.before], self.after))
        else:
            trans = str.maketrans(self.before,self.after)
        return data.translate(trans)


class FilterPipesRegexCommand(FilterPipesCommandBase):
    """Performs a regular expression replacement.

    Because re.sub is magic, replacement can be either a string or a
    function that takes a match object.

    """
    regex = None
    replacement = None
    flags = 0
    count = 0
    lines = False

    def filter(self, data):
        if self.regex is None or self.replacement is None:
            return None
        if self.lines:
            self.flags |= re.MULTILINE
        return re.sub(self.regex, self.replacement, data,
                      count=self.count, flags=self.flags)


class FilterPipesExecPromptCommand(sublime_plugin.TextCommand):
    """Prompt for a command to filter text through."""

    def run(self, edit):
        self.view.window().show_input_panel(
            'Filter Command:', '', self.on_done, None, None)

    def on_done(self, text):
        self.view.run_command(
            'filter_pipes_process', {'command': text, 'shell': True})
