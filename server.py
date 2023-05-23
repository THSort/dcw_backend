from flask import Flask , request , abort
from flask_cors import CORS, cross_origin
import sys
import json
import requests
from bs4 import BeautifulSoup
import datetime
from datetime import date
from flask_apscheduler import APScheduler
from flask_matomo import *
from apscheduler.schedulers.background import BackgroundScheduler
from twilio.rest import Client
import pandas as pd 

# from heyoo import WhatsApp

app = Flask(__name__)
CORS(app)
# matomo = Matomo(app, matomo_url="https://dcwwebapp.matomo.cloud/",id_site=1, token_auth="8fa95ce59879d0fa76a6bfa83a25f500")

app.config['SECRET_KEY'] = 'myAppSecretKey'

scheduler = BackgroundScheduler(daemon=True)
# messenger = WhatsApp('EAATB7dhJHjsBADvfD2iyjyhgjmpzKDAFghMuHbIEe3t1QLqKvYcezTS0JtnLvKIZArOxjfYBrfZByCmAObCUhQdlCpPCoG5cDZAuaTwZBnU2v98NBMZARt7S8sO4QLeZB0CnDn1PVZB1yxwGkiQns1u3p6QkXMq6gJ6WZCrE7FzDMSkjwSPrHsxLYZCq6jReIeB8N5HZC4aTVL3gZDZD',phone_number_id='103015676020734')

def scheduleTask():
#     # # For sending a Text messages
#     # messenger.send_message('https://e04i0uq5ei.execute-api.us-east-2.amazonaws.com/', '923211043091')

#     headers = {
#         "Authorization": "Bearer EAATB7dhJHjsBADvfD2iyjyhgjmpzKDAFghMuHbIEe3t1QLqKvYcezTS0JtnLvKIZArOxjfYBrfZByCmAObCUhQdlCpPCoG5cDZAuaTwZBnU2v98NBMZARt7S8sO4QLeZB0CnDn1PVZB1yxwGkiQns1u3p6QkXMq6gJ6WZCrE7FzDMSkjwSPrHsxLYZCq6jReIeB8N5HZC4aTVL3gZDZD",
#         "Content-Type": "application/json",
#     }
#     json_data = {
#        "messaging_product": "whatsapp",
#        "to": "923158972386",
#        'type': 'text',
#        "text": {
#            "body": "https://e04i0uq5ei.execute-api.us-east-2.amazonaws.com/"
#        }
#    }

#     response = requests.post('https://graph.facebook.com/v15.0/103015676020734/messages', headers=headers, json=json_data)
#     print(response.text)

    # TWILIO
    account_sid = "AC9565c3efedecda35ceb4ed7f902cf13a"
    auth_token = "b958a85c59c5e586d77063976b704b62"
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body = "https://e04i0uq5ei.execute-api.us-east-2.amazonaws.com/",
        to='whatsapp:+923211043091'
     )

    # print(message.sid)


scheduler.add_job(func=scheduleTask, trigger="interval", minutes=1)
scheduler.start()

@app.route("/")
def recentArticles():
    url = "https://www.sochfactcheck.com/category/politics/"

    html_content = requests.get(url).text

    soup = BeautifulSoup(html_content , "html.parser")

    cards = soup.find_all("div", {"class": "card"})

    templist = []
    for card in cards:
        anchor = card.find("a") # anchor tag details
        # <a href="https://www.sochfactcheck.com/journalist-ahmad-noorani-did-not-report-that-general-bajwa-took-a-50-crore-bribe-to-oust-imran-khan/">
        #     <span class="label"></span>
        #     <picture>
        #         <img alt="" data-src="https://www.sochfactcheck.com/wp-content/uploads/2022/12/Ahmed-Noorani-FC.png" src="https://www.sochfactcheck.com/assets/images/placeholder.svg"/>
        #     </picture>
        # </a>
        article_link = anchor.get("href") # article link
        img_data_src = anchor.find("img").get("data-src") # IS MORE IMPORTANT -- THE ACTUAL PICTURE ITSELF
        img_src = anchor.find("img").get("src") # IS JUST THE PLACE HOLDER (EMPTY GREY BOX)

        details = card.find("div" , {"class": "details"})
        # <div class="details">
            # <a href="https://www.sochfactcheck.com/journalist-ahmad-noorani-did-not-report-that-general-bajwa-took-a-50-crore-bribe-to-oust-imran-khan/">
            # <h3>
            #   Journalist Ahmad Noorani did not report that General Bajwa took a 50 crore bribe to oust Imran Khan
            # </h3>
            # </a>
            # <div class="time-category">
            #   <time datetime="2022-12-29T12:33:52+05:00" itemprop="datePublished">29 December 2022</time>
            #   <ul class="post-categories">
            #       <li><a href="https://www.sochfactcheck.com/category/pakistan/" rel="category tag">Pakistan</a></li>
            #       <li><a href="https://www.sochfactcheck.com/category/politics/" rel="category tag">Politics</a></li></ul>
            # </div>
        # </div>
        article_headline = details.find("h3").text.strip() # article headline
        article_date = details.find("time").text.strip() # date on which article was posted

        resp = {
            "Response": 200,
            "Article_Link": article_link,
            "Img_Data_Src": img_data_src,
            "Img_src": img_src,
            "Article_Headline": article_headline,
            "Article_Date": article_date
        }
        article_day = article_date.split()[0]
        article_month = article_date.split()[1]
        article_year = article_date.split()[2]

        today = datetime.date.today()

        year = today.year
        month = today.month
        day = today.day

        month_map = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}
        article_datetime = date(int(article_year), month_map[article_month], int(article_day))
        diff = today - article_datetime
        if(diff.days <= 7):
            templist.append(resp)

    return templist

