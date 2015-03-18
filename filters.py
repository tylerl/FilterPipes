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

"""
Included filters for FilterPipes.

These filters use the base classes from the filterpipes library
to

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

    def filter(self, text):
        if self.decode:
            return base64.b64decode(text.encode('UTF-8')).decode('UTF-8')
        encoded = base64.b64encode(text.encode('UTF-8')).decode('UTF-8')
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
