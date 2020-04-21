import luigi
import os
import json
import requests
from multiprocessing import Pool

from ...twitter_example import get_tweets, print_it
from service_composition.pybossa.pybossa_wrapper import PybossaWrapper


class MakeDirectory(luigi.Task):
    path = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.path)

    def run(self):
        os.makedirs(self.path)

class IAmUseless(luigi.Task):
    def output(self):
        return luigi.LocalTarget("dummy")

    def run(self):
        with open(self.output().path, 'w') as file:
            file.write("dummy")

class TwitterCrawler(luigi.Task):
    terms = luigi.ListParameter()
    path = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.path)

    def run(self):
        

        with open(self.output().path, 'w') as out:
            tweets = get_tweets.run(None)
            for i, t in zip(range(10), tweets): 
                out.write(json.dumps(t))
                out.write('\n')

    def requires(self):
        return [MakeDirectory(path=os.path.dirname(self.path)), IAmUseless()]

class Geolocate(luigi.Task):
    id = luigi.Parameter(default='test')
    user = luigi.Parameter()
    password = luigi.Parameter()

    def f(self, t):
        print("sending request...")
        js = json.loads(t)
        r = requests.post(
            "http://131.175.120.108:20007/e2mc/CIME/v1.0/tweet/twitter_json", 
            json=js, 
            auth=(self.user, self.password), 
            timeout=200
        )
        js["cime_geo"] = r.json() if r.ok else "null"
        return js

    def run(self):
        with open(self.input().path, 'r') as tweets_file, open(self.output().path, 'w') as geolocated:
            n = 4
            with Pool(n) as p:
                results = p.map(self.f, tweets_file)
                for js in results:
                    geolocated.write(json.dumps(js))
                    geolocated.write('\n')
               
    def output(self):
        return luigi.LocalTarget('output_files/twitter_results/{}/geolocated.txt'.format(self.id))

    def requires(self):
        return TwitterCrawler(path='output_files/twitter_results/{}/tweets.txt'.format(self.id), terms=[])

class PrintCrawled(luigi.Task):
    id = luigi.Parameter(default='test')

    def run(self):
        with open(self.input().path, 'r') as tweets_file:
            for t in tweets_file:
                print_it.run(t)
        with open(self.output().path, 'w') as out:
            out.write("done")

    def requires(self):
        return Geolocate(id=self.id)

    def output(self):
        path = 'output_files/twitter_results/{}/done_deal.txt'.format(self.id)
        return luigi.LocalTarget(path)

PYBOSSA_CONFIG_PATH="../config/pybossa_config.json"
class ToPybossaProject(luigi.Task):
    id = luigi.Parameter(default='test')

    pybossa = None
    with open(os.path.abspath(PYBOSSA_CONFIG_PATH), 'r') as config_f:
        config = json.load(config_f)
        pybossa = PybossaWrapper(config['endpoint'], config['apikey'])
        print(pybossa.get_projects())
    pybossa.delete_all_projects() # For testing purposes
    project = pybossa.create_project('Test project name', 'Test project shortname', 'Test project description', 'service_composition/pybossa/json_presenter.html')

    def run(self):
        with open(self.input().path, 'r') as tweets_file:
            for tweet in tweets_file:
                self.pybossa.create_task(self.project.id, tweet)
        with open(self.output().path, 'w') as out:
            out.write("done")

    def requires(self):
        return TwitterCrawler(path='output_files/twitter_results/{}/tweets.txt'.format(self.id), terms=[])
        #return Geolocate(id=self.id)

    def output(self):
        path = 'output_files/twitter_results/{}/done_deal.txt'.format(self.id)
        return luigi.LocalTarget(path)


if __name__ == '__main__':
   luigi.run()
