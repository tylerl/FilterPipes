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

"""Custom FilterPipes plugin creation.

The components in this file handle the creation and access
of your custom FilterPipes plugin project. The full content
of the custom plugin is contained here.

Part of the FilterPipes SublimeText Plugin.
github.com/tylerl/FilterPipes

"""


import os
import sublime
import sublime_plugin
CUSTOM_PLUGIN_NAME = 'MyCustomFilterPipes'
CUSTOM_PLUGIN_PROJECT = 'plugin.sublime-project'
README_FILENAME = 'README.txt'


class FilterPipesMyPluginCommand(sublime_plugin.WindowCommand):
    def _create_plugin_impl(self, plugin_dir):
        os.mkdir(plugin_dir, 493)  # 0755 (python 2/3 safe)
        for name, content in CONTENT_TEMPLATE.items():
            filepath = os.path.join(plugin_dir, name)
            with os.fdopen(
                os.open(filepath, os.O_WRONLY | os.O_CREAT, 420),
                    'w') as f:   # 420 = 0644
                if name == README_FILENAME:
                    content = content.format(directory=plugin_dir)
                f.write(content)

    def _maybe_create_plugin(self, plugin_dir):
        if not sublime.ok_cancel_dialog(
                'Your custom filter plugin does not exist yet. '
                'Would you like to create it now?',
                'Create it'
        ):
            return False
        self._create_plugin_impl(plugin_dir)
        return True

    def run(self):
        plugin_dir = os.path.join(sublime.packages_path(), CUSTOM_PLUGIN_NAME)
        if not os.path.exists(plugin_dir):
            try:
                if not self._maybe_create_plugin(plugin_dir):
                    return
            except Exception as ex:
                sublime.message_dialog('Failed to create plugin:\n%s' % (ex))
                raise ex
            readme_path = os.path.join(plugin_dir, README_FILENAME)
            self.window.run_command('open_file', {'file': readme_path})
        self.window.run_command('open_dir', {'dir': plugin_dir})


