<p align="center">
<img src="logo.svg" width="60%" >
</p>

[English](README.md) | 中文

# PlatformIO OpenCPU开发平台

当前支持的特性：

> ✔ 适配多款模组 <br>
> ✔ 支持CSDK开发 <br>
> ✔ 支持一键编译和下载 <br>
> ❌ 暂不支持Arduino开发 <br>
> ❌ 暂不支持调试器 <br>
> ❌ 暂不支持PlatformIO公共库 <br>

| 模组    | RAM   | ROM | 用户代码可用RAM | 用户代码可用ROM | CSDK | Arduino | 编译 | 烧录 | 调试器 |
| ------- | ----- | --- | --------------- | --------------- | ---- | ------- | ---- | ---- | ------ |
| FC41D   | 256KB | 2M  | 125KB           | 249KB           | √    | ×       | √    | √    | ×      |
| FGM842D | 288KB | 2M  | 126KB           | 233KB           | √    | ×       | √    | √    | ×      |
| FCM360W | 512KB | 4M  | 130KB           | 1000KB          | √    | ×       | √    | √    | ×      |

### 安装
------------------
打开PlatformIO依次进入如下菜单：`PIO Home` > `Platforms` > `Advanced Installation`。

在弹窗中输入：`https://github.com/Fatmear/platform-quectel` 并点击`install`按钮。

### Q&A
------------------
#### Q1:烧录时Ubuntu报错：`"could not open port /dev/ttyUSB0: [Errno 13] Permission denied: ‘/dev/ttyUSB0"`。

A1:使用如下命令将当前用户放入dailout组中，重启生效：
  
```
sudo usermod -aG dialout user
reboot
```

#### Q2:Windows编译报错：`"libxxx.a: file format not recognized; treating as linker script"`。

A2:这是由于Windows下拉取Git仓库时会自动将非Windows的换行符自动转换为Windows的换行符，导致编译失败，执行如下命令后重新拉取仓库可解决该问题：

```
git config --global core.autocrlf false
```

### 官网
--------------------
移远通信官网：https://www.quectel.com.cn/

移远通信-短距离官网：https://short-range.quectel.com/
