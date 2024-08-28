import time 
import requests 
from datetime import datetime 
import json 
from threading import Thread 

def loadLast(category):
    with open(f'{category}.json','r',encoding='utf-8') as f:
        return json.load(f)

def writeLast(data, category):
    with open(f'{category}.json','w',encoding='utf-8') as f:
        json.dump(data,f)

def loadProxies():
    with open('proxies.txt','r',encoding='utf-8') as f:
        return set([ i.strip() for i in f.readlines() ])


proxylist = loadProxies()
proxylistused = set()

with open('webhook.json','r',encoding='utf-8') as f:
    webhookurl = json.load(f)['webhook']

session = requests.Session()

def pushToMyDiscord(title,time,url):
    headers= {
        "Content-Type": "application/json"
    }
    payload = {
        "username": "Upbit Announcements",
        "embeds": [{
            "title": title,
            "description": "[ Upbit ]",
            "url": url,
            "color": 234234,
            "footer": {
                "text": time
            }
        }]
    }
    requests.post("https://discord.com/api/webhooks/1272560122438090776/YcH8v-Zsr8inS0zLdfqbMf8HZiT-YIxUQ2PZoNbUPXi3YdTEy0mu4mGwAtRbaIhfq_fU",headers=headers,json=payload)

def pushToDiscord(title,time,url):
    headers= {
        "Content-Type": "application/json"
    }
    payload = {
        "username": "Upbit Announcements",
        "embeds": [{
            "title": title,
            "description": "[ Upbit ]",
            "url": url,
            "color": 234234,
            "footer": {
                "text": time
            }
        }]
    }
    requests.post(webhookurl,headers=headers,json=payload)

latest = loadLast("latest")

#https://api-manager.upbit.com/api/v1/announcements/search?search=ta&page=1&per_page=1&category=all&os=web
#https://api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=1&category=all
def sendRequest(session,category,url):
    
    global proxylist , proxylistused , latest 

    if len(proxylist) == 0:
        proxylist = loadProxies()
        proxylistused = set()

    proxy = list(proxylist)[0]

    if proxy not in proxylistused:
        proxylistused.add(proxy)

    if proxy in proxylist:
        proxylist.remove(proxy)
    
    print(datetime.now(),url,proxy)

    #print(proxy)

    headers = {
        "Accept-language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Brave\";v=\"127\", \"Chromium\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "sec-gpc": "1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "authority": "api-manager.upbit.com",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip"
    }

    proxies = {
        'http': proxy,
        'https': proxy,
    }

    session.cache = None 
    session.proxies.update(proxies) 
    sent=datetime.now()
    res=session.get(url, headers=headers)
    recieved=datetime.now()
    
    sentwms = sent.strftime('%Y-%m-%d %H:%M:%S') + f'.{sent.strftime('%f')[:3] }'
    recievedwms = recieved.strftime('%Y-%m-%d %H:%M:%S') + f'.{recieved.strftime('%f')[:3] }'
    
    #print(f'Response : {res.status_code}\nDelay : {recieved-sent}\nFound : {recieved}')

    if res.status_code != 200:
        pushToDiscord('Status Code not 200',res.status_code , url)
        pushToMyDiscord('Status Code not 200',res.status_code , url)
        return 

    title = res.json()['data']['notices'][0]['title']
    id = res.json()['data']['notices'][0]['id']
    
    if title == latest['title'] and id == latest['id']:
        return 
    
    latest = {'title': title , 'id': id}
        
    writeLast(latest , category)

    pushToDiscord(res.json()['data']['notices'][0]['title'],sentwms+'\n'+recievedwms+'\n'+res.json()['data']['notices'][0]['listed_at'] , url)
    pushToMyDiscord(res.json()['data']['notices'][0]['title'],sentwms+'\n'+recievedwms+'\n'+res.json()['data']['notices'][0]['listed_at'] , url)


# Keep the script running
while True:
    try:
        Thread(target=sendRequest, args=(session,'latest','https://api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=1&category=all')).start()
        Thread(target=sendRequest, args=(session,'latest','https://api-manager.upbit.com/api/v1/announcements/search?search=ta&page=1&per_page=1&category=all&os=web')).start()
        Thread(target=sendRequest, args=(session,'latest','https://api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=1&category=all')).start()
        Thread(target=sendRequest, args=(session,'latest','https://api-manager.upbit.com/api/v1/announcements/search?search=ta&page=1&per_page=1&category=all&os=web')).start()
        Thread(target=sendRequest, args=(session,'latest','https://api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=1&category=all')).start()
        Thread(target=sendRequest, args=(session,'latest','https://api-manager.upbit.com/api/v1/announcements/search?search=ta&page=1&per_page=1&category=all&os=web')).start()
        time.sleep(0.5) 

    except:
        pushToDiscord('Bot Stopped!','Script Over!' , '')
        pushToMyDiscord('Bot Stopped!','Script Over!' , '')
        break 