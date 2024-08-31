import time 
import requests 
from datetime import datetime 
import json 
from threading import Thread 
import random
import string
from bs4 import BeautifulSoup

def generate_random_string(length=20):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for i in range(length))
    return random_string

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
proxylistused = set()

noOfSessions = 100
Sessions = []
Cookies = []

for i in range(0,noOfSessions):
    Sessions.append(requests.Session())
    Cookies.append('')


with open('webhook.json','r',encoding='utf-8') as f:
    webhookurl = json.load(f)['webhook']

def pushToMyDiscord(title,desc,time,url):
    headers= {
        "Content-Type": "application/json"
    }
    payload = {
        "username": "Binance Announcements",
        "embeds": [{
            "title": title,
            "description": f"[ Binance | {desc} ]",
            "url": url,
            "color": 16776960,
            "footer": {
                "text": time
            }
        }]
    }
    requests.post("https://discord.com/api/webhooks/1272560122438090776/YcH8v-Zsr8inS0zLdfqbMf8HZiT-YIxUQ2PZoNbUPXi3YdTEy0mu4mGwAtRbaIhfq_fU",headers=headers,json=payload)

def pushToDiscord(title,desc,time,url):
    headers= {
        "Content-Type": "application/json"
    }
    payload = {
        "username": "Binance Announcements",
        "embeds": [{
            "title": title,
            "description": f"[ Binance | {desc} ]",
            "url": url,
            "color": 16776960,
            "footer": {
                "text": time
            }
        }]
    }
    requests.post(webhookurl,headers=headers,json=payload)

latest = loadLast("latest")

def sendRequest(category,url,index):
    url += f'&nonce={index}&email={generate_random_string()}'
    global proxylist , proxylistused , latest 

    proxy = list(proxylist)[index]

    print(datetime.now(),proxy,index)

    headers = {
        "X-Buster": generate_random_string(),
        "X-Nonce": str(index),
        "Referer": "https://binance.com/",
        "Accept-language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip",
        "Cache-Control": "max-age=0, no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "priority": "u=0, i",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "authority": "www.binance.com",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip",
    }

    proxies = {
        'http': proxy,
        'https': proxy,
    }

    Sessions[index].cache = None 
    Sessions[index].proxies.update(proxies) 
    sent=datetime.now()
    res=Sessions[index].get(url, headers=headers)
    recieved=datetime.now()
    
    sentwms = sent.strftime('%Y-%m-%d %H:%M:%S') + f'.{sent.strftime('%f')[:3] }'
    recievedwms = recieved.strftime('%Y-%m-%d %H:%M:%S') + f'.{recieved.strftime('%f')[:3] }'
    
    #print(f'Response : {res.status_code}\nDelay : {recieved-sent}\nFound : {recieved}')

    print(res.headers['X-Cache-Date'],end=f' {index}\n')

    if res.status_code != 200:
        Thread(target=pushToDiscord , args=(title,'',sentwms+'\n'+recievedwms+'\n'+date , '')).start()
        Thread(target=pushToMyDiscord , args=(title,'',sentwms+'\n'+recievedwms+'\n'+date , '')).start()
        return 
    
    soup = BeautifulSoup(res.text , 'html.parser')
    script = json.loads(soup.find('script', id='__APP_DATA').text)

    for i in script['appState']['loader']['dataByRouteId']['d9b2']['catalogs']:
        title = i['articles'][0]['title']
        date = datetime.fromtimestamp(int(str(i['articles'][0]['releaseDate'])[:-3])).strftime('%Y-%m-%d, %H:%M:%S')
        catID = i['catalogId']
        catName = i['catalogName']

        if latest[str(catID)]['title'] == title or latest[str(catID)]['releaseDate'] > i['articles'][0]['releaseDate']:
            continue 
        
        latest[str(catID)]['title'] = title
        latest[str(catID)]['releaseDate'] = i['articles'][0]['releaseDate']

        writeLast(latest, category)

        Thread(target=pushToDiscord , args=(title,catName,sentwms+'\n'+recievedwms+'\n'+date , '' )).start()
        print(title)
        Thread(target=pushToMyDiscord , args=(title,catName,sentwms+'\n'+recievedwms+'\n'+date , '')).start()


#Threading 
# Keep the script running
while True:
    try:
        for i in range(0,noOfSessions):
            Thread(target=sendRequest, args=('latest','https://www.binance.com/en/support/announcement/new-cryptocurrency-listing?c=48&navId=48&hl=en' , i)).start()
            time.sleep(1.3)
            
    except:
        pushToDiscord('Bot Stopped!', '','Script Over!' , '')
        pushToMyDiscord('Bot Stopped!', '','Script Over!' , '')
        break 