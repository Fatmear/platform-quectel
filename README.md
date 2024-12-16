<p align="center">
<img src="logo.svg" width="60%" >
</p>

English | [中文](README_CN.md)

# OpenCPU development platform for PlatformIO

Currently supported features:

| module  | RAM   | ROM | user code available RAM | user code available ROM | CSDK | Arduino | compile | download | debuger |
| ------- | ----- | --- | ----------------------- | ----------------------- | ---- | ------- | ------- | -------- | ------- |
| FC41D   | 256KB | 2M  | 125KB                   | 249KB                   | √    | ×       | √       | √        | ×       |
| FGM842D | 288KB | 2M  | 126KB                   | 233KB                   | √    | ×       | √       | √        | ×       |
| FCM360W | 512KB | 4M  | 130KB                   | 1000KB                  | √    | ×       | √       | √        | ×       |

### Install
------------------
Open PlatformIO and enter the following menu: `PIO Home` > `Platforms` >` Advanced Installation `.

In the popup window input: `https://github.com/Fatmear/platform-quectel` and click on `install` button.

### Q&A
------------------
#### Q1: Ubuntu error when burning: `"could not open port /dev/ttyUSB0: [Errno 13] Permission denied:' /dev/ttyUSB0"`.

A1: Run the following command to add the current user to the dailout group for the restart to take effect:

```
sudo usermod -aG dialout username
reboot
```

#### Q2:Windows compiler error: `"libxxx.a: file format not recognized; treating as linker script"`.

A2: This is because when Windows pull-down Git repository, non-Windows line breaks are automatically converted to Windows line breaks, resulting in compilation failure. To solve this problem, run the following command to pull the repository again:

```
git config --global core.autocrlf false
```

### Official website
--------------------
Quectel: https://www.quectel.com.cn/

Quectel - Short Range: https://short-range.quectel.com/
