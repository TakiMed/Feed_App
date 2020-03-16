import feedparser
from datetime import datetime
from flask import Flask, request
from bson.json_util import dumps
from config import mydb, mycol_sources
import json
def parse (url):
    return feedparser.parse(url)

def get_articles(parsed):
    articles=[]
    for entry in parsed['entries']:
        articles.append({
            'id': entry['id'],
            'title': entry['title'],
            'summary': entry['summary'],
            'link': entry['link'],
            'published': entry['published_parsed'] if 'published_parsed' in entry.keys() else entry['updated_parsed']
            })
    return articles
app = Flask(__name__)
@app.route("/sources", methods=["POST","GET"])
def create_sources_coll():
    if request.method=="POST":
        sources=[{
        "name":"nasa",
        "url":"https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "title":"NASA Breaking news"

    },
    {   "name":"reddit",
        "url":"https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "title":"Reddit front page"},
    {
        "name":"mobile",
        "url":"https://www.mobileworldlive.com/latest-stories/feed/",
        "title":"Mobile World Live"
    }]
        try:
            mycol_sources.insert_many(sources)
            return dumps(mycol_sources.find())
        except Exception as e:
            return dumps({"error": str(e)})
    elif request.method=="GET":
        try:
            return dumps(mycol_sources.find())
        except Exception as e:
            return dumps({"error": str(e)})

@app.route('/sources/<feed_name>', methods=["PUT","DELETE"])
def put_and_delete_from_sources(feed_name):
    if request.method=="PUT":
        request_data=request.get_json()
        request_dict=json.loads(request_data)
        try:
            for key in request_dict.keys():
                mycol_sources.update_one({"name":feed_name},{"$set": {key:request_dict[key]}})
            return dumps(mycol_sources.find_one({"name":feed_name}))
        except Exception as e:
            return dumps({"error": str(e)})
    elif request.method=="DELETE":
        try:
            mycol_sources.find_one_and_delete({"name":feed_name})
            return dumps(mycol_sources.find())
        except Exception as e:
            return dumps({"error": str(e)})
#fetch
@app.route("/feed/<feed_name>", methods=["POST"])
def fetch_articles(feed_name):
    feed=mycol_sources.find_one({"name":feed_name})
    if request.method=="POST":
        try:
            feed_url=feed["url"]
            all_articles=get_articles(parse(feed_url))
            return dumps(all_articles)
        except Exception as e:
            return dumps({"error": str(e)})

#new
@app.route("/article/<feed_name>", methods=["GET","POST"] )
def article_fun(feed_name):
    mycol=mydb[feed_name]
    if request.method=="GET":
        try:
            articles = list(mycol.find())
            return dumps(articles)
        except Exception as e:
            return dumps({"error": str(e)})
    elif request.method=="POST":
        request_data=request.get_json()
        try:
            new_article={
                'id':request_data['id'],
                'title': request_data['title'],
                'summary': request_data['summary'],
                'link': request_data['link'],
                'published': request_data['published_parsed'] #if 'published_parsed' in request_data.keys() else request_data['updated_parsed']
            }
            mycol.insert_one(new_article)
            return dumps(mycol.find())
        except Exception as e:
            return dumps({"error": str(e)})

@app.route("/feed/<feed_name>/<article_title>", methods=["DELETE","PUT"])
def del_and_put_articles(feed_name,article_title):
    mycol=mydb[feed_name]
    if request.method=="DELETE":
        try:
            mycol.find_one_and_delete({"title":article_title})
            return dumps(mycol.find())
        except Exception as e:
            return dumps({"error": str(e)})
    elif request.method=="PUT":
        request_data=request.get_json()
        request_dict=json.loads(request_data)
        try:
            for key in request_dict.keys():
                mycol.update_one({"title":article_title},{"$set": {key:request_dict[key]}})
            return dumps(mycol.find_one({"title":article_title}))
        except Exception as e:
            return dumps({"error": str(e)})

app.run(port=1000)