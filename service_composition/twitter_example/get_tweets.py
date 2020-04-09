
def run():
    from service_composition.mini_crawler.fake_crawler import FakeCrawler

    crawler = FakeCrawler(data_path="data/test/test.txt")
    tweets = crawler.get_tweets()
    return tweets