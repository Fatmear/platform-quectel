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

def generate_c_cpp_properties():
    import json
    import shutil

    head = """//
// !!! WARNING !!! AUTO-GENERATED FILE!
// PLEASE DO NOT MODIFY IT AND USE "platformio.ini":
// https://docs.platformio.org/page/projectconf/section_env_build.html#build-flags
//
"""

    data = {
        "configurations": [
            {
                "name": "PlatformIO",
                "includePath": [
                    join(env['PROJECT_DIR'], "include"),
                    join(env['PROJECT_DIR'], "src")
                ],
                "browse": {
                    "limitSymbolsToIncludedHeaders": True, 
                    "path": [
                        join(env['PROJECT_DIR'], "include"),
                        join(env['PROJECT_DIR'], "src")
                    ]
                },
                "defines": [""],
                "cStandard": "c99",
                "cppStandard": "c99",
                "compilerPath": "cc",
                "compilerArgs": [""],
            }
        ],
        "version": 4,
    }

    if 'CPPPATH' in env:
        data['configurations'][0]['includePath'] += env['CPPPATH']
        data['configurations'][0]['browse']['path'] += env['CPPPATH']
    
    if os.path.exists(join(env['PROJECT_DIR'], ".vscode")) == False:
        os.mkdir(join(env['PROJECT_DIR'], ".vscode"))

    with open(join(env['PROJECT_DIR'], ".vscode", "c_cpp_properties.json"), "w") as f:
        f.write(head)
        json.dump(data, f, ensure_ascii=False, indent=4)

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
    CPPPATH=[
        join(FRAMEWORK_DIR, "ql_tools", "nds32le-elf-mculib-v3s", "nds32le-elf", "sys-include"),
        join(FRAMEWORK_DIR, "ql_kernel", "arch"),
        join(FRAMEWORK_DIR, "ql_kernel", "Boards", "ecr6600", "common", "include"),
        join(FRAMEWORK_DIR, "ql_kernel", "Boards", "ecr6600", "standalone", "generated"),
        join(FRAMEWORK_DIR, "ql_application", "uart_demo"),
        join(FRAMEWORK_DIR, "ql_application", "https_demo"),
        join(FRAMEWORK_DIR, "ql_application", "wlan_demo"),
        join(FRAMEWORK_DIR, "ql_application", "adc_demo"),
        join(FRAMEWORK_DIR, "ql_application", "lowpower_demo"),
        join(FRAMEWORK_DIR, "ql_application", "wdt_demo"),
        join(FRAMEWORK_DIR, "ql_application", "ble_demo"),
        join(FRAMEWORK_DIR, "ql_application", "spi_flash_demo"),
        join(FRAMEWORK_DIR, "ql_application", "i2s_demo"),
        join(FRAMEWORK_DIR, "ql_application", "ch392_demo"),
        join(FRAMEWORK_DIR, "ql_application", "rtc_demo"),
        join(FRAMEWORK_DIR, "ql_application", "timer_demo"),
        join(FRAMEWORK_DIR, "ql_application", "config_network_demo"),
        join(FRAMEWORK_DIR, "ql_application", "ftp_demo"),
        join(FRAMEWORK_DIR, "ql_application", "st_demo"),
        join(FRAMEWORK_DIR, "ql_application", "w5500_demo"),
        join(FRAMEWORK_DIR, "ql_application", "fs_demo"),
        join(FRAMEWORK_DIR, "ql_application", "spi_demo"),
        join(FRAMEWORK_DIR, "ql_application", "gpio_demo"),
        join(FRAMEWORK_DIR, "ql_application", "osi_api_demo"),
        join(FRAMEWORK_DIR, "ql_application", "i2c_demo"),
        join(FRAMEWORK_DIR, "ql_application", "aliyun_demo"),
        join(FRAMEWORK_DIR, "ql_application", "mqtt_demo"),
        join(FRAMEWORK_DIR, "ql_application", "pwm_demo"),
        join(FRAMEWORK_DIR, "ql_application", "sockets_demo"),
        join(FRAMEWORK_DIR, "ql_application", "ota_demo"),
        join(FRAMEWORK_DIR, "ql_application", "flash_demo"),
        join(FRAMEWORK_DIR, "ql_application", "sl_tls_demo"),
        join(FRAMEWORK_DIR, "ql_components", "platform_api"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_common"), 
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_adc"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_gpio"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_os_api"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_timer"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_uart"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_wlan"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_spi"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_pwm"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_ble"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_flash"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_spi_flash"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_ch392_lwip"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_w5500_lwip"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_lowpower"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_ota"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_https"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_wdt"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_rtc"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_sys"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_mem"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_i2c"),
        join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_i2s"),
        # join(FRAMEWORK_DIR, "ql_components", "quectel", "quec_open", "quec_fs"),
        join(FRAMEWORK_DIR, "ql_components", "wifi_crtl"),
        join(FRAMEWORK_DIR, "ql_components", "cli"),
        join(FRAMEWORK_DIR, "ql_components", "nv"),
        join(FRAMEWORK_DIR, "ql_components", "cjson"),
        join(FRAMEWORK_DIR, "ql_components", "http_server"),
        join(FRAMEWORK_DIR, "ql_components", "sntp"),
        #join(FRAMEWORK_DIR, "ql_components", "fs", "fatfs"),
        join(FRAMEWORK_DIR, "ql_components", "drivers", "trng"),
        join(FRAMEWORK_DIR, "ql_components", "drivers", "uart"),
        join(FRAMEWORK_DIR, "ql_components", "drivers", "rtc"),
        join(FRAMEWORK_DIR, "ql_components", "drivers", "sdcard"),
        join(FRAMEWORK_DIR, "ql_components", "drivers", "flash"),
        join(FRAMEWORK_DIR, "ql_components", "drivers", "hal"),
        join(FRAMEWORK_DIR, "ql_components", "ota"),
        join(FRAMEWORK_DIR, "ql_components", "ota", "include"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "mqtt"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "mqtt", "include"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "fatfs"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "fatfs", "include"),
        join(FRAMEWORK_DIR, "ql_components", "wpa", "src", "utils"),
        join(FRAMEWORK_DIR, "ql_components", "pthread"),
        join(FRAMEWORK_DIR, "ql_components", "os"),
        join(FRAMEWORK_DIR, "ql_components", "os", "freertos"),

        # LWIP
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "contrib"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "contrib", "port"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "contrib", "port", "arch"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "contrib", "port", "netif"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "api"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "include"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "include", "lwip"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "include", "lwip", "prot"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "include", "lwip", "priv"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "include", "lwip", "apps"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "include", "netif"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "include", "netif", "ppp"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "include", "netif", "ppp", "polarssl"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "include", "compat"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "include", "compat", "stdc"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "include", "compat", "posix"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "include", "compat", "posix", "arpa"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "include", "compat", "posix", "net"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "include", "compat", "posix", "sys"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "core"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "core", "ipv4"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "core", "ipv6"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "apps"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "apps", "snmp"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "apps", "mqtt"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "apps", "mdns"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "apps", "altcp_tls"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "apps", "lwiperf"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "apps", "netbiosns"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "apps", "dhcpserver"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "apps", "smtp"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "apps", "ping"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "apps", "http"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "apps", "http", "makefsdata"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "apps", "tftp"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "apps", "sntp"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "netif"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "netif", "ppp"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "src", "netif", "ppp", "polarssl"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "doc"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "lwip", "lwip-2.1.0", "doc", "doxygen"),

        # MBEDTLS
        join(FRAMEWORK_DIR, "ql_components", "third_party", "mbedtls"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "mbedtls", "mbedtls", "library"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "mbedtls", "mbedtls", "include"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "mbedtls", "mbedtls", "include", "mbedtls"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "mbedtls", "port"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "mbedtls", "port", "include"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "mbedtls", "port", "include", "mbedtls"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "mbedtls", "ui"),

        # CURL
        join(FRAMEWORK_DIR, "ql_components", "third_party", "curl"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "curl", "curl-8.1.2"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "curl", "curl-8.1.2", "lib"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "curl", "curl-8.1.2", "lib", "vtls"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "curl", "curl-8.1.2", "lib", "vauth"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "curl", "curl-8.1.2", "lib", "vssh"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "curl", "curl-8.1.2", "lib", "vquic"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "curl", "curl-8.1.2", "include"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "curl", "curl-8.1.2", "include", "curl"),

        # MQTT
        join(FRAMEWORK_DIR, "ql_components", "third_party", "mqtt"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "mqtt", "include"),

        # FATFS
        join(FRAMEWORK_DIR, "ql_components", "third_party", "fatfs"),
        join(FRAMEWORK_DIR, "ql_components", "third_party", "fatfs", "include"),
    ],
    upload_source = join(env["PROJECT_BUILD_DIR"], board.get('name'), "${PROGNAME}.bin"),
)

generate_c_cpp_properties()
