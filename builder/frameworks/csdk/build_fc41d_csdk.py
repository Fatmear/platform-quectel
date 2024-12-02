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

from platformio.platform.base import PlatformBase
from platformio.platform.board import PlatformBoardConfig
from SCons.Script import (
    DefaultEnvironment,
    Environment,
    Builder
)

system = plat.system()

def gen_firmware_bin(source, target, env):
    import os
    import shutil
    last_dir = os.getcwd()
    ql_out_path = join(FRAMEWORK_DIR, "ql_out")
    if os.path.exists(ql_out_path) and os.path.isdir(ql_out_path): 
        shutil.rmtree(ql_out_path)
    os.mkdir(ql_out_path)
    shutil.copy(str(source[0]), join(ql_out_path, "fc41d_bsp_app.bin"))
    os.chdir(join(FRAMEWORK_DIR, "ql_tools", "beken_packager"))
    os.system("python ocpu_bk_packager.py fc41d_bsp_app")
    if os.path.exists(join(env["PROJECT_BUILD_DIR"], board.get('name'), "fc41d_bsp_app_uart_2M.1220.bin")):  
        os.remove(join(env["PROJECT_BUILD_DIR"], board.get('name'), "fc41d_bsp_app_uart_2M.1220.bin"))  
    shutil.move("./fc41d_bsp_app_uart_2M.1220.bin", join(env["PROJECT_BUILD_DIR"], board.get('name')))
    if os.path.exists(join(env["PROJECT_BUILD_DIR"], board.get('name'), os.path.basename(str(target[0])))):  
        os.remove(join(env["PROJECT_BUILD_DIR"], board.get('name'), os.path.basename(str(target[0]))))  
    shutil.move("../../ql_out/all_2M.1220.bin", join(env["PROJECT_BUILD_DIR"], board.get('name'), os.path.basename(str(target[0]))))
    os.chdir(last_dir)

env: Environment = DefaultEnvironment()
platform: PlatformBase = env.PioPlatform()
board: PlatformBoardConfig = env.BoardConfig()
FRAMEWORK_DIR = platform.get_package_dir("framework-" + board.get('name').lower() + "-csdk")
assert isdir(FRAMEWORK_DIR)

if system == "Windows":
    gcc_path = join(FRAMEWORK_DIR, "ql_tools", "gcc-arm-none-eabi-5_4-2016q3-20160926-win32")
    if not os.path.exists(gcc_path):
        os.system(join(FRAMEWORK_DIR, "ql_tools", "7z", "7z.exe") + " x " + join(FRAMEWORK_DIR, "ql_tools", "gcc-arm-none-eabi-5_4-2016q3-20160926-win32.zip") + " -o" + gcc_path)

    upload_port = 0
    try:
        if "COM" in env["UPLOAD_PORT"]:
            upload_port = int(env["UPLOAD_PORT"][3:])
    except Exception as e:
        pass

    env.Replace(
        UPLOADER=FRAMEWORK_DIR + "/ql_tools/bk_loader/bk_loader.exe",
        UPLOADERFLAGS=[
            "-p", upload_port,
            "-b", "921600",
            "-i",
        ],
        UPLOADCMD='$UPLOADER download $UPLOADERFLAGS $SOURCE',
    )

    env.Replace(
        AR = join(gcc_path, "bin", "arm-none-eabi-ar.exe"),
        AS = join(gcc_path, "bin", "arm-none-eabi-gcc.exe"),
        CC = join(gcc_path, "bin", "arm-none-eabi-gcc.exe"),
        CXX = join(gcc_path, "bin", "arm-none-eabi-g++.exe"),
        GDB = join(gcc_path, "bin", "arm-none-eabi-gdb.exe"),
        NM = join(gcc_path, "bin", "arm-none-eabi-gcc-nm.exe"),
        LINK = join(gcc_path, "bin", "arm-none-eabi-gcc.exe"),
        OBJCOPY = join(gcc_path, "bin", "arm-none-eabi-objcopy.exe"),
        OBJDUMP = join(gcc_path, "bin", "arm-none-eabi-objdump.exe"),
        RANLIB = join(gcc_path, "bin", "arm-none-eabi-gcc-ranlib.exe"),
        SIZETOOL = join(gcc_path, "bin", "arm-none-eabi-size.exe"),
    )
