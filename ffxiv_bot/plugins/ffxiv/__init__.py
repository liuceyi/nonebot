from nonebot import on_command, on_message
from nonebot.rule import to_me
from nonebot.adapters import Message, Event, Bot
import nonebot.adapters.qq as QQ
import nonebot.adapters.console as Console
import nonebot.adapters.kaiheila as KOOK
from nonebot.params import CommandArg, ArgPlainText, EventPlainText, EventMessage
from nonebot.matcher import Matcher

from .scrapper import universalis_scrapper, cn_current_scrapper
from .model import chat_model
from .save import local_save, local_load
from .visualize import visualizer

import time

QQBOT_URL = 'https://sandbox.api.sgroup.qq.com'
EOP = """
"""
LOCAL_SAVE_PATH = 'save'
LOCAL_SAVE_CHANNELS_FNAME = 'channels.pkl'

channels_binded = local_load(LOCAL_SAVE_PATH, LOCAL_SAVE_CHANNELS_FNAME)
us = universalis_scrapper()
ccs = cn_current_scrapper()
cm = chat_model()
vs = visualizer()


# region rules for validation
async def is_binded_channel(event: KOOK.Event) -> bool: # 规则：是否绑定频道
    channel_id = event.target_id
    
    result = channel_id in channels_binded['channel_id'].values
    return result
# endregion

# region command

tax_rate = on_command('税率', priority=1, block=True)
item_price = on_command('价格', priority=1, block=True)
item_trend = on_command('趋势', priority=1, block=True)
bind_kook_channel = on_command('绑定频道', priority=2, block=True)
chat_kook = on_message(priority=9, rule=is_binded_channel, block=True)
chat = on_message(priority=10, rule=to_me(), )

# endregion

# region tax_rate

def get_tax_rate_list(server):
    for us_server in us.server_list:
        if server == us_server['name']:
            tax_rate = us.get_tax_rate(world_name=server)
            return tax_rate
    return False

