import os
import json

'''
Gets tweets from a json file as stored by the MiniCrawler
'''
class FakeCrawler:

    def __init__(self, *args, **kwargs):
        """
        Constructor with data_path
        """
        
        data_path = os.path.abspath(kwargs.pop('data_path', None))

        if not data_path or not os.path.exists(data_path):
            raise Exception('data file not found')

        self.data_path = data_path

    def get_tweets(self, amount=100, starting_at=0):
        end_at = starting_at + amount
        result = []
        with open(self.data_path, 'r') as fh:
            n = 0
            for line in fh:
                if n >= starting_at and n < end_at:
                    result.append(json.loads(line))
                n += 1
        return result


        