elif system == "Linux":
    gcc_path = join(FRAMEWORK_DIR, "ql_tools", "gcc-arm-none-eabi-5_4-2016q3")
    if not os.path.exists(gcc_path):
        os.system("tar -xvf " + join(FRAMEWORK_DIR, "ql_tools", "gcc-arm-none-eabi-5_4-2016q3.tar.bz2") + " -C " + join(FRAMEWORK_DIR, "ql_tools"))

    upload_port = 0
    try:
        if "/dev/ttyUSB" in env["UPLOAD_PORT"]:
            upload_port = int(env["UPLOAD_PORT"][11:])
    except Exception as e:
        pass

    env.Replace(
        UPLOADER=FRAMEWORK_DIR + "/ql_tools/bk_loader/bk_loader",
        UPLOADERFLAGS=[
            "-p", upload_port,
            "-b", "921600",
            "-i",
        ],
        UPLOADCMD='sudo $UPLOADER download $UPLOADERFLAGS $SOURCE',
    )

    env.Replace(
        AR = join(gcc_path, "bin", "arm-none-eabi-ar"),
        AS = join(gcc_path, "bin", "arm-none-eabi-gcc"),
        CC = join(gcc_path, "bin", "arm-none-eabi-gcc"),
        CXX = join(gcc_path, "bin", "arm-none-eabi-g++"),
        GDB = join(gcc_path, "bin", "arm-none-eabi-gdb"),
        NM = join(gcc_path, "bin", "arm-none-eabi-gcc-nm"),
        LINK = join(gcc_path, "bin", "arm-none-eabi-gcc"),
        OBJCOPY = join(gcc_path, "bin", "arm-none-eabi-objcopy"),
        OBJDUMP = join(gcc_path, "bin", "arm-none-eabi-objdump"),
        RANLIB = join(gcc_path, "bin", "arm-none-eabi-gcc-ranlib"),
        SIZETOOL = join(gcc_path, "bin", "arm-none-eabi-size"),
    )
else:
    print("Unsupported operating system")
    exit(1)

