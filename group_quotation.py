import base64, os, random, nonebot
from io import BytesIO
from PIL import Image
from hoshino import Service, aiorequests
from hoshino.typing import CQEvent
from nonebot import on_command, CommandSession

_path = os.path.join(os.path.dirname(__file__), 'image/')
if not os.path.exists(os.path.join(os.path.dirname(__file__), 'image')):
    os.mkdir(os.path.join(os.path.dirname(__file__), 'image'))
sv = Service('群友语录', help_="")

headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6) ",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Language": "zh-cn"
           }

message_type = 1  #十连发送时的消息类型 1：转发消息 0：普通消息

def render_forward_msg(msg_list: list):
    forward_msg = []
    for msg in msg_list:
        forward_msg.append({
            "type": "node",
            "data": {
                "name": '某不愿透露姓名的小环奈', #修改这里可以让bot转发消息时显示其他人
                "uin": '2779874515',
                "content": msg
            }
        })
    return forward_msg


def get_all_img_url(event): #从消息中提取图片URL
    all_url = []
    for i in event["message"]:
        if i["type"] == "image":
            all_url.append(i["data"]["url"])
    return all_url

def con_num(_path): #保存时计数
    num = len(sorted(fn for fn in os.listdir(_path)))
    return num

send_times = 0 #用于计算触发上传后发送了几句不含图片语句，超过3句将自动结束上传，防止卡死
async def save_img(image_url, gid): #保存图片
    global send_times
    try:
        if len(image_url) == 0:
            send_times += 1 
            return '', send_times
        for url in image_url:
            response = await aiorequests.get(url, headers=headers)
            image = Image.open(BytesIO(await response.content))
            if not os.path.exists(f'{_path}{gid}'):
                os.mkdir(f'{_path}{gid}')
            image.save(f'{_path}{gid}/{con_num(_path + gid) + 1}.png')
            
        return '图片保存成功\n', send_times
    except:
        return '保存失败\n', send_times

@on_command('upload', only_to_me=False, aliases=('上传图片', '上传语录')) #hoshino无法这样处理就用none了
async def upload(session: CommandSession):
    gid = str(session.ctx["group_id"])
    session.get('', prompt='发送要上传的图片,暂不支持gif') #开始捕获该用户的所有消息
    global send_times
    if session.current_arg != '结束': #不是结束就继续
        all_img_url = get_all_img_url(session.ctx)
        msg, times =  await save_img(all_img_url, gid)
        if times <= 3:
            session.pause(msg.strip()) #暂停等待下次捕获消息
        else:
            send_times = 0
            await session.finish('上传结束') #超过3句不含有图片内容将自动结束上传，防止卡死
    await session.send('上传结束')


@sv.on_fullmatch("群友语录",  only_to_me = True) #问就是hoshino用着顺手
async def send_group_img(bot, ev):
    gid = str(ev.group_id)
    try:
        image_list = sorted(fn for fn in os.listdir(f'{_path}{gid}') if fn.endswith('.png')) #从指定目录下获取图片列表
        image = Image.open(f'{_path}{gid}/{random.choice(image_list)}')  #随机取一张图片进行缓存
        buf = BytesIO()
        image.save(buf, format='PNG')
        base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
        await bot.send(ev, f'[CQ:image,file={base64_str}]') #发送图片
    except:
        await bot.send(ev, '没有语录哦')

@sv.on_fullmatch("语录十连",  only_to_me = True)
async def send_group_10(bot, ev):  #和单张发送类似
    gid = str(ev.group_id)
    try:
        image_list = sorted(fn for fn in os.listdir(f'{_path}{gid}') if fn.endswith('.png'))
        if len(image_list) < 10:
            await bot.send(ev, '没有这么多库存哦')
            return
        msg_list = []
        for i in range(10):
            image = Image.open(f'{_path}{gid}/{random.choice(image_list)}')
            buf = BytesIO()
            image.save(buf, format='PNG')
            base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
            msg_list.append(f'[CQ:image,file={base64_str}]')
        if message_type:
            msg = render_forward_msg(msg_list)
            await bot.send(ev, msg)
        else:
            for msg in msg_list:
                await bot.send(ev, msg)
    except:
        await bot.send(ev, '没有语录哦')
