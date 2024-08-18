import requests 
import time 
from datetime import datetime 
import multiprocessing
import json 
from functools import partial
from threading import Thread


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

session = requests.Session()

def pushToDiscord(title,time):
    headers= {
        "Content-Type": "application/json"
    }
    payload = {
        "username": "Upbit Announcements",
        "embeds": [{
            "title": title,
            "color": 44444,
            "footer": {
                "text": time
            }
        }]
    }
    requests.post(webhookurl,headers=headers,json=payload)

def sendRequest(session,proxy,wait):
    print(f'process started {wait}')
    headers = {
        'Cache-Control': 'no-cache',
        'Accept-Encoding': 'gzip'
    }
    proxies = {
        'http': proxy,
        'https': proxy,
    }
    session.proxies.update(proxies) 

    time.sleep(wait)

    sent=datetime.now()
    res=session.get(f'https://api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=1&category=all&timestamp={float(sent.timestamp())}', headers=headers)
    recieved=datetime.now()
    
    sentwms = sent.strftime('%Y-%m-%d %H:%M:%S') + f'.{sent.strftime('%f')[:3] }'
    recievedwms = recieved.strftime('%Y-%m-%d %H:%M:%S') + f'.{recieved.strftime('%f')[:3] }'
    
    print(f'Response : {res.status_code}\nDelay : {recieved-sent}\nFound : {recieved}')

    if res.status_code != 200:
        pushToDiscord('Status Code not 200',res.status_code)
        return 
    
    title = res.json()['data']['notices'][0]['title']
    id = res.json()['data']['notices'][0]['id']

    last = loadLast()

    if title == last['title'] and id == last['id']:
        return 
    
    writeLast({'title': title,'id': id})

    pushToDiscord(title,sentwms+'\n'+recievedwms)


def testip(session,proxy,wait):
    print(proxy,wait)
    
    headers = {
        'Accept-Encoding': 'gzip'
    }
    
    proxies = {
        'http': proxy,
        'https': proxy,
    }
    
    session.proxies.update(proxies)
    
    time.sleep(wait)

    sent=datetime.now()
    res=session.get('https://api.ipify.org/?format=json', headers=headers)
    recieved=datetime.now()
    print(res.json())
    print(f'Response : {res.status_code}\nDelay : {recieved-sent}\nFound : {recieved}')


sleepTimes = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
if __name__ == '__main__':
    while True:
        for _,proxy in enumerate(proxylist):
            a=datetime.now()

            for wait in sleepTimes:
                p = multiprocessing.Process(target=sendRequest, args=(session,proxy,wait))
                p.start()
            
            time.sleep(1)
            print(f'Going to Next Proxy\nTime Taken {datetime.now()-a}: ')