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

import sys
import os
from os.path import join, isdir

import utils.trans_cmakelists as trans_cmakelists
from platformio.platform.base import PlatformBase
from platformio.platform.board import PlatformBoardConfig
from SCons.Script import (
    COMMAND_LINE_TARGETS,
    AlwaysBuild,
    Default,
    DefaultEnvironment,
    Environment
)

env: Environment = DefaultEnvironment()
platform: PlatformBase = env.PioPlatform()
board: PlatformBoardConfig = env.BoardConfig()

# Firmware name
if env.get("PROGNAME", "program") == "program":
    env.Replace(PROGNAME="firmware")
env.Replace(PROGSUFFIX=".elf")

if "nobuild" in COMMAND_LINE_TARGETS:
    bsp_app_elf = join("${BUILD_DIR}", "${PROGNAME}.elf")
    bsp_app_bin = join("${BUILD_DIR}", "bsp_app.bin")
    firmware_bin = join("${BUILD_DIR}", "${PROGNAME}.bin")
else:
    env.SConscript("frameworks/csdk/csdk.py")
    if hasattr(env, 'RunBuildSH'):
        env.RunBuildSH(None, env["PROGNAME"])
        bsp_app_elf = join("${BUILD_DIR}", "${PROGNAME}.elf")
        bsp_app_bin = join("${BUILD_DIR}", "${PROGNAME}.bin")
        firmware_bin = join("${BUILD_DIR}", "${PROGNAME}.bin")
    else:
        bsp_app_elf = env.BuildProgram()
        bsp_app_bin = env.ElfToBin(join("${BUILD_DIR}", "bsp_app"), bsp_app_elf)
        firmware_bin = env.GenFirmBin(join("${BUILD_DIR}", "${PROGNAME}.bin"), bsp_app_bin)
    
AlwaysBuild(env.Alias("nobuild", bsp_app_bin))
AlwaysBuild(env.Alias("nobuild", firmware_bin))
target_buildprog = env.Alias("buildprog", firmware_bin, firmware_bin)

target_size = env.Alias(
    "size",
    bsp_app_elf,
    env.VerboseAction("${SIZEPRINTCMD}", "Calculating size ${SOURCE}"),
)
AlwaysBuild(target_size)

upload_actions = [
    env.VerboseAction(env.AutodetectUploadPort, "Looking for upload port..."),
    env.VerboseAction("${UPLOADCMD}", "Uploading ${SOURCE}"),
]

AlwaysBuild(env.Alias("upload", "${upload_source}", upload_actions))

Default([target_buildprog, target_size])
