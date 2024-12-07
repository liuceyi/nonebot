import plotly.graph_objects as go
from plotly.io import to_image
from datetime import datetime
import plotly.io as pio
import plotly.express as px
import requests
import io

import matplotlib
matplotlib.rcParams['font.family'] = '宋体'


class visualizer:
    def __init__(self):
        self.FPATH_TEMP = 'export/temp'

    def get_bar_chart(self, data, x='', y='', name=None, save=True, fname=None):
        # 创建一个简单的条形图表
        fig = px.bar(
            data, # 数据集
            x=x, # x轴
            y=y, # y轴
            color = y,
            text = y
        )
        

        if save:
            # 导出图表为PNG图片
            image_data = to_image(fig, format='png')
            with open(f'{self.FPATH_TEMP}.png', 'wb') as f:
                f.write(image_data)
            with open(f'{self.FPATH_TEMP}.png', 'rb') as f:
                return self.upload(f)
        else:
            fig.show()


    def get_bar_line_chart(self, x, y1, y2, name1="", name2="", title='', save=True, fname=""):
        trace1 = go.Bar(
            x=x,
            y=y1,
            name=name1,
            marker=dict(
                colorscale='Purples', 
                color=y1,
                cmin = 0,
                cmax = max(y1),
                opacity=0.7)
        )
        trace2 = go.Scatter(
            x=x,
            y=y2,
            name=name2,
            xaxis='x', 
            yaxis='y2', #标明设置一个不同于trace1的一个坐标轴
            line = dict(color='gold', width=3),
            line_shape='spline'
        )
        
        data = [trace1, trace2]
        layout = go.Layout(
            yaxis2=dict(title=name2, anchor='x', overlaying='y', side='right')#设置坐标轴的格式，一般次坐标轴在右侧
        )
        
        fig = go.Figure(data=data, layout=layout)
        
        fig.update_layout(
            title=title,
            yaxis_title=name1,
            template = "plotly_dark",
            showlegend=True,
            xaxis_tickformat='%Y-%m-%d',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            # margin=dict(t=0,l=0,b=0,r=0),
            bargap=0.15
        )
        if save:
            # 导出图表为PNG图片
            image_data = to_image(fig, format='png')
            with open(f'{self.FPATH_TEMP}.png', 'wb') as f:
                f.write(image_data)
            with open(f'{self.FPATH_TEMP}.png', 'rb') as f:
                return self.upload(f)
        #     # 将图片数据写入文件
        #     if not fname: fname = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
        #     with open(f'{fname}.png', 'wb') as f:
        #         f.write(image_data)
                
        #     return f'{fname}.png'
        # else:
        #     fig.show()

    def upload(self, img_file):
        url = '你的图床地址'
        
        files = {'file': img_file}
        # data = {'strategy_id': 2}
        res = requests.post(url=url, files=files)
        res_data = res.json()
        if res_data['status'] == True:
            return res_data['data']['links']['url']
        