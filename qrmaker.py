import hoshino, os, asyncio
from .qrcode_maker import qrcode
from hoshino import Service,  aiorequests, R
from hoshino.typing import CQEvent, MessageSegment as ms
from PIL import Image, ImageSequence
from io import BytesIO

sv = Service('二维码快速生成', bundle='qrcode', help_=''.strip())

headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6) ",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Language": "zh-cn"
           }
 
    
def get_set(arrs):  #这个是用于解析命令语句
    result = []
    for i in range(4):  #强制保留前4个 不足的补None
        try:
            result.append(arrs[i])
        except:
            result.append(None)
    
    re_result = ['', False, None, None]  #预设默认返回值
    re_result[0] = result[0]  #第一个总视为是文本参数
    index = 0
    for re in result:
        if index == 0:  #跳过第一个
            index += 1
            continue
        if result[index] == 'c':  #检测到C则启用图片彩色模式
            re_result[1] = True
            index += 1
            continue
        if result[index]:  #如果有参数而不是None则继续
            try:  #利用try进行float的强制转换，懒得用.isdigit()
                if not re_result[2]:  
                    re_result[2] = float(result[index])
                else:
                    re_result[3] = float(result[index])
            except: #报错就说明这一位传的有问题，不是数字，直接置为默认值
                if not re_result[2]:
                    re_result[2] = 1.0
                else:
                    re_result[3] = 1.0
            index += 1
            continue
        else:
            index += 1
            continue  #防止漏传没用break，反正也就4个，几乎不影响计算速度
    if not re_result[2] or (re_result[2] * 10) not in range(0, 11): #防止传递的参数超界
        re_result[2] = 1.0
    if not re_result[3] or (re_result[3] * 10) not in range(0, 11):
        re_result[3] = 1.0
        
    return re_result



async def save_img(url): #从消息中拿图
    response = await aiorequests.get(url,
                                     headers=headers)  # aiorequests是hoshino异步封装过的requests 这里可以直接用requests，用reques的话只是无法异步而已
    image = Image.open(BytesIO(await response.content))
    info = image.info

    try:
        image_type = 'gif' if image.n_frames > 1 and image.n_frames <= 200 else 'png'
    except:
        image_type = 'png'

    picture = os.path.join(os.path.dirname(__file__), f'temp.{image_type}')  # 这个是合成以下刚刚的那个path 其实可以先合成再save的（小声）
    # amzqr和MyQR都是从本地读取图片，提供的图片也是本地存储位置而不是Image.open的图片，所有要先保存到本地
    if image_type == 'gif':
        # gif保存
        frames = [f.copy() for f in ImageSequence.Iterator(image)]
        frames[0].save(picture, format='GIF', save_all=True,
                       append_images=frames[1:], disposal=2,
                       quality=80, **info)
    else:
        # png保存
        image.save(os.path.join(os.path.dirname(__file__),
                                f'temp.{image_type}'))
    return picture, image_type

@sv.on_prefix('!qr')
async def qrcode_maker(bot, ev):
    msg = ev.message
    picture, text, image_type = [None, '', 'png']
    for i in msg: #如果消息中含有图片的话，message就会被图片分割成多份，其中图片那部分的type为image，消息的type为text
        if i.type == 'image':
            try:
                picture, image_type = await save_img(i.data['url'])  #image消息中会含有['url']，为这张图片的存储链接，直接拿到这个链接后去requests就可以拿到消息中包含的图片
            except:
                await bot.send(ev, '图片读取发生错误，您可能是转发的含图消息，请不要转发')
                return
        elif i.type == 'text':
            arrs = str(i).split()
            text, colorized, contrast, brightness = get_set(arrs)
        if picture and text:
            break
    try:
        qr = qrcode(text, picture = picture, colorized = colorized, contrast = contrast, brightness = brightness, image_type = image_type)
    except:
        await bot.send(ev, '二维码生成发生错误，暂不支持生成中文二维码哦')  #amzqr和MyQR均有字符验证，只支持数字和字母输入，如果不符合会直接返回说字符验证不通过，可以手动去除那个验证
        return
    await bot.send(ev, ms.image(qr.base64_str))  #发送消息，方法挺多的
    #await bot.send(ev, R.img(f'temp_qrcode.{image_type}').cqcode)
    if picture:
        os.remove(picture) #别忘了删掉临时保存的图片，其实不删影响好像也不是很大
    return
    
