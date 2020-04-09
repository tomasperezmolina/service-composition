import twython
import os
import json
import time
import datetime

CLIENT_ARGS = {'timeout': 30}

class MiniCrawler(twython.Twython):

    def __init__(self, *args, **kwargs):
        """
        Constructor with config_path, and output_folder
        """
        import copy

        
        config_path = copy.copy(kwargs.pop('config_path', './config.json'))

        if not os.path.exists(os.path.abspath(config_path)):
            raise Exception('config file not found')

        config = None
        with open(os.path.abspath(config_path), 'r') as config_f:
            config = json.load(config_f)

        apikeys = list(config['apikeys'].values()).pop()

        self.apikeys = copy.copy(apikeys) # keep a copy
        #self.crawler_id = kwargs.pop('crawler_id', None)

        self.output_folder = os.path.abspath(kwargs.pop('output_folder', './data'))
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        oauth2 = kwargs.pop('oauth2', True) # default to use oauth2 (application level access, read-only)

        if oauth2:
            # no need for these in oauth2
            apikeys.pop('oauth_token')
            apikeys.pop('oauth_token_secret')
            twitter = twython.Twython(apikeys['app_key'], apikeys['app_secret'], oauth_version=2)
            access_token = twitter.obtain_access_token()
            kwargs['access_token'] = access_token
            apikeys.pop('app_secret')
        else:
            # api needs a user context
            pass

        kwargs.update(apikeys)

        if not 'client_args' in kwargs:
            kwargs.update({'client_args': CLIENT_ARGS})

        super(MiniCrawler, self).__init__(*args, **kwargs)

    def search_by_terms(self, search_terms, amount=100, batch_size=100, exclude_retweets=True, since_id = 0, geocode=None, lang=None, output_to_file=False):

        query = None
        if (exclude_retweets):
            query = '%s -filter:retweets'%(' OR '.join('(' + term + ')' for term in search_terms))
        else:
            query = '%s'%(' OR '.join('(' + term + ')' for term in search_terms))

        now=datetime.datetime.now()
        #logger.info("query: %s; since_id: %d"%(query, since_id))
        place = None
        geo = None
        filename = None
        day_output_folder = None

        if (output_to_file):
            if (geocode):
                place, geo = geocode

                day_output_folder = os.path.abspath('%s/%s/%s'%(self.output_folder, now.strftime('%Y%m%d'), place))
            else:
                day_output_folder = os.path.abspath('%s/%s'%(self.output_folder, now.strftime('%Y%m%d')))

            if not os.path.exists(day_output_folder):
                os.makedirs(day_output_folder)


            import hashlib
            filename = os.path.abspath('%s/%s'%(day_output_folder, hashlib.md5(query.encode('utf-8')).hexdigest()))

        prev_max_id = -1

        if(batch_size > 100):
            batch_size = 100
        if (amount < batch_size):
            batch_size = amount

        current_max_id = 0
        cnt = 0
        current_since_id = since_id

        retry_cnt = 1 #3 in the example
        result_tweets = []
        while current_max_id != prev_max_id and retry_cnt > 0 and amount > cnt:
            try:
                print("querying {} tweets".format(batch_size))
                if current_max_id > 0: 
                    tweets = self.search(q=query, geocode=geo, since_id=since_id, lang=lang, tweet_mode='extended', max_id=current_max_id-1,count=batch_size) # result_type='recent',
                else:
                    tweets = self.search(q=query, geocode=geo, since_id=since_id, lang=lang, tweet_mode='extended', result_type='recent', count=batch_size)


                prev_max_id = current_max_id # if no new tweets are found, the prev_max_id will be the same as current_max_id

                if (output_to_file):
                    with open(filename, 'a+', newline='', encoding='utf-8') as f:
                        for tweet in tweets['statuses']:
                            f.write('%s\n'%json.dumps(tweet))
                            if current_max_id == 0 or current_max_id > int(tweet['id']):
                                current_max_id = int(tweet['id'])
                            if current_since_id == 0 or current_since_id < int(tweet['id']):
                                current_since_id = int(tweet['id'])
                else:
                    for tweet in tweets['statuses']:
                        if current_max_id == 0 or current_max_id > int(tweet['id']):
                            current_max_id = int(tweet['id'])
                        if current_since_id == 0 or current_since_id < int(tweet['id']):
                            current_since_id = int(tweet['id'])

                #no new tweets found
                if (prev_max_id == current_max_id):
                    break

                result_tweets.extend(tweets['statuses'])


                batch_length = len(tweets['statuses'])
                cnt += batch_length

                print("Got {} tweets".format(batch_length))

                #logger.debug('%d > %d ? %s'%(prev_max_id, current_max_id, bool(prev_max_id > current_max_id)))

                time.sleep(1)

            except twython.exceptions.TwythonRateLimitError:
                self.rate_limit_error_occured('search', '/search/tweets')
            except Exception as exc:
                time.sleep(10)
                print("exception: %s"%exc)
                retry_cnt -= 1
                if (retry_cnt == 0):
                    print("exceed max retry... return")
                    return since_id
                #raise MaxRetryReached("max retry reached due to %s"%(exc))

        #logger.info("[%s]; since_id: [%d]; total tweets: %d "%(query, since_id, cnt))
        print("Finished crawling, crawled {} tweets".format(cnt))
        return result_tweets