CONTENT_TEMPLATE = {
    'Default.sublime-commands':
    r"""[
    /*********************************************************
    * The following example commands show you the basics of  *
    * working with filter pipes. Delete, modify, rename, and *
    * use as you see fit.                                    *
    **********************************************************/

    // ###########################################################
    // Translate filters. Translates characters in the "before"
    // string to the corresponding (by position) character in
    // the "after" string.
    {
        "caption": "FilterPipes Example: Swap Quotes",
        "command": "filter_pipes_translate",
        "args": {
            "before": "'\"",
            "after": "\"'"
        }
    },

    {
        "caption": "FilterPipes Example: Convert to Straight Quotes",
        "command": "filter_pipes_translate",
        "args": {
            "before": "\u201c\u201d\u201f\u301d\u301e\uff02\u201e\u301f\u2018\u2019\u201b\uff07\u201a",
            "after": "\"\"\"\"\"\"\"\"'''''"
        }
    },
    // ###########################################################
    // Regex filters. Runs the selection through a regular
    // expression replacement.
    //
    // You can specify
    //      "lines": true
    // to add the MULTILINE flag to replacement function --
    // this makes ^ and $ match the beginning and end of each
    // individual line instead of the whole string.

    {
        "caption": "FilterPipes Example: collapse spaces",
        "command": "filter_pipes_regex",
        "args": {
            "regex": "\\s+",
            "replacement": " "
        }
    },
    // ###########################################################
    // Process filters. Runs the selection through an external
    // program as a filter instead. Remember you can specify
    //      "use_selections": false
    // if you want to always process the whole file, regardless of
    // selections.
    //
    // Also note that if command is a list, then the first element
    // is the executable, and the other elements are parameters.
    // If it's instead simply a string, then, then that string is
    // interpreted as a shell command.

    // "pip install jsbeautifier" to make this one work
    {
        "caption": "FilterPipes Example: Beautify JS (js-beautify)",
        "command": "filter_pipes_process",
        "args": {
            "command": ["js-beautify", "-i"]
        }
    },
    {
        "caption": "FilterPipes Example: Minify JS (uglifyjs)",
        "command": "filter_pipes_process",
        "args": {
            "command": ["uglifyjs"]
        }
    },

    // ###########################################################
    // Python Filters. These have corresponding entries in the
    // myfilters.py file, where the command name is translated to
    // camelcase with the word "Command" appended. So for example
    // "camel_case_filter" is the class "CamelCaseFilterCommand"
    // in myfilters.py. The filter() function determines what the
    // filter does. Finally, any args provided here get automatically
    // set as class object instance variables; usually overriding
    // a Default setting.

    {   /* See ReverseWordsCommand */
        "caption": "FilterPipes Example: Reverse Words",
        "command": "reverse_words"
    },

    {   /* See CamelCaseFilterCommand */
        "caption": "FilterPipes Example: to CamelCase",
        "command": "camel_case_filter",
        "args": {
            "initial_caps": true
        }
    },

    {   /* See CamelCaseFilterCommand */
        "caption": "FilterPipes Example: to mixedCase",
        "command": "camel_case_filter",
        "args": {
            "initial_caps": false
        }
    },

    {   /* See UnderscoreCaseFilterCommand */
        "caption": "FilterPipes Example: to underscore_case",
        "command": "underscore_case_filter"
    }
]
""",
    'myfilters.py':
    """"\""Sample filters for doing mildly useful things using FilterPipes."\""

try:
    from FilterPipes import filterpipes  # ST3-style import
except ImportError:
    import filterpipes  # ST2-style import


class ReverseWordsCommand(filterpipes.FilterPipesCommandBase):
    "\""Reverse the order of selected words. Extremely simple example."\""
    def filter(self, data):
        return " ".join(reversed(data.split(" ")))


class CamelCaseFilterCommand(filterpipes.FilterPipesCommandBase):
    "\""Converts words_with_underlines to CamelCase."\""
    initial_caps = True

    def filter(self, data):
        next_upper = self.initial_caps
        out = []
        for c in data:
            if c == '_':
                next_upper = True
            elif c.islower():
                if next_upper:
                    out.append(c.upper())
                else:
                    out.append(c)
                next_upper = False
            else:
                next_upper = self.initial_caps and not c.isalnum()
                out.append(c)
        return ''.join(out)


class UnderscoreCaseFilterCommand(filterpipes.FilterPipesCommandBase):
    "\""Converts CamelCase to words_with_underlines."\""

    def filter(self, data):
        prev_lower = False
        out = []
        for c in data:
            if c.isupper():
                if prev_lower:
                    out.append('_')
                out.append(c.lower())
                prev_lower = False
            elif c.islower():
                prev_lower = True
                out.append(c)
            else:
                prev_lower = False
                out.append(c)
        return ''.join(out)
""",
    README_FILENAME:
    """CUSTOM PLUGIN FILTERS
=====================

This directory contains the a set of filters to be customized
by you, the user. It's pre-populated with a few that show you
the basics of how to create your own. These examples are
designed to be useful in their own right. But feel free to
modify, rename, or remove them as you see fit.

To restore it to this initial state, just remove or
rename this directory and re-create it using the
"My Custom Filters" command.

This plugin was created at:
{directory}

FILES
=====

You should pay attention to the following files. The others... meh.

Default.sublime-commands
------------------------

A good first place to start. This is where you define what commands
will appear in your command palette. You can use the same Python
class to create multiple commands using different arguments. You'll
see several examples of that in example content provided.

You can create a Default.sublime-keymap file to do the same thing
but for keyboard shortcuts instead of command palette entries.

myfilters.py
------------

This contains examples of custom Python filters. Each filter command
is its own classes with a filter() function. The naming convention
on the class is enforced by Sublime, so follow the pattern you see
in the file; namely: camelcase words ending in "Command". For example,
to create a command named "convert_to_lowercase" your class will be
named ConvertToLowercaseCommand.
"""
}
