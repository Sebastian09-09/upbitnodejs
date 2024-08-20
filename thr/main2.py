from concurrent.futures import ThreadPoolExecutor
import random 
import requests 
import time 
from datetime import datetime 
from threading import Thread
import json 

def loadLast(category):
    with open(f'{category}.json','r',encoding='utf-8') as f:
        return json.load(f)

def writeLast(data, category):
    with open(f'{category}.json','w',encoding='utf-8') as f:
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
            "color": 234234,
            "footer": {
                "text": time
            }
        }]
    }
    requests.post(webhookurl,headers=headers,json=payload)


def sendRequest(session,proxy,category):
    headers = {
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

    session.proxies.update(proxies) 
    sent=datetime.now()
    res=session.get(f'https://api-manager.upbit.com/api/v1/announcements/latest?os=web', headers=headers)
    recieved=datetime.now()
    
    sentwms = sent.strftime('%Y-%m-%d %H:%M:%S') + f'.{sent.strftime('%f')[:3] }'
    recievedwms = recieved.strftime('%Y-%m-%d %H:%M:%S') + f'.{recieved.strftime('%f')[:3] }'
    
    #print(f'Response : {res.status_code}\nDelay : {recieved-sent}\nFound : {recieved}')

    if res.status_code != 200:
        pushToDiscord('Status Code not 200',str(res.status_code)+" | "+proxy)
        return 
    
    listed_at = res.json()['data']['listed_at']

    latest = loadLast(category)
    
    if listed_at == latest['listed_at']:
        return 
    
    writeLast({'listed_at': listed_at} , category)

    found = [False, '']
    nres=session.get(f'https://api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=2&category=all', headers=headers)
    for dat in nres.json()['data']['notices']:
        if dat['listed_at'] == listed_at:
            found = [True, dat['title'] ]

    while not found[0] and nres.status_code == 200:
        nres=session.get(f'https://api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=2&category=all', headers=headers)
        for dat in nres.json()['data']['notices']:
            if dat['listed_at'] == listed_at:
                found = [True, dat['title'] ]

    pushToDiscord(found[1] ,sentwms+'\n'+recievedwms)

while True:
    try:
        for _,proxy in enumerate(proxylist):
            a=datetime.now()
            for i in range(2):
                t = Thread(target=sendRequest , args=(session,proxy,'latest'))
                t.start()
                time.sleep(0.5)
            print(f'Going to Next\nTime Taken : {datetime.now()-a}')

    except Exception as e:
        pushToDiscord("Error", e)
        break 


#    print(proxiestouse)
                
        #alreadyinuse = []
        #a = datetime.now()
        #for i in range(5):
        #    for cat in categories:
        #        proxy = getRandomProxy(alreadyinuse)
        #        alreadyinuse.append(proxy)
        #        #print(proxy,cat)
        #        t=Thread(target=sendRequest, args=(session,proxy,cat))
        #        t.start()

        #    time.sleep(0.2)
        #print(f'Going to Next\nTime Taken : {datetime.now()-a}')

        #for _,proxy in enumerate(proxylist):
        #    a=datetime.now()
        #    for i in range(5):
        #        t=Thread(target=sendRequest, args=(session,proxy))
        #        t.start()
        #        time.sleep(0.2)
        #        print(f'proxy {_} fired run {i}')

            #print(f'Going to Next Proxy\nTime Taken {datetime.now()-a}: ')
            #if _ % 50 == 0:
            #    Thread(target=pushToDiscord, args=('50 Proxies Done', f'Time Taken for Last Proxy : {datetime.now()-a}')).start()

    #except Exception as e:
    #    sendRequest("Error", e)
    #    break 