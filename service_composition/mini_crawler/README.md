# Mini Twitter crawler
Based on [https://github.com/bianjiang/tweetf0rm](https://github.com/bianjiang/tweetf0rm/)

## Dependencies
- [Twython](https://github.com/ryanmcgrath/twython)

Run:
```bash
pip install -r requirements.txt
```

## Getting started
- Create a twitter dev account at https://dev.twitter.com/apps
- Create an application and get your `Consumer Key`, `Consumer Secret`, `Access token` and `Access token secret`
- You will need to complete the following config.json file with your data, be careful not to share it.
```json
{
        "apikeys": {
                "myapp": {
                        "app_key": "APP_KEY",
                        "app_secret": "APP_SECRET",
                        "oauth_token": "OAUTH_TOKEN",
                        "oauth_token_secret": "OAUTH_TOKEN_SECRET"
                }
        }
}
```
## Usage
The `MiniCrawler` constructor has two optional arguments:
- `config_path`:  path to the config.json file (defaults to ./config.json)
- `output_folder`:  path to the output folder where the crawled tweets will be stored (defaults to ./data)

Example:
```python
    crawler = MiniCrawler(config_path="../config/config.json", output_folder="../data/my_data")
    tweets = crawler.search_by_terms(["covid", "coronavirus", "covid-19", "#covid-19", "#coronavirus"], 100)
    n = 1
    for tweet in tweets:
        print("Tweet {} :".format(n))
        print(tweet["full_text"])
        print("\n")
        n += 1
```


The `FakeCrawler` can be used to parse the tweets stored by the `MiniCrawler`, arguments:
- `data_path`: path to the data file to read from

Example:
```python
    crawler = FakeCrawler(data_path="../data/test.txt")
    tweets = crawler.get_tweets(amount=10, starting_at=20)
    n = 1
    for tweet in tweets:
        print("Tweet {}:".format(n))
        print(tweet["full_text"])
        print("\n")
        n += 1
```