@app.route("/all")
def allArticles():
    url = "https://www.sochfactcheck.com/category/politics/"

    html_content = requests.get(url).text

    soup = BeautifulSoup(html_content , "html.parser")

    cards = soup.find_all("div", {"class": "card"})

    templist = []
    for card in cards:
        anchor = card.find("a") # anchor tag details
        # <a href="https://www.sochfactcheck.com/journalist-ahmad-noorani-did-not-report-that-general-bajwa-took-a-50-crore-bribe-to-oust-imran-khan/">
        #     <span class="label"></span>
        #     <picture>
        #         <img alt="" data-src="https://www.sochfactcheck.com/wp-content/uploads/2022/12/Ahmed-Noorani-FC.png" src="https://www.sochfactcheck.com/assets/images/placeholder.svg"/>
        #     </picture>
        # </a>
        article_link = anchor.get("href") # article link
        img_data_src = anchor.find("img").get("data-src") # IS MORE IMPORTANT -- THE ACTUAL PICTURE ITSELF
        img_src = anchor.find("img").get("src") # IS JUST THE PLACE HOLDER (EMPTY GREY BOX)

        details = card.find("div" , {"class": "details"})
        # <div class="details">
            # <a href="https://www.sochfactcheck.com/journalist-ahmad-noorani-did-not-report-that-general-bajwa-took-a-50-crore-bribe-to-oust-imran-khan/">
            # <h3>
            #   Journalist Ahmad Noorani did not report that General Bajwa took a 50 crore bribe to oust Imran Khan
            # </h3>
            # </a>
            # <div class="time-category">
            #   <time datetime="2022-12-29T12:33:52+05:00" itemprop="datePublished">29 December 2022</time>
            #   <ul class="post-categories">
            #       <li><a href="https://www.sochfactcheck.com/category/pakistan/" rel="category tag">Pakistan</a></li>
            #       <li><a href="https://www.sochfactcheck.com/category/politics/" rel="category tag">Politics</a></li></ul>
            # </div>
        # </div>
        article_headline = details.find("h3").text.strip() # article headline
        article_date = details.find("time").text.strip() # date on which article was posted

        resp = {
            "Response": 200,
            "Article_Link": article_link,
            "Img_Data_Src": img_data_src,
            "Img_src": img_src,
            "Article_Headline": article_headline,
            "Article_Date": article_date
        }
        article_day = article_date.split()[0]
        article_month = article_date.split()[1]
        article_year = article_date.split()[2]

        # print(json.dumps(resp))
        templist.append(resp)

    return templist

@app.route('/article/<string:headline>') # headline needs to be dash-separated and not space separated!
def viewArticle(headline):
    print(headline)
    html_content = requests.get("https://www.sochfactcheck.com/" + headline).text

    soup = BeautifulSoup(html_content , "html.parser")

    page_content = soup.find("article", {"class": "sPost"})
    # fhandle = open("page_content.txt" , "w" , encoding="utf-8")
    # fhandle.write(str(page_content))
    # fhandle.close()
    img_data_src = page_content.find("img").get("data-src") # IS MORE IMPORTANT -- THE ACTUAL PICTURE ITSELF

    resp = {
        "content": str(page_content),
        "img_link": img_data_src
    }
    return resp

@app.route("/tracking/", methods = ['POST'])
def trackingData():
    # print("\nHELLOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO\n")
    tracking_data = request.get_json()
    # {'page_url': {'pathname': '/home/03211043091', 'search': '', 'hash': ''}, 'phone_number': '03211043091', 'time_stamp': 'Fri May 19 2023 00:17:37 GMT+0500 (Pakistan Standard Time)'}
    page_url = tracking_data['page_url']['pathname']
    phone_num = tracking_data['phone_number']
    visit_timestamp = tracking_data['time_stamp']

    data = {
        'phone_num': [phone_num],
        'page_url': [page_url],
        'timestamp': [visit_timestamp]
    }

    df = pd.DataFrame(data)
    df.to_csv('logs.csv', mode='a', index=False, header=False)



    return tracking_data

if __name__ == "__main__":
    app.run(host='110.93.235.130', port=7777)