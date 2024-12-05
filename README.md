# platform-quectel

### Install
PIO Home > Platforms > Advanced Installation

Enter https://github.com/Fatmear/platform-quectel and click install

### Q&A
Q1:烧录时Ubuntu报错："could not open port /dev/ttyUSB0: [Errno 13] Permission denied: ‘/dev/ttyUSB0"

A1:使用如下命令将当前用户放入dailout组中，重启生效
  
```
sudo usermod -aG dialout user
reboot
```
<br>

Q2:Windows编译报错："libxxx.a: file format not recognized; treating as linker script"

A2:这是由于Windows下拉取Git仓库时会自动将非Windows的换行符自动转换为Windows的换行符，导致编译失败，执行如下命令后重新拉取仓库可解决该问题

```
git config --global core.autocrlf false
```