@tax_rate.handle()
async def tax_rate_handle(matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text():        
        matcher.set_arg("server", args)

@tax_rate.handle()
async def tax_rate_handle_normal(bot:QQ.Bot|Console.Bot, server: str=ArgPlainText()):
    tax_rate_list = get_tax_rate_list(server)
    tax_rate_str = ','.join([f'{city}:{tax}' for city, tax in tax_rate_list.items()]) # type: ignore
    if tax_rate_str:
        await tax_rate.finish(f"今天{server}的税率是{tax_rate_str}")
    else:
        await tax_rate.finish(f"艾欧泽亚真的有 {server} 这个地方吗？")

@tax_rate.handle()
async def tax_rate_handle_KOOK(bot:KOOK.Bot, server: str=ArgPlainText()):
    tax_rate_list = get_tax_rate_list(server)
    if tax_rate_list:
        await tax_rate.finish(
            KOOK.MessageSegment.Card(
                [
                    {
                        "type": "card",
                        "theme": "secondary",
                        "size": "lg",
                        "modules": [
                        {
                            "type": "section",
                            "text": {
                            "type": "paragraph",
                            "cols": 2,
                            "fields": [
                                {
                                "type": "kmarkdown",
                                "content": "**城市**\n" + "\n".join([city for city in tax_rate_list.keys()])
                                },
                                {
                                "type": "kmarkdown",
                                "content": "**税率**\n" + "\n".join([str(tax)+'%' for tax in tax_rate_list.values()])
                                }
                            ]
                            }
                        }
                        ]
                    }
                ]
            )
        )
    else:
        await tax_rate.finish(f"艾欧泽亚真的有 {server} 这个地方吗？")

# @tax_rate.got("server", prompt="请输入服务器")
# async def got_server(server: str = ArgPlainText()):
#     print('here2')
#     tax_rate_str = get_tax_rate_str(server)
#     if tax_rate_str:
#         await tax_rate.finish(f"今天{server}的税率是{tax_rate_str}")
#     else:
#         await server.reject(f"你想查询的服务器 {server} 暂不支持，请重新输入！")

# endregion

# region item_price
def get_item_price_str(item_name):
    item_searched = ccs.get_item_full_name(item_name)
    # item_searched = us.get_item_id(item_name)

    if not item_searched: # 未能搜到对应物品
        return '这是什么，艾欧泽亚好像没有呀'
    else:
        if item_name != item_searched:
            prefix_str = f"模糊匹配到{item_searched}{EOP}"
        else:
            prefix_str = f'{EOP}'
    market_formated = ccs.get_item_price(item_searched)
    # market_formated = us.get_item_price(item_searched['ID'])

    output_str = prefix_str
    for market_name, market in market_formated.items(): # type: ignore
        output_str += f'|{market_name}| 近期均价:{market["current_avg_price"]:.0f}, 最新价格:{market["last_purchase_price"]}, 热度:{market["sale_tag"]}{EOP}'
    output_str = output_str[:-1]
    return output_str

@item_price.handle()
async def item_price_handle(matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("item_name", args)

@item_price.handle()
async def item_price_handle_normal(bot:QQ.Bot|Console.Bot, item_name: str=ArgPlainText()):
    print(item_name)
    item_price_str = get_item_price_str(item_name=item_name)
    if item_price_str:
        await item_price.finish(item_price_str)

@item_price.handle()
async def item_price_handle_kook(bot:KOOK.Bot, item_name: str=ArgPlainText()):
    item_searched = ccs.get_item_full_name(item_name)
    # item_searched = us.get_item_id(item_name)
    if not item_searched: # 未能搜到对应物品
        await item_price.finish('这是什么，艾欧泽亚好像没有呀')
    else:
        section_title = f"(font)模糊匹配到(font)[warning]`{item_searched}`" if item_name != item_searched else f"匹配到`{item_searched}`"
    market_formated = ccs.get_item_price(item_searched)
    # market_formated = us.get_item_price(item_searched)
    def change_color_by_tag(tag_str):
        if tag_str == '无人问津':
            tag_str = f'(font){tag_str}(font)[info]'
        elif tag_str == '小有名气':
            tag_str = f'(font){tag_str}(font)[success]'
        elif tag_str == '备受关注':
            tag_str = f'(font){tag_str}(font)[purple]'
        elif tag_str == '明星商品':
            tag_str = f'(font){tag_str}(font)[warning]'
        elif tag_str == '超级热门':
            tag_str = f'(font){tag_str}(font)[pink]'
        return tag_str

    await item_price.finish(
        KOOK.MessageSegment.Card(
            [
                {
                    "type": "card",
                    "theme": "secondary",
                    "size": "lg",
                    "modules": [
                    {
                        "type": "section",
                        "text": {
                        "type": "kmarkdown",
                        "content": section_title
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                        "type": "paragraph",
                        "cols": 3,
                        "fields": [
                            {
                            "type": "kmarkdown",
                            "content": "**服务器**\n" + "\n".join([market_name for market_name in market_formated.keys()])
                            },
                            {
                            "type": "kmarkdown",
                            "content": "**最新价格**\n" + "\n".join([f':moneybag:{market["last_purchase_price"]:.0f}' for market in market_formated.values()])
                            },
                            {
                            "type": "kmarkdown",
                            "content": "**热度**\n" + "\n".join([change_color_by_tag(market["sale_tag"]) for market in market_formated.values()])
                            }
                        ]
                        }
                    }
                    ]
                }
            ]
        )
    )
    
# endregion

# region item_trend
@item_trend.handle()
async def item_trend_handle(matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("item_server", args)

@item_trend.handle()
async def item_trend_handle_QQ(bot:QQ.Bot, item_server: str=ArgPlainText()):
    args_list = str(item_server).split(' ')
    item_name = args_list[0]
    server_name = args_list[1]

    item_searched = ccs.get_item_full_name(item_name)
    # item_searched = us.get_item_id(item_name)
    if not item_searched: # 未能搜到对应物品
        await item_price.finish('这是什么，艾欧泽亚好像没有呀')
        return
    trend = ccs.get_item_trend(item_full_name=item_searched, server_name=server_name)
    flink = vs.get_bar_line_chart(
        trend['dates'], 
        trend['values'][1]['value'], 
        trend['values'][0]['value'], 
        name1='quantity', 
        name2='price', 
        title=f'[{server_name}]{item_searched}'
    )
    await item_price.finish(
        QQ.MessageSegment.image(flink)
    )

@item_trend.handle()
async def item_trend_handle_kook(bot:KOOK.Bot, item_server: str=ArgPlainText()):
    args_list = str(item_server).split(' ')
    item_name = args_list[0]
    server_name = args_list[1]

    item_searched = ccs.get_item_full_name(item_name)
    # item_searched = us.get_item_id(item_name)
    if not item_searched: # 未能搜到对应物品
        await item_price.finish('这是什么，艾欧泽亚好像没有呀')
        return


    trend = ccs.get_item_trend(item_full_name=item_searched, server_name=server_name)
    flink = vs.get_bar_line_chart(
        trend['dates'], 
        trend['values'][1]['value'], 
        trend['values'][0]['value'], 
        name1='quantity', 
        name2='price', 
        title=f'[{server_name}]{item_searched}'
    )
    await item_price.finish(
        KOOK.MessageSegment.Card(
            [
                {
                    "type": "card",
                    "theme": "secondary",
                    "size": "lg",
                    "modules": [
                    {
                        "type": "container",
                        "elements": [
                        {
                            "type": "image",
                            "src": flink
                        }
                        ]
                    }
                    ]
                }
            ]
        )
    )

# endregion


# region bind_kook_channel
@bind_kook_channel.handle()
async def bind_kook_channel_handle(bot: Bot, event: KOOK.Event):
    global channels_binded
    if event.channel_type == 'GROUP':
        print(event)
        server_id = event.extra.guild_id
        channel_id = event.target_id
        roles = event.extra.author.roles # type: ignore
        res = await bot.guildRole_list(guild_id=server_id)
        role_list = res.roles
        for role in roles: # type: ignore
            permissions = None
            for role_setting in role_list:
                if role == role_setting.role_id:
                    permissions = role_setting.permissions
                    break
            if not permissions: 
                await bind_kook_channel.finish('抱歉，你的职级权限不够哦')
                return

            
            bitValue = 5 # 对应频道管理权限
            if permissions & (1 << bitValue)  == (1 << bitValue): # 存在该权限
                if channel_id in channels_binded['channel_id'].values:
                    await bind_kook_channel.finish('我已经在这上班啦')
                    return
                # 绑定该频道，保存信息到pkl文件中
                channels_binded = channels_binded._append({'server_id': server_id, 'channel_id': channel_id}, ignore_index=True) # type: ignore # 将频道加入到本地存储中
                channels_binded.drop_duplicates(inplace=True)
                local_save(LOCAL_SAVE_PATH, LOCAL_SAVE_CHANNELS_FNAME, channels_binded)
                await bind_kook_channel.finish('那这里就是我的咨询室啦，有问题可以直接问我~')

# endregion

# region chat_kook

@chat_kook.handle()
async def chat_kook_handle(bot:KOOK.Bot, chat_str: str = EventPlainText()):
    resp = cm.send(chat_str)
    if not resp: return False
    await chat.finish(f'{resp}')

# endregion

# region chat

@chat.handle()
async def chat_handle(bot:Console.Bot, chat_str: str = EventPlainText()):
    resp = cm.send(chat_str)
    if not resp: return False
    await chat.finish(f'{resp}')
    
# endregion