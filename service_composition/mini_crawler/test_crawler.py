from mini_crawler import MiniCrawler
import os
import json

CONFIG_PATH="config.json"
OUTPUT_FOLDER = "data/test"
TERMS = ["covid", "coronavirus", "covid-19", "#covid-19", "#coronavirus"]

def test_constructor():
    crawler = MiniCrawler(config_path=CONFIG_PATH, output_folder=OUTPUT_FOLDER)
    print(crawler.output_folder)

def test_config():
    config_path = CONFIG_PATH
    config = None
    with open(os.path.abspath(config_path), 'r') as config_f:
        config = json.load(config_f)
    apikeys = list(config['apikeys'].values()).pop()
    print(apikeys)

def test_crawler():
    crawler = MiniCrawler(config_path=CONFIG_PATH, output_folder=OUTPUT_FOLDER)
    result = crawler.search_by_terms(TERMS, 10, output_to_file=True)
    #print(result)
    n = 1
    for tweet in result:
        print("Tweet {}:".format(n))
        print(tweet["text"])
        print("\n")
        n += 1

test_constructor()
test_config()

#commented just in case, uncomment to test
#test_crawler()

