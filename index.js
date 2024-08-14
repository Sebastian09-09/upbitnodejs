import fetch from 'node-fetch';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import fs from 'fs/promises';


puppeteer.use(StealthPlugin());

const data = await fs.readFile("webhook.json", 'utf8');

const webhookurl = JSON.parse(data).webhook;

async function postToDiscordWebhook(title,timeStamp) {
    try {
        const response = await fetch(webhookurl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: "Upbit Announcements",
                embeds: [{
                    title: title ,
                    color: 13709,
                    footer: {
                        text: timeStamp
                    }
                }] 
            }),
        });
    } catch {}
}

async function logToDiscordWebhook(title,desc,url=null) {
    try {
        const response = await fetch(webhookurl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: "Upbit Announcements",
                embeds: [{
                    title: title ,
                    url: url,
                    description: desc 
                }] 
            }),
        });
    } catch {}
}

const announcementHandler = async (response) => {
    const url = response.url();
    const now = new Date();

    await fs.appendFile('endpoint.txt', url+'|'+now+'\n');
    try{
        const responseBody = await response.json();
        const responseBodyText = JSON.stringify(responseBody, null, 2);
        logToDiscordWebhook('Got Json', responseBodyText, url);
        if (responseBodyText.includes('2024-08-14')) {
            logToDiscordWebhook('Got Json with 2024-08-14', responseBodyText, url);
            await fs.appendFile('specialurl.txt', url+'|'+now+'\n'+responseBodyText+'\n\n');
        }

    }catch{}

    if (url.includes('announcement')) {
        try{
            const responseBody = await response.json();
            if (responseBody.data.notices){
                postToDiscordWebhook(responseBody.data.notices[0].title , now );
            }else if (responseBody.data.title){
                postToDiscordWebhook(responseBody.data.title , now );
            }else {
                const responseBodyText = JSON.stringify(responseBody, null, 2);
                logToDiscordWebhook('Got URL with announcement', responseBodyText, url);
                await fs.appendFile('else.txt', url+'|'+now+'\n'+responseBodyText+'\n\n');
            }
        }catch{}
    }
};

(async () => {

    const browser = await puppeteer.launch({
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-software-rasterizer'
        ]});

    const page = await browser.newPage();

    await page.goto('https://upbit.com/service_center/notice', {waitUntil: 'networkidle2'});
    
    //await page.goto('https://upbit.com/service_center/notice');

    await page.on('response', announcementHandler);
    
    console.log('Monitoring Upbit Announcements!');
    logToDiscordWebhook('Monitoring Upbit Announcements!', 'Bot it Up!');
})();