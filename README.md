# FilterPipes

FilterPipes is a SublimeText (v2 and v3) plugin for filtering selected text
through pipes or filters, either written as Python functions or as external
processes.

This project lives at [github.com/tylerl/FilterPipes](https://github.com/tylerl/FilterPipes).

### Filter Through Process
This plugin provides a prompt for you to supply the shell command to execute.

![Shell execute animation](https://raw.githubusercontent.com/tylerl/FilterPipes/media/fp_sort.gif)

### Filter Through Python
Python code can also be used as the filter function. Several useful examples
are provided as listed below, but the real power comes in when you create your
own functions.

### Creating Custom Filters
FilterPipes makes it crazy-simple for you to create your own custom filter
plugins. There are some pre-defined classes for simple text replacement,
regular expressions, character-for-character translations, and external
processes. Creating your own custom filter is as simple as creating a
Python class with a single method called `filter` as demonstrated below:

![Plugin creation animation](https://raw.githubusercontent.com/tylerl/FilterPipes/media/fp_reverse.gif)

# Provided Commands

The following commands are included. All commands are accessible from
the command palette. No shortcut keys are assigned by default,
though you are free to add your own if you like.

* **My Custom Filters Plugin**: Create and access your own FilterPipes-derived
custom plugin. The first time you run this command it will create the plugin
for you and add some sample content. Every subsequent run will simply open
your existing plugin directory.
* **Send Text to Command**: Prompts you for a shell command to run, and
then executes that command using your selection(s) as `stdin`, and replacing
them with `stdout` if the program ends successfully.
* **Base64 Encode** and **Base64 Decode**: Encodes and decodes text using
[Base64](Base64 Decode) encoding rules.
* **URL Encode** and **URL Decode**: Similarly, encodes and decodes text
using [URL ("percent") encoding](http://en.wikipedia.org/wiki/Percent-encoding).
* **String Escape** and **String Unescape**: Encodes and decodes strings using
simple string-escaping rules (e.g. TAB character becomes `\t`, newline becomes
`\n`, and so forth.
* **Strip Trailing Space**: Does what it says on the tin: it strips any spaces
at the end of lines. While mildly useful, this is here primarily because I
wanted to include an example of a Regex-based filter.

### Example Filters

These filters are included in the "My Custom Filters Plugin" example. Run the
"My Custom Filters Plugin" command to install them.

Most of these filters don't use any custom Python class, but instead use the
customization options of the provided generic filters to do something more
interesting. The only code will be the entry in `Default.sublime-commands` file
for your created plugin.

#### Translation Commands
These provide simple character-for-character translations to apply. Think of
them like the unix `tr` command, if you're nerdy enough to ever have used it.

* **Swap Quotes**: Swaps single quotes for double quotes (and vice-versa).
(surprisingly useful, but not context-aware).
* **Convert to Straight Quotes**: Turns all the varieties of "smart quotes" into
normal "straight" quotes, like any good programmer would prefer.

#### Regex Filter
Your regex filter configuration provides a simple search regex and replacement
string. It's not unlike regex-based search-and-replace, except your setup gets
baked into a single simple command.

* **Collapse Spaces**: Turns runs of any sort of whitespace into a single
space character. 

* **Hex to Decimal, Decimal to Hex, Octal to Decimal, Decimal to Octal**:
Convert integers between popular numeric bases. This is provided as an
example of a regex filter that uses a callback function for replacements
instead of a simple string constant. It's also an example of the use of
using the `post_init` callback to rewrite the runtime configuration
(in this case the search regex) programatically. 

#### Process Filters
Entire plugins have been written for performing this one simple action. Actually,
this plugin started out as one of them. It's gotten much more useful since then,
though. This filter type lets you specify a command to run. Kind of like the
"Send Text to Command" filter, but without the input prompt, and (by default)
without the shell interpretation (you can optionally turn that on, though).

Note that the included examples require you to install the associated program.
You may have to fiddle with the path (and perhaps command-line options) as well,
depending on your local installation.

* **Beautify JS (js-beautify)**: Many javascript developers use a command called
"js-beautify" to clean up their code. This filter calls that command... assuming
it's installed in the PATH. Otherwise, it does nothing but serve as an example
of how to write this kind of filter.
* **Minify JS (uglifyjs)**: Just like the above, but exactly the opposite. This
command makes your javascript compact and illegible... assuming you have it
installed -- the same caveat applies as above.

#### Python Filters
These are the *really* cool ones. You write your own python code to transform
the selected text. Note that the naming of the command follows the same pattern
as per normal for SublimeText. You convert the Python class name from CamelCase
to underscore_case and remove `_command` from the end to ge the name that goes into
your `.sublime-commands` file. This is done internally by SublimeText, so don't get
mad at me about it.

* **Reverse Words**: This is the example coded in the animation above. It reverses
the order of words delimited by spaces. I have no idea why anyone would ever
want to do that, but the code is tiny and the effect is obvious, so it makes a
pretty compelling piece of example code.
* **to CamelCase**: Converts words from `underscore_case` to `CamelCase`.
* **to mixedCase**: Converts words from `underscore_case` to `mixedCase`, which is
exactly the same as CamelCase, but without the first letter capitalized. In fact,
both these filters use the same Python class. This filter demonstrates how to add
your own custom command options.
* **to underscore_case**: Converts from `CamelCase` back to `underscore_case`, included
mostly out of an obsessive-compulsive need for parity.

# Creating Your Own

To write your own plugin, start out by bringing up the command pallete (typically
<kbd>ctrl</kbd>+<kbd>shift</kbd>+<kbd>P</kbd> or
<kbd>cmd</kbd>+<kbd>shift</kbd>+<kbd>P</kbd>) and running "My Custom Filters Plugin".
Even if you don't end up using the plugin it creates, this will at least give
you a working scaffold with all the right configuration and examples such to get started.

All commands take the optional parameter `use_selections`, which when set to false, tells
the system to ignore your text selections and pass the whole file in. Typically this is
useful for tools that use the entire file for context, such as source code formatters.

## Using the built-in filter classes

Generic filter classes are provided that allow you to do a lot of cool things without
writing any Python code. For these, you don't need a custom plugin, you can just
put the appropriate command invocation in your own `.sublime-settings` or `.sublime-keymap`
file.

#### Using `filter_pipes_process`

This sends text to an external process. The general configuration looks like
this. Note that unless you've specified `shell` as `true`, you'll want your
command to be a list of parameters rather than a single string.

```json
{
    "caption": "YOLO Text",
    "command": "filter_pipes_process",
    "args": {
        "command": ["banner", "-w", "80"],
        "shell": false
    }
}
```

#### Using `filter_pipes_translate`

Does character-for-character translations using Python's `string.translate`
function. That remark earlier about the `tr` command? Yeah, time to get your *Nerd* on.

```json
{
    "caption": "H4X0R",
    "command": "filter_pipes_translate",
    "args": {
        "before": "AaEeiIoOlsSTt",
        "after":  "4433110015577"
    }
}
```

#### Using `filter_pipes_regex`

Supply a regex and replacement. Pretty straightforward, but don't forget that
backslashes have to be escaped for JSON encoding.

```json
{
    "caption": "Format Phone Numbers",
    "command": "filter_pipes_regex",
    "args": {
        "regex": "(\\d{3})(\\d{3})(\\d{4})",
        "replacement":  "(\\1) \\2-\\3"
    }
}
```

#### Writing your own custom Python Filters

Here's where the real magic happens. You can very easily write
custom code to transform your text in any way imaginable, and
it only takes a minute or two to get going.

Once you've got your custom filter plugin created, open
up the `myfilters.py` file and at the bottom of the file
create a class like this:

```python
class SuperAwesomeFilterCommand(filterpipes.FilterPipesCommandBase):
    """Does approximately nothing, but does it with style."""
    def filter(self, data):
        return data
```

The class name determines the command name using the SublimeText rules
metioned earlier. So `SuperAwesomeFilterCommand` becomes `super_awesome_filter`.

Whatever your `filter()` function returns is what your text will
be replaced with. So go get creative.

Note that if you want your plugin to take some configurable parameter
from the `.sublime-commands` file, it's pretty easy. First you create
a class variable and assign it your desired default value:

```python
class SurroundSelectionCommand(filterpipes.FilterPipesCommandBase):
    """Prepends and appends some string to the selected text."""
    prepend = '{'
    append = '}'
    def filter(self, data):
        return self.prepend + data + self.append
```

Then in your `.sublime-keymap` or `.sublime-commands` file, specify
some alternate value for those variables in the "args" section like so:

```json
{
    "caption": "Double Power Bracket",
    "command": "surround_selection",
    "args": {
        "prepend": ".:[[",
        "append": "]]:."
    }
}
```

# Copyright and License

***This is not an official Google product.***

    Copyright 2015 Google Inc. All Rights Reserved.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

