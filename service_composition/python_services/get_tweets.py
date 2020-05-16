import json

def run(e = None, **kwargs):
    from service_composition.mini_crawler.fake_crawler import FakeCrawler

    crawler = FakeCrawler(data_path="data/tweets/default-etna.txt")
    tweets = crawler.get_tweets()
    return [json.dumps(t) for t in tweets]
