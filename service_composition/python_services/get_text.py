import json

def run(e, **kwargs):
    return json.dumps({ "text": e["tweet_text"] })