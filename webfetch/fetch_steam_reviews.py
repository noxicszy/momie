


import requests, json
url = "http://store.steampowered.com/appreviews/475150?json=1"
data = {'filter': 'all',
					'language': 'zh-CN',
					'day_range': '10000',
					'start_offset': '20',
					'review_type': 'all',
					'purchase_type': 'all'}

header = {
	"Accept-Language" : "zh-CN,zh", 
}
r = requests.get(url, params=data,  headers=header)
print r.text.encode('utf-8')


