import requests 
import time 
from datetime import datetime 
from threading import Thread
import json 

def loadLast():
    with open('last.json','r',encoding='utf-8') as f:
        return json.load(f)

def writeLast(data):
    with open('last.json','w',encoding='utf-8') as f:
        json.dump(data,f)

def loadProxies():
    with open('proxies.txt','r',encoding='utf-8') as f:
        return [ i.strip() for i in f.readlines() ]


proxylist = loadProxies()

with open('webhook.json','r',encoding='utf-8') as f:
    webhookurl = json.load(f)['webhook']

last = loadLast()
session = requests.Session()

def pushToDiscord(title,time):
    headers= {
        "Content-Type": "application/json"
    }
    payload = {
        "username": "Upbit Announcements",
        "embeds": [{
            "title": title,
            "color": 13709,
            "footer": {
                "text": time
            }
        }]
    }
    requests.post(webhookurl,headers=headers,json=payload)

def sendRequest(session,proxy):
    global last 

    headers = {
        'Cache-Control': 'no-cache',
        'Accept-Encoding': 'gzip'
    }
    proxies = {
        'http': proxy,
        'https': proxy,
    }
    session.proxies.update(proxies) 
    sent=datetime.now()
    res=session.get(f'https://api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=1&category=all&timestamp={float(sent.timestamp())}', headers=headers)
    recieved=datetime.now()
    
    sentwms = sent.strftime('%Y-%m-%d %H:%M:%S') + f'.{sent.strftime('%f')[:3] }'
    recievedwms = recieved.strftime('%Y-%m-%d %H:%M:%S') + f'.{recieved.strftime('%f')[:3] }'
    
    print(f'Response : {res.status_code}\nDelay : {recieved-sent}\nFound : {recieved}')

    if res.status_code != 200:
        return 
    
    title = res.json()['data']['notices'][0]['title']
    id = res.json()['data']['notices'][0]['id']

    if title == last['title'] and id == last['id']:
        return 
    
    last = {
        'title': title,
        'id': id
    }

    pushToDiscord(title,sentwms+'\n'+recievedwms)

    writeLast(last)

def testip(session,proxy):
    headers = {
        'Accept-Encoding': 'gzip'
    }
    proxies = {
        'http': proxy,
        'https': proxy[:4]+'s'+proxy[4:],
    }
    session.proxies.update(proxies)
    sent=datetime.now()
    res=session.get('https://api.ipify.org/?format=json', headers=headers)
    recieved=datetime.now()
    print(res.json())
    print(f'Response : {res.status_code}\nDelay : {recieved-sent}\nFound : {recieved}')


while True:
    for _,proxy in enumerate(proxylist):
        print('starting')
        a=datetime.now()
        for i in range(10):
            t=Thread(target=sendRequest, args=(session,proxy))
            t.start()
            time.sleep(0.1)
            print(f'proxy {_} fired run {i}')
        print(f'Going to Next Proxy\nTime Taken {datetime.now()-a}: ')