from service_composition.mini_crawler.fake_crawler import FakeCrawler

TEST_FILE="../data/test.txt"

def test_get_tweets():
    crawler = FakeCrawler(data_path=TEST_FILE)
    tweets = crawler.get_tweets(amount=10, starting_at=0)
    
    n = 1
    for tweet in tweets:
        print("Tweet {}:".format(n))
        print(tweet["text"])
        print("\n")
        n += 1

test_get_tweets()
