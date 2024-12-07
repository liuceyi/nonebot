import requests
import traceback
from datetime import datetime, timedelta
import json
from urllib.parse import urlencode, quote


class universalis_scrapper:
    def __init__(self):
        self.session = requests.Session()
        headers = {
            
        }
        cookies = {
            'mogboard_server': quote("红玉海"),
            'mogboard_language': 'chs',
            'mogboard_timezone': 'Asia/Shanghai',
            'mogboard_leftnav': 'off',
            'mogboard_homeworld': 'no',
            'includeGst': 'no'
        }
        self.session.headers.update(headers)
        self.session.cookies.update(cookies)

        self.server_list = [
            {"id":1173,"name":"宇宙和音"},
            {"id":1044,"name":"幻影群岛"},
            {"id":1042,"name":"拉诺西亚"},
            {"id":1175,"name":"晨曦王座"},
            {"id":1174,"name":"沃仙曦染"},
            {"id":1081,"name":"神意之地"},
            {"id":1167,"name":"红玉海"},
            {"id":1060,"name":"萌芽池"},
            {"id":1121,"name":"拂晓之间"},
            {"id":1113,"name":"旅人栈桥"},
            {"id":1176,"name":"梦羽宝境"},
            {"id":1170,"name":"潮风亭"},
            {"id":1076,"name":"白金幻象"},
            {"id":1172,"name":"白银乡"},
            {"id":1171,"name":"神拳痕"},
            {"id":1166,"name":"龙巢神殿"},
            {"id":1169,"name":"延夏"},
            {"id":1045,"name":"摩杜纳"},
            {"id":1178,"name":"柔风海湾"},
            {"id":1177,"name":"海猫茶屋"},
            {"id":1179,"name":"琥珀原"},
            {"id":1043,"name":"紫水栈桥"},
            {"id":1106,"name":"静语庄园"},
            {"id":1186,"name":"伊修加德"},
            {"id":1180,"name":"太阳海岸"},
            {"id":1064,"name":"月牙湾"},
            {"id":1192,"name":"水晶塔"},
            {"id":1201,"name":"红茶川"},
            {"id":1183,"name":"银泪湖"},
            {"id":1187,"name":"雪松原"},
            {"id":1068,"name":"黄金谷"}
        ] # 服务器列表
        self.server_name = "红玉海"
    
    # 切换当前查询服务器
    def switch_server(self, server_name):
        for server in self.server_list:
            if server_name == server['name']:
                self.session.cookies.update({'mogboard_server': quote(server_name)})
                self.server_name = server_name
                return True
        return False
        


    # 获取服务器各城市税率
    def get_tax_rate(self, world_name=""):
        if world_name == "":
            world_name = self.server_name
        url = 'https://universalis.app/api/tax-rates'
        params = {
            'world': world_name
        }
        res = self.session.get(url=url, params=urlencode(params))
        
        try:
            city_taxs = {}
            res_data = res.json()
            city_dict = {
                'Crystarium': '水晶都',
                'Gridania': '格里达尼亚',
                'Ishgard': '伊修加德',
                'Kugane': '黄金港',
                'Limsa Lominsa': '利姆萨罗敏萨',
                'Old Sharlayan': '萨雷安',
                'Tuliyollal': '图莱尤拉',
                "Ul'dah": '乌尔达哈'
            }
            
            for city_name_en, city_tax in res_data.items():
                city_name_cn = city_dict[city_name_en]
                city_taxs[city_name_cn] = city_tax

            return city_taxs
        except:
            traceback.print_exc()
            return False

    # 获取物品ID
    def get_item_id(self, item_name):
        url = 'https://cafemaker.wakingsands.com/search'
        params = {
            'string': item_name,
            'indexes': 'item',
            'language': 'chs',
            'filters': 'ItemSearchCategory.ID>=1',
            'columns': 'ID,Icon,Name,LevelItem,Rarity,ItemSearchCategory.Name,ItemSearchCategory.ID,ItemKind.Name',
            'limit': '100',
            'sort_field': 'LevelItem',
            'sort_order': 'desc'
        }
        res = self.session.get(url=url, params=urlencode(params))
        try:
            res_data = res.json()
            results = res_data['Results']
            if len(results) > 0:
                for result in results:
                    if item_name == result['Name']:
                        return result
                return results[0]
            else:
                return False
        except:
            traceback.print_exc()
            return False

    # 获取物品价格
    def get_item_price(self, item_id):
        url = f'https://universalis.app/_next/data/N8UrbBK-P_YmP8-dxZD9L/market/{item_id}.json'
        params = {
            'itemId': item_id
        }
        res = self.session.get(url=url, params=urlencode(params))
        
        try:
            res_data = res.json()
            markets = res_data['pageProps']['markets']
            market_formated = {}
            for market_id, market in markets.items():
                market_name = None
                for server in self.server_list:
                    if str(market_id) == str(server['id']):
                        market_name = server['name']
                if not market_name: continue
                # current_avg_price = market['currentAveragePrice'] # 最近均价
                recent_history = market['recentHistory']
                if len(recent_history) > 0:
                    last_purchase = recent_history[0]
                    last_purchase_price = last_purchase['pricePerUnit']
                    total_n, total_price = 0, 0
                    for item in recent_history:
                        total_n += item['quantity']
                        total_price += item['total']
                    current_avg_price = total_price / total_n
                else:
                    current_avg_price = None
                    last_purchase_price = None
                sale_velocity = market['regularSaleVelocity']
                if sale_velocity < 1:
                    sale_tag = '无人问津'
                elif sale_velocity < 10:
                    sale_tag = '小有名气'
                elif sale_velocity < 50:
                    sale_tag = '备受关注'
                else:
                    sale_tag = '明星商品'

                market_formated[market_name] = {'current_avg_price': current_avg_price, 'last_purchase_price': last_purchase_price, 'sale_tag': sale_tag}
            return market_formated
        
        except Exception as e:
            traceback.print_exc()
            return False



