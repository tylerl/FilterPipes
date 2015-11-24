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

"""Included filters for FilterPipes.

These filters build upon the classes from the filterpipes base
library to provide a useful set of features for everyday use.

Part of the FilterPipes SublimeText Plugin.
github.com/tylerl/FilterPipes

"""

import sys
if sys.version_info[0] == 3:  # Python 3; ST 3
    from FilterPipes import filterpipes  # ST3-style import
    from urllib.parse import quote, unquote
else:
    import filterpipes  # ST2-style import
    from urllib import quote, unquote

import base64


class FilterPipesBase64Command(filterpipes.FilterPipesCommandBase):
    decode = False
    wrap = 64
    urlsafe = False

    def filter(self, text):
        b64e = base64.base64encode
        b64d = base64.base64decode
        if self.urlsafe:
            b64e = base64.urlsafe_base64encode
            b64d = base64.urlsafe_base64decode
        if self.decode:
            return b64d(text.encode('UTF-8')).decode('UTF-8')
        encoded = b64e(text.encode('UTF-8')).decode('UTF-8')
        if self.wrap:
            return '\n'.join(
                (encoded[i:i + self.wrap] for i in
                    range(0, len(encoded), self.wrap)))
        return encoded


class FilterPipesUrlencodeCommand(filterpipes.FilterPipesCommandBase):
    decode = False

    def filter(self, text):
        if self.decode:
            return unquote(text)
        else:
            return quote(text)


class FilterPipesEscapeCommand(filterpipes.FilterPipesCommandBase):
    decode = False

    def filter(self, data):
        if self.decode:
            return data.encode("UTF-8").decode('unicode-escape')
        else:
            return data.encode('unicode-escape').decode("UTF-8")


class FilterPipesIntToIntCommand(filterpipes.FilterPipesRegexCommand):
    """Converts integer strings between common bases.

    Included as a demonstration of more complex uses of regex matching,
    including configuration using the post_init callback as well as
    replacement using a function instead of static text.
    """
    BASE_REGEX = {
        10: r"\b([0-9]+)\b",
        16: r"\b((?:0[Xx])?[0-9a-fA-F]+)\b",
        8: r"\b([0-7]+)\b"
    }
    BASE_FMT = {8: "%o", 10: "%i", 16: "%x"}
    PREFIX = {8: "0", 10: "", 16: "0x"}
    regex = None  # set by post_init
    from_base = 10
    to_base = 16
    case = "lower"
    output_prefix = True

    def post_init(self):
        self.from_base = int(self.from_base)
        self.to_base = int(self.to_base)
        self.regex = self.BASE_REGEX[self.from_base]
        self.output_fmt = self.BASE_FMT[self.to_base]
        if self.output_prefix:
            self.output_fmt = self.PREFIX[self.to_base] + self.output_fmt
        if self.case == "upper":
            self.output_fmt = self.output_fmt.upper()

    def replacement(self, match):
        txt = match.group(1)
        try:
          val = int(txt, self.from_base)
          return self.output_fmt % (val)
        except ValueError:
            pass
        return match.group(0)
