import luigi
import os
import json
import requests

from ..twitter_example import get_tweets, print_it

class MakeDirectory(luigi.Task):
    path = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.path)

    def run(self):
        os.makedirs(self.path)

class TwitterCrawler(luigi.Task):
    terms = luigi.ListParameter()
    path = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.path)

    def run(self):
        with open(self.output().path, 'w') as out:
            tweets = get_tweets.run()
            for i, t in zip(range(5), tweets): 
                out.write(json.dumps(t))
                out.write('\n')

    def requires(self):
        return MakeDirectory(path=os.path.dirname(self.path))

class Geolocate(luigi.Task):
    id = luigi.Parameter(default='test')
    user = luigi.Parameter()
    password = luigi.Parameter()

    def run(self):
        with open(self.input().path, 'r') as tweets_file, open(self.output().path, 'w') as geolocated:
            for t in tweets_file:
                js = json.loads(t)
                r = requests.post(
                    "http://131.175.120.108:20007/e2mc/CIME/v1.0/tweet/twitter_json", 
                    json=js, 
                    auth=(self.user, self.password), 
                    timeout=200
                )
                if r.ok:
                    js["cime_geo"] = r.json() if r.ok else "null"
                    geolocated.write(json.dumps(js))
                    geolocated.write('\n')
                else:
                    print(r.json())
    
    def output(self):
        return luigi.LocalTarget('results/{}/geolocated.txt'.format(self.id))

    def requires(self):
        return TwitterCrawler(path='results/{}/tweets.txt'.format(self.id), terms=[])

class PrintCrawled(luigi.Task):
    id = luigi.Parameter(default='test')

    def run(self):
        with open(self.input().path, 'r') as tweets_file:
            for t in tweets_file:
                print_it.run(t)
        with open(self.output().path, 'w') as out:
            out.write("done")

    def requires(self):
        return Geolocate()

    def output(self):
        path = 'results/{}/done_deal.txt'.format(self.id)
        return luigi.LocalTarget(path)

if __name__ == '__main__':
   luigi.run()