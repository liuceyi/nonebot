import requests

MAXKB_API_URL = "你的知识库地址"
MAXKB_API_KEY = "你的知识库APIKEY"
MAXKB_API_APPID = "你的知识库APPID"

class chat_model:
    def __init__(self):
        self.session = requests.Session()
        headers = {
            'AUTHORIZATION': MAXKB_API_KEY,
            'accept': 'application/json'
        }
        self.session.headers.update(headers)
        self.CHAT_ID = None

    def get_chat_id(self):
        url = f'{MAXKB_API_URL}/{MAXKB_API_APPID}/chat/open'
        res = self.session.get(url=url)
        res_data = res.json()
        if res_data['code'] == 200:
            self.CHAT_ID = res_data['data'] 
            return True
        return False

    def send(self, chat_str):
        if not self.CHAT_ID:
            is_success = self.get_chat_id()
            if not is_success: return False

        url = f'{MAXKB_API_URL}/chat_message/{self.CHAT_ID}'
        data = {
            "message": chat_str,
            "re_chat": True,
            "stream": False
        }
        res = self.session.post(url=url, data=data)

        res_data = res.json()
        print(res_data)
        if res_data['code'] == 200:
            return res_data['data']['content']
        if res_data['code'] == 500:
            return '你问得好急，让我喝口水啦'
        return False
    