class cn_current_scrapper:
    def __init__(self):
        self.session = requests.Session()
        headers = {
            'content-type': 'application/json',
            'host': 'www.ff14pvp.top',
            'origin': 'https://www.ff14pvp.top',
            'referer': 'https://www.ff14pvp.top/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        }
        cookies = {
            'user': 'NTZhZmQyNDRmZmEwNDIyNWE3YmY4OWVkOGZhODQ3MTM=',
            'world': '6ZmG6KGM6bif'
        }
        self.session.headers.update(headers)
        self.session.cookies.update(cookies)
        self.SERVER_LIST = [
            '拉诺西亚',
            '幻影群岛',
            '神意之地',
            '萌芽池',
            '红玉海',
            '宇宙和音',
            '沃仙曦染',
            '晨曦王座'
        ]

    def get_item_id(self, item_full_name):
        url = 'https://www.ff14pvp.top/ffbusiness/itemNew/getOne'
        data = {
            'name': item_full_name
        }
        res = self.session.post(url=url, data=json.dumps(data))
        try:
            res_data = res.json()
            if len(res_data['rows']) > 0:
                return res_data['rows'][0]['id']
        except Exception as e:
            traceback.print_exc()
            return False

    def get_item_full_name(self, item_name):
        url = 'https://www.ff14pvp.top/ffbusiness/itemNew/suggestName'
        data = {
            'name': item_name, 
            'all': True
        }
        res = self.session.post(url=url, data=json.dumps(data))
        try:
            res_data = res.json()
            if len(res_data) > 0:
                return res_data[0]
        except Exception as e:
            traceback.print_exc()
            return False



    def get_item_price(self, item_full_name):
        url = 'https://www.ff14pvp.top/ffbusiness/saleHistory/realData'
        data = {
            "itemId":None,
            "itemName": item_full_name,
            "worldName": "陆行鸟",
            "buyerName": None,
            "timestamp": None,
            "onlyHq": 0,
            "itemTypes": [],
            "pageSize": 300,
            "pageNumber": 1
        }
        res = self.session.post(url=url, data=json.dumps(data))
        try:
            res_data = res.json()
            rows = res_data['rows']
            market_formated = {}
            for row in rows:
                if row['worldName'] not in market_formated:
                    market_formated[row['worldName']] = [row]
                else:
                    if len(market_formated[row['worldName']]) == 10: continue
                    market_formated[row['worldName']].append(row)
            
            for market_name, purchase_list in market_formated.items():
                if len(purchase_list) > 2:
                    last_purchase_price = purchase_list[0]['pricePerUnit']
                    
                    market_sum = 0
                    market_count = 0
                    market_gap = timedelta(seconds=0)
                    last_ts = None
                    for purchase in purchase_list:
                        market_sum += purchase['sum']
                        market_count += purchase['quantity']
                        ts = datetime.strptime(purchase['timestamp'], "%Y/%m/%d %H:%M:%S")
                        if not last_ts:
                            last_ts = ts 
                        else:
                            market_gap += ts - last_ts
                    current_avg_price = market_sum / market_count

                    market_avg_gap = market_gap / (len(purchase_list) - 1)
                    if market_avg_gap > timedelta(days=3):
                        sale_tag = '无人问津'
                    elif market_avg_gap > timedelta(days=1):
                        sale_tag = '小有名气'
                    elif market_avg_gap > timedelta(hours=3):
                        sale_tag = '备受关注'
                    else:
                        sale_tag = '明星商品'

                    market_formated[market_name] = {'current_avg_price': current_avg_price, 'last_purchase_price': last_purchase_price, 'sale_tag': sale_tag}

            return market_formated
        
        except Exception as e:
            traceback.print_exc()
            return False
        
    def get_item_trend(self, item_full_name, server_name):
        if server_name not in self.SERVER_LIST:
            return
        today = datetime.today()
        url = 'https://www.ff14pvp.top/ffbusiness/summary/query'
        data = {
            'itemId': self.get_item_id(item_full_name), 
            'startDate': (today - timedelta(days=7)).strftime('%Y%m%d'), 
            'endDate': today.strftime('%Y%m%d'), 
            'worldName': server_name
        }

        res = self.session.post(url=url, data=json.dumps(data))
        try:
            res_data = res.json()
            return res_data
        except Exception as e:
            traceback.print_exc()
            return False


if __name__ == "__main__": # 调试用
    # us = universalis_scrapper()
    # print(us.get_item_price(44053))
    ccs = cn_current_scrapper()
    res = ccs.get_item_trend('神眼魔晶石拾型', '红玉海')
    # print(get_bar_line_chart(res['dates'], res['values'][0]['value'], res['values'][1]['value'], '均价', '购买量'))