
from flask import Flask, jsonify, Blueprint,request
import pandas as pd
import json
from sqlalchemy import create_engine
# from flask_cors import CORS
import pymongo
import simplejson
import urllib
import config


app = Flask(__name__)
# CORS(app)


uri = 'mongodb+srv://' + config.credentials['username'] + ':' + config.credentials['password'] + '@' + config.credentials['host'] 
client = pymongo.MongoClient(uri)
db = client[config.credentials['database']]





# given某時間點、位置，回傳"某時間點"之前，離"位置"最近之十家醫院的分別的最新Kamera資料
@app.route('/KAMERA/')
def get_kamera():

	ambulance_latlng = request.args.get('latlng', default = 1, type = str)
	timestamp = request.args.get('timestamp', default = 1, type = str)
	# url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false"


	# calculate traveling time with google api 
	def get_10_hospital_nearby_v1():
		query = {"updated_timestamp":{'$lte':timestamp }}
		projection = {"hospital_name": 1, "hospital_latlng":1}
		df = pd.DataFrame(list(db["kamera"].find(query, projection)))
		df = df.drop_duplicates(["hospital_name"])
		df["traveling_time"] = df["hospital_latlng"].apply(lambda x: simplejson.load(urllib.request.urlopen(url.format(ambulance_latlng,x)))['rows'][0]['elements'][0]['duration']['value'])
		hospital_nearby = df.sort_values("traveling_time" , ascending=True )[:10]
		return list(hospital_nearby["hospital_name"])


	# calculate distance using formula

	def calculate_distance(destination):
		a = (float(destination.split(",")[0])-float(ambulance_latlng.split(",")[0]))**2
		b = (float(destination.split(",")[1])-float(ambulance_latlng.split(",")[1]))**2
		return (a+b)

	def get_10_hospital_nearby_v2():
		query = {"updated_timestamp":{'$lte':timestamp }}
		projection = {"hospital_name": 1, "hospital_latlng":1}
		df = pd.DataFrame(list(db["kamera"].find(query, projection)))
		df = df.drop_duplicates(["hospital_name"])
		df["distance"] = df["hospital_latlng"].apply(calculate_distance)
		hospital_nearby = df.sort_values("distance" , ascending=True )[:10]
		return list(hospital_nearby["hospital_name"])





	if not ambulance_latlng:
		return(bad_request_kamera())

	else:
		g = []
		for i in get_10_hospital_nearby_v2():
			query = {
				"updated_timestamp":{'$lte':timestamp }, 
				"hospital_name": {'$in': [i]}
			}
			projection = {"_id": 0}
			temp = pd.DataFrame(list(db["kamera"].find(query, projection).sort("updated_timestamp",-1).limit(1)))
			g.append(temp)
		
		final = pd.concat(g)

		response = jsonify(dict(result=final.to_json( orient="records" )))
		response.status_code = 200


		return response






@app.route('/ePCR/', methods=["POST"])
def post_epcr():
	try:
		test_json = request.get_json()
	except Exception as e:
		raise e


	if not "ePCR_id"  or not "device_id" in  list(test_json.keys()):
		return bad_request_epcr()

	#   {ePCR_id} exists
	elif  list(db["epcr"].find({"ePCR_id":test_json["ePCR_id"]})):
		return forbidden_epcr()

	else:
		db["epcr"].insert_one(test_json)
		message = {
			'result': "success",
		}
		resp = jsonify(message)
		resp.status_code = 200
		return resp






@app.route('/ePCR/<epcr_id>', methods=["GET"])
def get_epcr(epcr_id):


	query = {"ePCR_id":epcr_id}
	projection = {'device_id': 0 , "_id":0}
	result_ = list(db["epcr"].find(query, projection))

	response = jsonify(dict(result=result_))
	response.status_code = 200



	return response




@app.route('/ePCR/<epcr_id>', methods=["PUT"])
def put_epcr(epcr_id):

	try:
		test_json = request.get_json()
	except Exception as e:
		raise e
	
	# ePCR_id does not exist
	if not list(db["epcr"].find({"ePCR_id":epcr_id})):
		return not_found_epcr()

	else:
		db["epcr"].update_one({'ePCR_id':epcr_id }, {"$set":test_json},upsert=False)
		message = {
			'result': "success",
		}
		resp = jsonify(message)
		resp.status_code = 200
		return resp




@app.route('/ePCR/<epcr_id>', methods=["DELETE"])
def delete_epcr(epcr_id):

	# ePCR_id does not exist
	if not list(db["epcr"].find({"ePCR_id":epcr_id})):
		return not_found_epcr()
	else:
		db["epcr"].remove({"ePCR_id":epcr_id})
		message = {
			'result': "success",
		}
		resp = jsonify(message)
		resp.status_code = 200
		return resp





