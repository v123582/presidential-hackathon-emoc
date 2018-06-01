# 救急救難一站通API文件

此API之目的為驗證系統之可行性(proof of concept)
* 不包含：Authentication & Authorization 之實作 (ex: auth token)
* 不包含：data integrity 之實作 (ex: timestamp-hash)

![](https://i.imgur.com/dOMEhqC.png)

# source code 

https://github.com/v123582/presidential-hackathon-emoc

# Base_url

base_url = ??

# 名詞介紹

* devices：這邊專指「紀錄電子救護之移動裝置」
* ePCRs：電子救護紀錄 (nElectronic Patient Care Reporting）
* hospitals：這邊專指「急救責任醫院」
* KAMERA：高屏區急診能量即時數據
* positions：裝置位置打卡
* reservations：送往醫院預佔

# KAMERA相關API

## 讀取KAMERA即時數據

```ruby=
# 讀取時間點{timestamp} 且 位置{latlng} 最近之10家醫院 KAMERA 數據
request method: GET
request url:    /KAMERA/?latlng={latlng}&timestamp={timestamp}
request body:   NULL

# latlng -
#    緯度,經度(latitude,longitude), Decimal Degree (DD)表示TWD97/WGS84
#    例內政部消防署位置為 24.983445,121.541582
#    可使用google map確認位置。https://www.google.com.tw/maps?q=24.983445,121.541582
# timestamp(optional) - (缺此參數則代表即時最新) 
#     ISO 8601表示 (YYYYMMDDThhmmssZ)
#     例201800502T220000Z 代表 2018年05月02日 22:00分
```

```ruby=
response header: 200 OK
response body:
{
	"result": [{
			"hospital_name": "高雄市立大同醫院",
			"hospital_id": "13",
			"hospital_latlng": "ddd",
			"updated_timestamp": "20140801T000004Z",
			"A01": 7,
			"A02": 0,
			"A03": 2,
			"A04": 1,
			"A05": 0,
			"A06": 2,
			"A07": 0,
			"A08": 1,
			"A09": 11,
			"A10": 0,
			"A11": 0,
			"A12": 9,
			"A13": 6,
			"A14": 0,
			"A15": 2,
			"A16": 40,
			"A17": 0,
			"C01": 0,
			"C02": 0,
			"C03": 0,
			"C04": 0,
			"C05": 0,
			"C06": 19,
			"B01": 0,
			"B02": 0,
			"B03": 5,
			"B04": 0,
			"B05": 0,
			"B06": 0,
			"Light": 1
		},
		{
			...
		}
	]
}
```

```ruby=
# ERROR CODE
#     缺少{latlng}
response header: 400 bad request
```
# ePCR相關API

## 新增ePCR

```ruby=
# 新增ePCR
request method: POST
request url:    /ePCR/
request body:
{
    "ePCR_id": "xxx",
    "device_id": "xxx",
    "gender": "男",
    "age_range": "16-64",
    "enroute_timestamp": "",
    "arrive_scene_timestamp": "",
    "leave_scene_timestamp": "",
    "arrive_hospital_timestamp": "",
    "leave_hospital_timestamp": "",
    "back_station_timestamp": "",
    "is_ALS": "YES",
    "special_need": [
        "AMI", "STROKE"
        ],
    "dispatch_addr": "xxx",
    "dispatch_latlng": "xxxx",
    "destination": ""
}

# {ePCR_id} {device_id} 是必填
# 
# gender - 性別
# age_range -  <1, 1-4, 5-17, 18-64, >65
# (年齡分類參考 WHO 2016 對於災難(EMERGENCY MEDICAL TEAMS)定義的MINIMUM DATA SET)
# https://extranet.who.int/emt/sites/default/files/Minimum%20Data%20Set.pdf
# 
# enroute_timestamp - 出勤時間
# arrive_scene_timestamp - 到達現場時間
# leave_scene_timestamp - 離開現場時間
# arrive_hospital_timestamp - 送達醫院時間
# leave_hospital_timestamp - 離開醫院時間
# back_station_timestamp - 返隊待命時間
#
# # ISO 8601表示 (YYYYMMDDThhmmssZ)
# 例201800502T220000Z 代表 2018年05月02日 22:00
# 
# is_ALS - 現場是否為危急個案
# special_need - 特殊狀況(時間急症) OHCA, AMI, STROKE, MAJOR_TRAMUA (未來可以加入更多 例如燒燙傷...)
# 
# dispatch_addr - 派遣地址
# dispatch_latlng - 派遣地址座標
# destination - 填醫院代碼 aka hospital_id
```

```ruby=
response header: 200 OK
response body:
{
	"result": "success"
}
```

```ruby=
# ERROR CODE
#     缺少{ePCR_id} or {device_id}
response header: 400 bad request
#     {ePCR_id}之紀錄已存在
response header: 403 forbidden
```

## 讀取全部ePCR (new)
```ruby=
# 新增ePCR
request method: GET
request url:    /ePCR/
request body:   NULL
```
```ruby=
response header: 200 OK
response body:
{
	"result": [{
			"ePCR_id": "123xxxx",
			"gender": "男",
			"age_range": "成年",
			"enroute_timestamp": "",
			"arrive_scene_timestamp": "",
			"leave_scene_timestamp": "",
			"arrive_hospital_timestamp": "",
			"leave_hospital_timestamp": "",
			"back_station_timestamp": "",
			"is_ALS": "YES",
			"special_need": [
				"AMI", "STROKE"
			],
			"dispatch_addr": "xxx",
			"dispatch_latlng": "xxxx",
			"destination": ""
		},
		{
			"ePCR_id": "456xxx",
			"gender": "男",
			"age_range": "成年",
			"enroute_timestamp": "",
			"arrive_scene_timestamp": "",
			"leave_scene_timestamp": "",
			"arrive_hospital_timestamp": "",
			"leave_hospital_timestamp": "",
			"back_station_timestamp": "",
			"is_ALS": "YES",
			"special_need": [
				"AMI", "STROKE"
			],
			"dispatch_addr": "xxx",
			"dispatch_latlng": "xxxx",
			"destination": ""
		}
	]
}
```


## 讀取單一筆ePCR


```ruby=
# 新增ePCR
request method: GET
request url:    /ePCR/{ePCR_id}
request body:   NULL
```

```ruby=
response header: 200 OK
response body:
{
	"result": {
		"ePCR_id": "xxx",
		"gender": "男",
		"age_range": "成年",
		"enroute_timestamp": "",
		"arrive_scene_timestamp": "",
		"leave_scene_timestamp": "",
		"arrive_hospital_timestamp": "",
		"leave_hospital_timestamp": "",
		"back_station_timestamp": "",
		"is_ALS": "YES",
		"special_need": [
			"AMI", "STROKE"
		],
        "dispatch_addr": "xxx",
        "dispatch_latlng": "xxxx",
        "destination": ""
	}
}
```


## 更新ePCR
```ruby=
# 更新ePCR
request method: PUT
request url:    /ePCR/{ePCR_id}
request body:   
{
	"gender": "男",
	"age_range": "成年",
	"enroute_timestamp": "",
	"arrive_scene_timestamp": "",
	"leave_scene_timestamp": "",
	"arrive_hospital_timestamp": "",
	"leave_hospital_timestamp": "",
	"back_station_timestamp": "",
	"is_ALS": "YES",
	"special_need": [
		"AMI", "STROKE"
	],
	"dispatch_addr": "xxx",
	"dispatch_latlng": "xxxx",
	"destination": ""
}
```
```ruby=
response header: 200 OK
response body:
{
	"result": "success"
}
```

```ruby=
# ERROR CODE
#     ePCR_id不存在
response header: 404 not found
```

## 刪除ePCR
```ruby=
# 
request method: DELETE
request url:    /ePCR/{ePCR_id}
request body:   NULL
```

```ruby=
response header: 200 OK
response body:
{
	"result": "success"
}
```

```ruby=
# ERROR CODE
#     ePCR_id不存在
response header: 404 not found
```

# 位置打卡相關API

## 位置打卡

```ruby=
# 位置打卡
request method: POST
request url:    /positions/
request body:   
{
    "device_id": "xxx",
    "ePCR_id": "xxx",
    "timestamp": "xxxxx",
    "latlng": "xxx,xxx"
}

# device_id(必填) - 裝置的ID
# ePCR_id(必填) - 案件ID
# timestamp(必填) - 打卡時間
#     ISO 8601表示 (YYYYMMDDThhmmssZ)
#     例201800502T220000Z 代表 2018年05月02日 22:00
# latlng(必填) - 打卡位置
#    緯度,經度(latitude,longitude), Decimal Degree (DD)表示TWD97/WGS84
#    例內政部消防署位置為 24.983445,121.541582
#    可使用google map確認位置。https://www.google.com.tw/maps?q=24.983445,121.541582
```
```ruby=
response header: 200 OK
response body:
{
	"result": "success"
}
```

```ruby=
# ERROR CODE
#     缺少{device_id} or {ePCR_id} or {timestamp} or {latlng}
response header: 400 bad request
```

## 讀取位置

```ruby=
# 查詢「裝置」
request method: GET
request url:    /positions/
request body:   NULL
```
```ruby=
# 查詢「裝置」
request method: GET
request url:    /positions/?device_id={device_id}
request body:   NULL
```
```ruby=
# 查詢「裝置」
request method: GET
request url:    /positions/?ePCR_id={ePCR_id}
request body:   NULL
```
```ruby=
# 查詢「裝置」
request method: GET
request url:    /positions/?device_id={device_id}&ePCR_id={ePCR_id}
request body:   NULL
```

```ruby=
response header: 200 OK
response body:
{
	"result": [{
			"device_id": "xxx",
			"ePCR_id": "xxx",
			"timestamp": "XX91",
			"latlng": "xxx,xxx"
		},
		{
			"device_id": "xxx",
			"ePCR_id": "xxx",
			"timestamp": "XX91",
			"latlng": "xxx,xxx"
		}
	],
	"status": {
		"total_count": 250,
		"prev_link": "http://xxxx",
		"next_link": "http://xxxx"
	}
}
```
```ruby=
# ERROR CODE
#     ePCR_id不存在
response header: 404 not found
```

# 送往醫院預佔相關API

## 「預約」送往醫院預佔

```ruby=
# 「預約」送往醫院預佔
request method: POST
request url:    /reservations/
request body:   
{
	"device_id": "xxx",
	"ePCR_id": "xxx",
	"gender": "男",
	"age_range": "成年",
	"is_ALS": "YES",
	"special_need": [
		"AMI", "STROKE"
	],
	"destination": ""
}

# 會加入自動欄位 is_active (受到ePCR PUT/DELETE 會改變) 
```
```ruby=
# 查詢「預約」送往醫院預佔 (只看某hospital) 且 is_active
request method: GET
request url:    /reservations/?destination={hospital}&is_active={is_active}
request body:   NULL
```

```ruby=
# ERROR CODE
#     ePCR_id不存在
response header: 404 not found
```

# 裝置相關API

## 查詢裝置(Private API)
```ruby=
# 查詢「裝置」
request method: GET
request url:    /devices/
request body:   NULL
```
```ruby=
response header: 200 OK
response body:
{
	"result": [{
			"device_name": "xxx",
			"device_id": "xxx",
			"EMSUnit": "XX91"
		},
		{
			"device_name": "xxx",
			"device_id": "xxx",
			"EMSUnit": "XX91"
		}
	],
	"status": {
		"total_count": 60,
		"prev_link": "http://xxxx",
		"next_link": "http://xxxx"
	}
}
```

## 新增裝置(Private API)

```ruby=
# 新增「裝置」
request method: POST
request url:    /devices/
request body:   
{
    "device_name": "xxx",
    "device_id": "xxx",
    "EMSUnit": "XX91",
}

# P.S. 通常標準應是不提供device_id 新增成功後系統給予device_id，這裡簡化之
```

```ruby=
response header: 200 OK
response body:
{
	"result": {
		"device_id": "xxx"
	}
}
```
```ruby=
# ERROR CODE
#     device_id之裝置已存在
response header: 403 forbidden
```

device_name = device_id = EMSUnit

['五甲92' '大昌91' '十全91' '鳳祥92' '鼎金91' '鳳祥91' '大昌92' '鳳山91' '大寮92' '大寮91'
 '前金91' '中華91' '十全92' '鳥松91' '右昌91' '楠梓93' '楠梓91' '鼎金92' '成功91' '中華92'
 '中庄92' '中庄91' '五甲91' '新莊91' '左營92' '高桂91' '左營91' '大林91' '林園91' '鳳山92'
 '仁武91' '橋頭91' '燕巢91' '永安91' '大社92' '仁武92' '鳥松92' '湖內91' '右昌93' '路竹91'
 '湖內92' '永安92' '大樹92' '梓官92' '岡山93' '前鎮91' '新興91' '新興92']


## 移除裝置(Private API)
```ruby=
# 移除「裝置」
request method: DELETE
request url:    /devices/{device_id}
request body:   NULL
```
```ruby=
response header: 200 OK
response body:
{
	"result": "success"
}
```
```ruby=
# ERROR CODE
#     device_id不存在
response header: 404 not found
```

# 醫院相關API

## 查詢醫院
```ruby=
# 查詢「醫院」
request method: GET
request url:    /hospitals/
request body:   NULL
```
```ruby=
response header: 200 OK
response body:
{
	"result": [{
			"hospital_name": "高雄市立大同醫院",
			"hospital_id": "102070020",
			"position": "22.627091,120.297333",
			"level": "中度"
		},
		{
			"hospital_name": "高雄市立大同醫院",
			"hospital_id": "102070020",
			"position": "22.627091,120.297333",
			"level": "中度"
		}
	],
	"status": {
		"total_count": 25,
		"prev_link": "http://xxxx",
		"next_link": "http://xxxx"
	}
}
```
```ruby=
# 查詢個別「醫院」
request method: GET
request url:    /hospitals/{hospital_id}
request body:   NULL
```
```ruby=
response header: 200 OK
response body:
{
	"result": {
		"hospital_name": "高雄市立大同醫院",
		"hospital_id": "102070020",
		"position": "22.627091,120.297333",
		"level": "中度"
	}
}
```
```ruby=
# ERROR CODE
#     device_id不存在
response header: 404 not found
```


## 新增醫院(Private API)

```ruby=
# 新增「醫院」
request method: POST
request url:    /hospitals/
request body:   
{
    "hospital_name": "高雄市立大同醫院",
    "hospital_id": "102070020",
    "position": "22.627091,120.297333",
    "level": "中度"    
}

```

```ruby=
response header: 200 OK
response body:
{
	"result": {
		"hospital_id": "102070020"
	}
}
```
```ruby=
# ERROR CODE
#     hospital_id之醫院已存在
response header: 403 forbidden
```

hospital_name = hospital_id 
['國軍高雄總' '高醫' '高雄榮總' '阮綜合' '高雄長庚' '義大醫院' '大同醫院' '市立民生' '國軍左營' '杏和'
 '聖功醫院' '大東' '小港醫院']

## 移除醫院(Private API)
```ruby=
# 移除「醫院」
request method: DELETE
request url:    /hospitals/{hospital_id}
request body:   NULL
```
```ruby=
response header: 200 OK
response body:
{
	"result": "success"
}
```
```ruby=
# ERROR CODE
#     hospital_id不存在
response header: 404 not found
```


# API使用應用範例

## 詹大千老師的輔助送醫決策系統(Decision Support System)

* 利用「**派遣位址地理座標**」+ **病人狀況** 「性別、年紀區別(<12,12~65,>65)、特殊需求(OHCA、AMI、STROKE、MAJOR_TRAUMA)」 ＋ 附近最近10家醫院「地理座標 及 **當下急診量能資料Kamera**」運算當下最佳送醫地點
* (optional) 利用其他119平板當下的案件之「送往醫院預佔」資料可提供未來即將到院前的資訊 或許可以改進「最佳送醫地點模型」？

* input：
    * ePCR_id
    * gender
    * age_range
    * is_ALS
    * special_need
    * dispatch_latlng
    * now_timestamp (for 這次demo simulate使用 不然直接當下時間即可)
* 使用的API
```ruby=
# 得到根據時間戳記當下且距離最近的十家醫院Kamera資料
GET /KAMERA/?latlng={dispatch_latlng}&timestamp={now_timestamp}
```
```ruby=
response header: 200 OK
response body:
{
	"result": [{
			"hospital_name": "高雄市立大同醫院",
			"hospital_id": "13",
			"hospital_latlng": "ddd",
			"updated_timestamp": "20140801T000004Z",
			"A01": 7,
			"A02": 0,
			"A03": 2,
			"A04": 1,
			"A05": 0,
			"A06": 2,
			"A07": 0,
			"A08": 1,
			"A09": 11,
			"A10": 0,
			"A11": 0,
			"A12": 9,
			"A13": 6,
			"A14": 0,
			"A15": 2,
			"A16": 40,
			"A17": 0,
			"C01": 0,
			"C02": 0,
			"C03": 0,
			"C04": 0,
			"C05": 0,
			"C06": 19,
			"B01": 0,
			"B02": 0,
			"B03": 5,
			"B04": 0,
			"B05": 0,
			"B06": 0,
			"Light": 1
		},
		{
			...
		}
	]
}
```

## 醫院/119 預送醫 即時動態(optional)

![Imgur](https://i.imgur.com/JidZMnf.png)

## 地理資訊事後回顧

* 出勤中、送醫中每隔15秒紀錄一次上傳 (15萬件/年 * 20分鐘 * 4 * 10byte~) 約莫 3~5 GB 資料

## 模擬影片

[![Demo](http://img.youtube.com/vi/FRKr6vZXpWk/0.jpg)](https://www.youtube.com/watch?v=FRKr6vZXpWk)


## License

MIT License

Copyright (c) 2018 WeiYuan, Deniel, Ziv Chang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
