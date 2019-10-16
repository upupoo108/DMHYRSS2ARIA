# 订阅自动化测试
from xml.dom import minidom
import json, os, re, requests
downloadFolder = "./下载/"
jsonFolder = "./json/"
token = "llkll"

def displayList(*keyword, url="https://share.dmhy.org/topics/rss/rss.xml"):
	rssurl = url + "?keyword="
	for i in keyword:
		rssurl = rssurl + "+" + i
	rss = anaylseRSS(rssurl)
	for in
		print(i+1, "  ", itemTitle)
	pass

def anaylseRSS(url):
	document = getRSS(url)
	items = document.getElementsByTagName("item")
	itemTitles, itemURLs, itemUIDs = [], [], []
	for i in range(0,len(items)):
		itemTitle = items[i].getElementsByTagName("title")[0].childNodes[0].data
		itemTitles.append(itemTitle)
		itemURL = items[i].getElementsByTagName("enclosure")[0].getAttribute('url')
		itemURLs.append(itemURL)
		itemUID = re.compile("view/[0-9]{5,6}_").findall(items[i].getElementsByTagName("link")[0].childNodes[0].data)[0].replace("view/","").replace("_","")
		itemUIDs.append(int(itemUID))
	return {"title":itemTitles, "magnet":itemURLs, "uid":itemUIDs}

def downloadSubscribeBangumi():
	if os.path.exists(jsonFolder):
		from xml.dom import minidom
		for i in os.listdir(jsonFolder):
			# 拉取本地json
			localInfo = readJSON(jsonFolder+i)
			print(localInfo["uid"])
			# 拉取剧集rss
			remoteInfo = anaylseRSS(localInfo["rss"])
			print(remoteInfo["uid"])
			for num in range(0, len(remoteInfo["uid"])):
				if remoteInfo["uid"][num] not in localInfo["uid"]: #找到没下载的uid
					newJSON = localInfo
					print(remoteInfo["uid"][num])
					if upload2aira(remoteInfo["magnet"][num], filePath=downloadFolder+localInfo["title"]) == 200:
						newJSON["uid"].append(remoteInfo["uid"][num])
						newJSON["magnet"].append(remoteInfo["magnet"][num])
			#如果有更新就写入json
			if "newJSON" in locals().keys():
				if writeJSON(jsonFolder+i, newJSON) == 200 :
					print("已写入数据库")
				else:
					print("[严重错误警告] 数据写入数据库失败！")
			else:
				print("无更新")
	else:
		print("[严重错误] 订阅条目数据库丢失")

def readJSON(path, key="", value=""):
	with open(path,'r') as jsonFile:
		jsonDict = json.load(jsonFile)
		return jsonDict

def writeJSON(path, newJSON):
	with open(path,"w") as jsonFile:
		json.dump(newJSON, jsonFile)
		return 200

def getRSS(url):
	response = requests.get(url)
	if response.status_code != 500:
		with open("./rss.xml","wb") as f:
			for chunk in response.iter_content(128):
				f.write(chunk)
		with open('./rss.xml','r',encoding='utf8') as RSSFile:
			document = minidom.parse(RSSFile).documentElement
			return document

def upload2aira(fileURL,filePath=downloadFolder,token=token,aria2RemoteURL="localhost",port="6800"):
	if filePath != "":
		filePath = {"dir":filePath}
	else:
		filePath = {}
	token = "token:" + token
	requestHeaders = {
				"Accept":"application/json, text/plain, */*",
				"Content-Type":"application/json;charset=UTF-8"
			}
	requestPayload = {
				"jsonrpc":"2.0",
				"method":"aria2.addUri",
				"id":"QXJpYU5nXzE1NjYzNjc2NTZfMC4xMDk3NDc1ODUzNzE4MzEyNw==",
				"params":
					[token,[fileURL],filePath]
			}
	# try:
	response = requests.post(url="http://"+aria2RemoteURL+":"+port+"/jsonrpc", headers=requestHeaders, data=json.dumps(requestPayload), timeout=5)
	# except requests.exceptions.ConnectionError as e:
	# 	print("[投送失败] 运载目标丢失")
	# else:
	print(response.json())
	if "[200]" in str(response):
		print("[投送成功] 行动编号: " + response.json()['result'])
		return 200
	elif "error" in response.json():
		message = response.json()['error']['message']
		if message == "Unauthorized":
			warning = "[投送失败] 行动暗号错误"
		elif message == "No URI to download.":
			warning = "[投送失败] 运载目的地错误"
		print(warning)

if __name__ == '__main__':
	downloadSubscribeBangumi()
