# 使用说明

## 语录 group_quotations.py

仿小龙bot（朋友开发）的自定义图片上传和随机发送功能 

原项目地址：https://github.com/MAVERICKdesu/DragonBot

发送 上传语录 或 上传图片 进入上传模式，bot会捕获你接下来的所有消息直到你发送结束或者3次不包含任何图片的消息为止，bot会将捕获到的所有图片保存在该源码同目录下的'/image/[你的群号]/'下（如果不存在这些文件夹的话bot会自动创建）

发送 @bot 群友语录 bot将会随机从该群文件夹中挑选一张图片发出

发送 @bot 语录十连 bot将会随机从该群文件夹中挑选十张图片发出(~~可能重复~~ 不会重复）（数量不足将不会执行）

注：暂未考虑多群/多人同时上传的情况，如遇到此情况且发现存在问题请提交issue我来修复

## 二维码快速生成器 qrcode_maker.py qrmaker.py

二维码生成器项目地址：https://github.com/x-hw/amazing-qr

需要pip install amzqr

发送 !qr [二维码文本] 来快速生成二维码

|可选参数|范围|效果|
| --- | --- | --- |
| [文本] | 任意 | 作为二维码扫描结果的文本，暂不支持中文文本，必须提供 |
| c | c or 不提供 | 采用彩色图片，不提供则为灰度图片 |
| [float1] | 0-1.0 | 对比度 除文本外的第一个float数会被识别为对比度，可选，默认1.0 |
| [float2] | 0-1.0 | 亮度，第二个float数会被识别为亮度，可选，默认1.0 |
| [一张图片] | png,jpg,gif | 生成二维码的底图，可选，图片类型代码会自动识别(理论上支持gif，但是我自己这边一直发不出来gif图片，可能是被压缩了？) |

注1：所有参数分隔用的是空格分隔，所以请勿在文本中间加入空格，'aaa bbb'会被识别为'aaa'和'bbb'导致只传入aaa

注2：已知问题： 1.无法发送gif图片（已修复，如果报错请注释掉源码中几行删除临时文件的代码，临时文件不删除并不会影响下一次使用）

2.无法生成中文二维码：生成器api的问题；[解决方法](https://github.com/x-hw/amazing-qr/pull/59) 按照这个PR中的更改自行去C:\Users\Administrator\AppData\Local\Programs\Python\Python39\Lib\site-packages\amzqr下修改这几处位置即可（注：MyQR和amzqr为同一款二维码生成器，内部源码我都看了，变量名称都一模一样）

3.image = Image.open(BytesIO(await response.content))报错：如果你的命令语句是转发别人的，就会出现这个问题，原因未知

4.生成二维码无法扫描：是腾讯的问题，其他家的扫描器都可以扫描，是qq不支持文本型二维码的显示
