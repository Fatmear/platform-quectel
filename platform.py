# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from platformio.managers.platform import PlatformBase

class QuectelPlatform(PlatformBase):
    def __init__(self, manifest_path):
        super().__init__(manifest_path)
        if "csdk" in self.frameworks.keys():
            if 'package' not in self.frameworks['csdk']:
                sections = self.config._parser.sections()
                if len(sections) > 0:
                    self.frameworks['csdk']['package'] = "framework-" + self.config._parser.get(sections[0],'board').lower() + "-csdk"
        else:
            print('Unkonwn framework!')
            