import json

def run(e):
    return json.dumps({ "text": e["tweet_text"] })