# 位置打卡相關 API: 位置打卡
@app.route('/positions/', methods=["POST"])
def post_positions():
	data = request.get_json()

	if {'device_id', 'timestamp', 'latlng', 'ePCR_id'} - set(data.keys()):
		return bad_request(message='Bad Request for positions')

	db["positions"].insert_one(data)

	message = {
	   'result': "success",
	}
	resp = jsonify(message)
	resp.status_code = 200
	return resp

# 位置打卡相關 API: 讀取位置
@app.route('/positions/', methods=["GET"])
def get_positions():
	data = request.values.to_dict()
	projection = {"_id":0}
	result_ = list(db["positions"].find(data, projection))
	status = {
		'total_count': len(result_)
	}
	resp = jsonify(dict(result=result_, status=status))
	resp.status_code = 200
	return resp


# 送往醫院預佔相關 API: 預約
@app.route('/reservations/', methods=["POST"])
def post_reservations():
	data = request.get_json()

	if {'device_id', 'ePCR_id', 'destination'} - set(data.keys()):
		return bad_request(message='Bad Request for reservations')

	r = {
		"device_id": data.get('device_id', None),
		"ePCR_id": data.get('ePCR_id', None),
		"gender": data.get('gender', None),
		"age_range":  data.get('age_range', None),
		"is_ALS":  data.get('is_ALS', None),
		"special_need":  data.get('special_need', []),
		"destination":  data.get('destination', None),
		"is_active": True,
	}

	db["reservations"].insert_one(r)

	message = {
	   'result': "success",
	}
	resp = jsonify(message)
	resp.status_code = 200
	return resp

# 送往醫院預佔相關 API: 查詢
@app.route('/reservations/', methods=["GET"])
def get_reservations():
	arrived_epcrs = [ epcr['ePCR_id'] for epcr in db["epcr"].find( { 'arrive_hospital_timestamp': { '$nin': ['', None] } } ) ]
	
	data = request.values.to_dict()
	projection = {"_id":0}
	r = {}

	if 'destination' in data:
		r['destination'] = data['destination']

	if 'is_active' in data and data['is_active'] in ['1', 'true', 'True']:
		r['ePCR_id'] = { '$nin': arrived_epcrs }

	result_ = list(db["reservations"].find(r, projection))


	status = {
		'total_count': len(result_)
	}
	resp = jsonify(dict(result=result_, status=status))
	resp.status_code = 200
	return resp


# 裝置相關 API: 查詢
@app.route('/devices/', methods=["GET"])
def get_devices():
	data = request.values.to_dict()
	projection = {"_id":0}
	result_ = list(db["devices"].find(data, projection))
	status = {
		'total_count': len(result_)
	}
	resp = jsonify(dict(result=result_, status=status))
	resp.status_code = 200
	return resp

# 裝置相關 API: 新增
@app.route('/devices/', methods=["POST"])
def post_devices():
	data = request.get_json()
	if {'device_id', 'device_name', 'EMSUnit'} - set(data.keys()):
		return bad_request(message='Bad Request for devices')

	db["devices"].insert_one(data)

	message = {
	   'result': "success",
	   'device_id': data['device_id'],
	}
	resp = jsonify(message)
	resp.status_code = 200
	return resp

# 裝置相關 API: 移除
@app.route('/devices/<device_id>', methods=["DELETE"])
def delete_devices(device_id):

	db["devices"].remove({'device_id': device_id})

	message = {
	   'result': "success",
	}
	resp = jsonify(message)
	resp.status_code = 200
	return resp

@app.errorhandler(400)
def bad_request_kamera(error=None):
	message = {
			'status': 400,
			'message': 'Bad Request ! Please specify latlng'  
	}
	resp = jsonify(message)
	resp.status_code = 400

	return resp

@app.errorhandler(400)
def bad_request_epcr(error=None):
	message = {
			'status': 400,
			'message': 'Bad Request ! Please specify ePCR_id and device_id'  
	}
	resp = jsonify(message)
	resp.status_code = 400

	return resp

@app.errorhandler(400)
def bad_request(error=None, message=""):
	resp = jsonify(message)
	resp.status_code = 400
	return resp


@app.errorhandler(403)
def forbidden_epcr(error=None):
	message = {
			'status': 403,
			'message': 'forbidden ! ePCR_id already exists'  
	}
	resp = jsonify(message)
	resp.status_code = 403

	return resp


@app.errorhandler(404)
def not_found_epcr(error=None):
	message = {
			'status': 404,
			'message': '404 not found ! ePCR_id does not exist'  
	}
	resp = jsonify(message)
	resp.status_code = 404

	return resp






if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)