env.Append(
    LDSCRIPT_PATH=join(FRAMEWORK_DIR, "ql_build", "bk7231n_bsp.lds"),
    ASFLAGS=[
        "-g",
        "-marm",
        "-mthumb-interwork",
        "-mcpu=arm968e-s",
        "-march=armv5te",
        "-x",
        "assembler-with-cpp"
    ],
    ASPPFLAGS=[
        "-g",
        "-marm",
        "-mthumb-interwork",
        "-mcpu=arm968e-s",
        "-march=armv5te",
        "-x",
        "assembler-with-cpp"
    ],
    CCFLAGS=[
        "-g",
        "-mthumb",
        "-mcpu=arm968e-s",
        "-march=armv5te",
        "-mthumb-interwork",
        "-mlittle-endian",
        "-Os",
        "-std=c99",
        "-ffunction-sections",
        "-Wall",
        "-Wno-implicit-function-declaration",
        "-Wno-format",
        "-Wno-unknown-pragmas",
        "-fsigned-char",
        "-fdata-sections",
        "-nostdlib",
        "-fno-strict-aliasing"
    ],
    CFLAGS = [
        "-g",
        "-mthumb",
        "-mcpu=arm968e-s",
        "-march=armv5te",
        "-mthumb-interwork",
        "-mlittle-endian",
        "-Os",
        "-std=c99",
        "-ffunction-sections",
        "-Wall",
        "-Wno-implicit-function-declaration",
        "-Wno-format",
        "-Wno-unknown-pragmas",
        "-fsigned-char",
        "-fdata-sections",
        "-nostdlib",
        "-fno-strict-aliasing"
    ],
    CXXFLAGS = [
        "-g",
        "-mthumb",
        "-mcpu=arm968e-s",
        "-march=armv5te",
        "-mthumb-interwork",
        "-mlittle-endian",
        "-Os",
        "-std=c99",
        "-ffunction-sections",
        "-Wall",
        "-Wno-implicit-function-declaration",
        "-Wno-format",
        "-Wno-unknown-pragmas",
        "-fsigned-char",
        "-fdata-sections",
        "-nostdlib",
        "-fno-strict-aliasing"
    ],
    CPPDEFINES = [
        ("SYS_CONFIG_FILE", r"\"sys_config.h\""),
        ("MBEDTLS_CONFIG_FILE", r"\"tls_config.h\""),
        ("CFG_OS_FREERTOS", 1),
    ],
    LINKFLAGS=[
        "-g",
        "-Wl,--gc-sections",
        "-marm",
        "-mcpu=arm968e-s",
        "-mthumb-interwork",
        "-nostdlib",
        "-Xlinker",
        "-Map=${TARGET}.map",
        "-Wl,-wrap,malloc",
        "-Wl,-wrap,_malloc_r",
        "-Wl,-wrap,free",
        "-Wl,-wrap,_free_r",
        "-Wl,-wrap,zalloc",
        "-Wl,-wrap,calloc",
        "-Wl,-wrap,realloc",
        "-Wl,-wrap,_realloc_r",
        "-Wl,-wrap,printf",
        "-Wl,-wrap,vsnprintf",
        "-Wl,-wrap,snprintf",
        "-Wl,-wrap,sprintf",
        "-Wl,-wrap,puts",
        "-Wl,-wrap,mbedtls_ssl_handshake_server_step",
        "-Wl,-wrap,mbedtls_ssl_handshake_client_step",
        "-Wl,-wrap,mbedtls_ssl_write_client_hello",
        "-Wl,-wrap,mbedtls_ssl_read",
        "-Wl,-wrap,mbedtls_ssl_write",
        "-Wl,-wrap,mbedtls_ssl_free",
        "-Wl,-wrap,mbedtls_ssl_session_reset",
        "-Wl,-wrap,mbedtls_ssl_setup",
        "-Wl,-wrap,mbedtls_ssl_send_alert_message",
        "-Wl,-wrap,mbedtls_ssl_close_notify",
    ],    
    CPPPATH=[
        join(FRAMEWORK_DIR, "ql_application"),
        join(FRAMEWORK_DIR, "ql_application","quectel_demo","tcp_server"),
        join(FRAMEWORK_DIR, "ql_application","quectel_demo","5500"),
        join(FRAMEWORK_DIR, "ql_application","quectel_demo","5500","w5500"),
        join(FRAMEWORK_DIR, "ql_application","quectel_demo"),
        join(FRAMEWORK_DIR, "ql_application","quectel_demo","tcp_client"),
        join(FRAMEWORK_DIR, "ql_components","curl","include"),
        join(FRAMEWORK_DIR, "ql_components","curl","include","curl"),
        # join(FRAMEWORK_DIR, "ql_components","mbedtls","mbedtls","include"),
        # join(FRAMEWORK_DIR, "ql_components","mbedtls","mbedtls","include","mbedtls"),
        join(FRAMEWORK_DIR, "ql_components","mbedtls","mbedtls-2.27.0","include"),
        join(FRAMEWORK_DIR, "ql_components","mbedtls","mbedtls-2.27.0","include","mbedtls"),
        join(FRAMEWORK_DIR, "ql_components","mbedtls","mbedtls-port","inc"),
        join(FRAMEWORK_DIR, "ql_components","mbedtls","mbedtls_ui"),
        join(FRAMEWORK_DIR, "ql_components","lwip_intf","lwip-2.0.2","arch"),
        join(FRAMEWORK_DIR, "ql_components","lwip_intf","lwip-2.0.2","port"),
        join(FRAMEWORK_DIR, "ql_components","lwip_intf","lwip-2.0.2","src","include","lwip"),
        join(FRAMEWORK_DIR, "ql_components","lwip_intf","lwip-2.0.2","src","include","posix"),
        join(FRAMEWORK_DIR, "ql_components","lwip_intf","lwip-2.0.2","src","include","netif"),
        join(FRAMEWORK_DIR, "ql_components","lwip_intf","lwip-2.0.2","src","include"),
        join(FRAMEWORK_DIR, "ql_components","lwip_intf","dhcpd"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","wolfssl"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","mac"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","ke"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","umac","src","rxu"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","umac","src","bam"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","umac","src","txu"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","umac","src","llc"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","umac","src","mesh"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","umac","src","mfp"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","umac","src","apm"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","umac","src","sm"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","umac","src","scanu"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","umac","src","me"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","umac","src","rc"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","rwnx"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","bfr"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","vif"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","mm"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","tpc"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","p2p"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","td"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","rx"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","rx","rxl"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","sta"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","ps"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","tx"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","tx","txl"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","rd"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","scan"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","chan"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","hal"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","lmac","src","tdls"),
        join(FRAMEWORK_DIR, "ql_kernel","ip","common"),
        join(FRAMEWORK_DIR, "ql_kernel","os","include"),
        join(FRAMEWORK_DIR, "ql_kernel","os","FreeRTOSv9.0.0"),
        join(FRAMEWORK_DIR, "ql_kernel","os","FreeRTOSv9.0.0","Source","include"),
        join(FRAMEWORK_DIR, "ql_kernel","os","FreeRTOSv9.0.0","Source","portable","Keil","ARM968es"),
        join(FRAMEWORK_DIR, "ql_kernel","app","led"),
        join(FRAMEWORK_DIR, "ql_kernel","app","net_work"),
        join(FRAMEWORK_DIR, "ql_kernel","app","standalone-ap"),
        join(FRAMEWORK_DIR, "ql_kernel","app","tftp"),
        join(FRAMEWORK_DIR, "ql_kernel","app"),
        join(FRAMEWORK_DIR, "ql_kernel","app","ftp"),
        join(FRAMEWORK_DIR, "ql_kernel","app","http"),
        join(FRAMEWORK_DIR, "ql_kernel","app","standalone-station"),
        join(FRAMEWORK_DIR, "ql_kernel","app","config"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","include"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","sys_ctrl"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","wdt"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","codec"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","uart"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","beken_ble_sdk","hci","include"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","beken_ble_sdk","host","include"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","beken_ble_sdk","sys","include"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","beken_ble_sdk","controller","include"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","beken_ble_sdk","mesh","include"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","beken_ble_sdk","mesh","src","models","include"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","beken_ble_sdk","mesh","src","dbg"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","profiles","comm","api"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","profiles","sdp","api"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","profiles","prf","include"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","plactform","arch"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","plactform","include"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","plactform","driver","sys_ctrl"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","plactform","driver","uart"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","plactform","driver","reg"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","plactform","driver","ir"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","plactform","driver","ble_icu"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","plactform","modules","include"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","config"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","modules","mesh_model","ali"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","modules","app","api"),
        # join(FRAMEWORK_DIR, "ql_kernel","driver","ble","modules","gernel_api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","rc_beken"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","spidma"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","general_dma"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","i2c"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","sdcard"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","flash"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","phy"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","saradc"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","i2s"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","sdio"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","jpeg"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","fft"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","arch","armv5","compiler"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","arch","armv5"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","arch","armv5","ll"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","hci","src"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","hci","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","hl","inc"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","hl","src","gatt","gattc"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","hl","src","gatt","gattm"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","hl","src","gatt","atts"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","hl","src","gatt","attm"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","hl","src","gatt"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","hl","src","gatt","attc"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","hl","src","gap","gapc"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","hl","src","gap","gapm"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","hl","src","l2c","l2cm"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","hl","src","l2c","l2cc"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","hl","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","ll","import","reg"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","ll","src"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","ll","src","llm"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","ll","src","llc"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","ll","src","lld"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","ble","ll","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","em","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","sch","import"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","ip","sch","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","modules","ke","src"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","modules","ke","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","modules","aes","src"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","modules","aes","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","modules","h4tl","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","modules","common","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","modules","ecc_p256","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","modules","dbg","src"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_lib","modules","dbg","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_pub","ui"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_pub","prf"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_pub","profiles","comm","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_pub","profiles","sdp","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","ble_pub","app","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","platform","7231n","rwip","import","reg"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","platform","7231n","rwip","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","platform","7231n","driver","rf"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","platform","7231n","driver","uart"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","platform","7231n","driver","reg"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","platform","7231n","entry"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","platform","7231n","config"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","ble_5_x_rw","platform","7231n","nvds","api"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","rw_pub"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","irda"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","qspi"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","intc"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","icu"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","entry"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","dma"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","gpio"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","macphy_bypass"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","security"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","spi"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","audio"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","pwm"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","common","reg"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","common"),
        join(FRAMEWORK_DIR, "ql_kernel","driver","calendar"),
        join(FRAMEWORK_DIR, "ql_kernel","common"),
        join(FRAMEWORK_DIR, "ql_kernel"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","include"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","temp_detect"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","misc"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","video_transfer"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","force_sleep"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","base64"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","user_driver"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","saradc_intf"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","ethernet_intf"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","sensor"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","rwnx_intf"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","wlan_ui"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","airkiss"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","power_save"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","joint_up"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","bk7011_cal"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","security"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","camera_intf"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","spidma_intf"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","sim_uart"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","hostapd_intf"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","easy_flash","inc"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","easy_flash"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","easy_flash","port"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","ble_wifi_exchange"),
        join(FRAMEWORK_DIR, "ql_components","qadpt","include"),
        join(FRAMEWORK_DIR, "ql_components","paho-mqtt","client"),
        join(FRAMEWORK_DIR, "ql_components","paho-mqtt","client","src"),
        join(FRAMEWORK_DIR, "ql_components","paho-mqtt","mqtt_ui"),
        join(FRAMEWORK_DIR, "ql_components","paho-mqtt","mqtt_ui","ssl_mqtt"),
        join(FRAMEWORK_DIR, "ql_components","paho-mqtt","mqtt_ui","tcp_mqtt"),
        join(FRAMEWORK_DIR, "ql_components","paho-mqtt","packet"),
        join(FRAMEWORK_DIR, "ql_components","paho-mqtt","packet","src"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","wpa_supplicant_2_9","src","utils"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","wpa_supplicant_2_9","src","ap"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","wpa_supplicant_2_9","src","common"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","wpa_supplicant_2_9","src","drivers"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","wpa_supplicant_2_9","src","wps"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","wpa_supplicant_2_9","src"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","wpa_supplicant_2_9","bk_patch"),
        join(FRAMEWORK_DIR, "ql_components","bk_func","wpa_supplicant_2_9","hostapd"),
        join(FRAMEWORK_DIR, "ql_build"),
        join(FRAMEWORK_DIR, "ql_application"),
    ],
    
    LIBPATH=[
        join(FRAMEWORK_DIR, "ql_build", "prebuilds")
    ],
    LIBS=[
        "libdriver",
        "libairkiss",
        "libbk_app", 
        "libsensor", 
        "libuart_debug",
        "libsupplicant",
        "librf_test",
        "libfunc", 
        "libos",  
        "librf_use",  
        "librwnx", 
        "librtos",  
        "libble",  
        "libquectel_api",        
        "libcal"
    ],
    BUILDERS=dict(
        ElfToBin=Builder(
            action=env.VerboseAction(
                " ".join(["$OBJCOPY", "-O", "binary", "$SOURCES", "$TARGET"]),
                "Building $TARGET",
            ),
            suffix=".bin",
        ),
        GenFirmBin=Builder(
            action=env.VerboseAction(
                gen_firmware_bin, "Building " + join("$BUILD_DIR", "firmware_bin")
            ),
        ),
    ),
    upload_source = join(env["PROJECT_BUILD_DIR"], board.get('name'), "${PROGNAME}.bin"),
)

libs = [
    env.BuildLibrary(
        join("$BUILD_DIR", "ql_app"),
        join(FRAMEWORK_DIR, "ql_application"),
        [
            "+<ql_app.c>"
        ],
    ),
    env.BuildLibrary(
        join("$BUILD_DIR", "ql_demo"),
        join(FRAMEWORK_DIR, "ql_application", "quectel_demo"),
        [
            "+<ql_lowpower_demo.c>",
            "+<ql_flash_demo.c>",
            "+<ql_uart_ymodem_upgrade_demo.c>",
            "+<tcp_server/mongoose.c>",
            "+<tcp_server/tcp_websocket_server.c>",
            "+<ql_ble_config_network_demo.c>",
            "+<ql_mqtt_demo.c>",
            "+<ql_ble_demo.c>",
            "+<ql_ble_multi_service_demo.c>",
            "+<ql_watchdog_demo.c>",
            "+<ql_wlan_config_network_demo.c>",
            "+<ql_adc_demo.c>",
            "+<5500/wizchip_test.c>",
            "+<5500/wizchip_conf.c>",
            "+<5500/w5500/w5500.c>",
            "+<5500/wizchip_port.c>",
            "+<5500/wizchip_ethnetif.c>",
            "+<ql_ftp_demo_c.c>",
            "+<ql_uart_demo.c>",
            "+<ql_timer_demo.c>",
            "+<ql_osi_demo.c>",
            "+<ql_wlan_demo.c>",
            "+<ql_i2c_eeprom_demo.c>",
            "+<ql_tls_demo.c>",
            "+<ql_gpio_demo.c>",
            "+<tcp_client/tcp_client_demo.c>",
            "+<ql_spi_flash_demo.c>",
            "+<ql_pwm_demo.c>",
            "+<ql_spi_demo.c>",
            "+<ql_http_demo.c>",
            "+<ql_ble_ams_ancs_demo.c>",
            "+<ql_ble_pair_demo.c>"
        ],
    ),
    env.BuildLibrary(
        join("$BUILD_DIR", "mbedtls"),
        join(FRAMEWORK_DIR, "ql_components", "mbedtls"),
        [
            "+<mbedtls-port/src/*.c>",
            "+<mbedtls-2.27.0/library/*.c>",
            "+<mbedtls_ui/*.c>"
        ],
    ),
    env.BuildLibrary(
        join("$BUILD_DIR", "paho_mqtt"),
        join(FRAMEWORK_DIR, "ql_components", "paho_mqtt"),
        [
            "+<client/src/*.c>",
            "+<mqtt_ui/*.c>",
            "+<packet/src/*.c>",
            "+<client/paho_mqtt_udp.c>",
        ],
    ),
    env.BuildLibrary(
        join("$BUILD_DIR", "curl"),
        join(FRAMEWORK_DIR, "ql_components", "curl"),
        [
            "+<src/*.c>",
            "+<src/vauth/*.c>",
            "+<src/vquic/*.c>",
            "+<src/vssh/*.c>",
            "+<src/vtls/*.c>",
        ],
    ),
    env.BuildLibrary(
        join("$BUILD_DIR", "lwip"),
        join(FRAMEWORK_DIR, "ql_components", "lwip_intf"),
        [
            "+<lwip-2.0.2/port/ethernetif.c>",
            "+<lwip-2.0.2/port/net.c>",
            "+<lwip-2.0.2/port/sys_arch.c>",
            "+<lwip-2.0.2/src/api/api_lib.c>",
            "+<lwip-2.0.2/src/api/api_msg.c>",
            "+<lwip-2.0.2/src/api/err.c>",
            "+<lwip-2.0.2/src/api/netbuf.c>",
            "+<lwip-2.0.2/src/api/netdb.c>",
            "+<lwip-2.0.2/src/api/netifapi.c>",
            "+<lwip-2.0.2/src/api/sockets.c>",
            "+<lwip-2.0.2/src/api/tcpip.c>",
            "+<lwip-2.0.2/src/core/def.c>",
            "+<lwip-2.0.2/src/apps/ping/ping.c>",
            "+<lwip-2.0.2/src/core/dns.c>",
            "+<lwip-2.0.2/src/core/inet_chksum.c>",
            "+<lwip-2.0.2/src/core/init.c>",
            "+<lwip-2.0.2/src/core/ip.c>",
            "+<lwip-2.0.2/src/core/ipv4/dhcp.c>",
            "+<lwip-2.0.2/src/core/ipv4/etharp.c>",
            "+<lwip-2.0.2/src/core/ipv4/icmp.c>",
            "+<lwip-2.0.2/src/core/ipv4/igmp.c>",
            "+<lwip-2.0.2/src/core/ipv4/ip4_addr.c>",
            "+<lwip-2.0.2/src/core/ipv4/ip4.c>",
            "+<lwip-2.0.2/src/core/ipv4/ip4_frag.c>",
            "+<lwip-2.0.2/src/core/ipv6/dhcp6.c>",
            "+<lwip-2.0.2/src/core/ipv6/ethip6.c>",
            "+<lwip-2.0.2/src/core/ipv6/icmp6.c>",
            "+<lwip-2.0.2/src/core/ipv6/inet6.c>",
            "+<lwip-2.0.2/src/core/ipv6/ip6_addr.c>",
            "+<lwip-2.0.2/src/core/ipv6/ip6.c>",
            "+<lwip-2.0.2/src/core/ipv6/ip6_frag.c>",
            "+<lwip-2.0.2/src/core/ipv6/nd6.c>",
            "+<lwip-2.0.2/src/core/ipv6/mld6.c>",
            "+<lwip-2.0.2/src/core/mem.c>",
            "+<lwip-2.0.2/src/core/netif.c>",
            "+<lwip-2.0.2/src/core/memp.c>",
            "+<lwip-2.0.2/src/core/pbuf.c>",
            "+<lwip-2.0.2/src/core/raw.c>",
            "+<lwip-2.0.2/src/core/stats.c>",
            "+<lwip-2.0.2/src/core/sys.c>",
            "+<lwip-2.0.2/src/core/tcp.c>",
            "+<lwip-2.0.2/src/core/tcp_in.c>",
            "+<lwip-2.0.2/src/core/tcp_out.c>",
            "+<lwip-2.0.2/src/core/timeouts.c>",
            "+<lwip-2.0.2/src/core/udp.c>",
            "+<lwip-2.0.2/src/netif/ethernet.c>",
            "+<lwip-2.0.2/src/apps/httpd/httpd.c>",
            "+<lwip-2.0.2/src/apps/httpd/fs.c>",
            "+<dhcpd/dhcp-server.c>",
            "+<dhcpd/dhcp-server-main.c>",
        ],
    ),
]

env.Prepend(LIBS=libs)