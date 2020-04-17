import json

def run(e):
    from service_composition.mini_crawler.fake_crawler import FakeCrawler

    crawler = FakeCrawler(data_path="data/tweets/default.txt")
    tweets = crawler.get_tweets()
    return [json.dumps(tweets[0])]