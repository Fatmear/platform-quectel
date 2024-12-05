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

import platform as plat
import os
from os.path import join, isdir
import configparser

from platformio.platform.base import PlatformBase
from platformio.platform.board import PlatformBoardConfig
from SCons.Script import (
    DefaultEnvironment,
    Environment
)

env: Environment = DefaultEnvironment()
platform: PlatformBase = env.PioPlatform()
board: PlatformBoardConfig = env.BoardConfig()
FRAMEWORK_DIR = platform.get_package_dir("framework-" + board.get('name').lower() +"-csdk")
assert isdir(FRAMEWORK_DIR)

system = plat.system()

def run_build_sh(self, source, target):
    import os
    import shutil
    last_dir = os.getcwd()
    ql_out_dir = join(FRAMEWORK_DIR, "ql_out")
    if os.path.exists(ql_out_dir):
        shutil.rmtree(ql_out_dir)
    os.chdir(FRAMEWORK_DIR)
    if system == "Windows":
        os.environ['PIO_PROJECT_DIR'] = env['PROJECT_DIR'].replace('\\', '/')
        if os.system("build.bat new FCM360W V01"):
            exit(1)
    elif system == "Linux":
        os.environ['PIO_PROJECT_DIR'] = env['PROJECT_DIR']
        if os.system("./build.sh new FCM360W V01"):
            exit(1)
    if os.path.exists(join(env['PROJECT_BUILD_DIR'], board.get('name'))):
        shutil.rmtree(join(env['PROJECT_BUILD_DIR'], board.get('name')))
    shutil.move(join(ql_out_dir, "debug"), join(env['PROJECT_BUILD_DIR'], board.get('name'), "debug"))
    shutil.move(join(ql_out_dir, "ECR6600F_standalone_allinone.bin"), join(env['PROJECT_BUILD_DIR'], board.get('name'), target + ".bin"))
    shutil.move(join(ql_out_dir, "ECR6600F_standalone_cpu_0x7000.bin"), join(env['PROJECT_BUILD_DIR'], board.get('name')))
    shutil.copy(join(env['PROJECT_BUILD_DIR'], board.get('name'), "debug", "standalone.elf"), join(env['PROJECT_BUILD_DIR'], board.get('name'), target + ".elf"))
    os.chdir(last_dir)

env.AddMethod(run_build_sh, "RunBuildSH")

project_config = configparser.ConfigParser()
project_config.read(env['PROJECT_CONFIG'])
if project_config.has_option(project_config.sections()[0], "FIRMWARE_NAME"):
    env.Replace(
        PROGNAME = project_config.get(project_config.sections()[0], "FIRMWARE_NAME")
    )
else:
    env.Replace(
        PROGNAME = "FCM360WAAR01A01_V01"
    )

if system == "Windows":
    gcc_path = join(FRAMEWORK_DIR, "ql_tools", "nds32le-elf-mculib-v3s-win")
    if not os.path.exists(gcc_path):
        os.system(join(FRAMEWORK_DIR, "ql_tools", "7z", "7z.exe") + " x " + join(FRAMEWORK_DIR, "ql_tools", "nds32le-elf-mculib-v3s-win.7z") + " -o" + gcc_path)

    upload_port = 0
    try:
        if "COM" in env["UPLOAD_PORT"]:
            upload_port = int(env["UPLOAD_PORT"][3:])
    except Exception as e:
        pass

    env.Replace(
        UPLOADER=FRAMEWORK_DIR + "/ql_tools/flashtool/EswinFlashTool.exe",
        UPLOADERFLAGS=[
            "-p", upload_port,
            "-b", "921600",
            "-f",
        ],
        UPLOADCMD='$UPLOADER $UPLOADERFLAGS $SOURCE',
    )
elif system == "Linux":
    gcc_path = join(FRAMEWORK_DIR, "ql_tools", "nds32le-elf-mculib-v3s")
    if not os.path.exists(gcc_path):
        os.system("tar -xvf " + join(FRAMEWORK_DIR, "ql_tools", "nds32le-elf-mculib-v3s.txz") + " -C " + join(FRAMEWORK_DIR, "ql_tools"))

    env.Replace(
        UPLOADER=FRAMEWORK_DIR + "/ql_tools/flashtool/trstool",
        UPLOADERFLAGS=[
            "-d", "$UPLOAD_PORT",
            "--download_baudrate", "921600",
            "-f",
        ],
        UPLOADCMD='$UPLOADER flash $UPLOADERFLAGS $SOURCE',
    )
else:
    print("Unsupported operating system")
    exit(1)

env.Append(
    upload_source = join(env["PROJECT_BUILD_DIR"], board.get('name'), "${PROGNAME}.bin"),
)
