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
    print(proxy, category)
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
    res=session.get(f'https://api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=1&category={category}', headers=headers)
    recieved=datetime.now()
    
    sentwms = sent.strftime('%Y-%m-%d %H:%M:%S') + f'.{sent.strftime('%f')[:3] }'
    recievedwms = recieved.strftime('%Y-%m-%d %H:%M:%S') + f'.{recieved.strftime('%f')[:3] }'
    
    #print(f'Response : {res.status_code}\nDelay : {recieved-sent}\nFound : {recieved}')

    if res.status_code != 200:
        pushToDiscord('Status Code not 200',str(res.status_code)+" | "+proxy)
        return 
    
    title = res.json()['data']['notices'][0]['title']
    id = res.json()['data']['notices'][0]['id']

    last = loadLast(category)
    
    if title == last['title'] and id == last['id']:
        return 
    
    writeLast({'title': title,'id': id} , category)

    pushToDiscord(title+"\n"+category ,sentwms+'\n'+recievedwms)


categories = ['notice','trade','dtw','maintenance','digital_asset','nft','staking','event']

counter = 0

while True:
    try:
        a = datetime.now()
        proxiestouse = []
        while len(proxiestouse) != 8:
            for i in proxylist[counter:]:
                proxiestouse.append(i)
                counter += 1
                if len(proxiestouse) == 8:
                    break 

            if counter >= 94:
                counter = 0

        for i in range(2):

            for index in range(8):
                cat = categories[index]
                proxy = proxiestouse[index]

                t=Thread(target=sendRequest, args=(session,proxy,cat))
                t.start()

            time.sleep(0.4)

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