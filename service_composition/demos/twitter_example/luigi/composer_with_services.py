import luigi
import os
import json
import requests
from multiprocessing import Pool

from service_composition.composer import service
from service_composition.pybossa.pybossa_wrapper import PybossaWrapper

class TwitterCrawler(luigi.Task):
    terms = luigi.ListParameter()
    path = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = service.PythonService("service_composition.python_services.get_tweets")

    def output(self):
        return luigi.LocalTarget(self.path)

    def run(self):
        with self.output().open('w') as out:
            tweets = self.service.run()
            for t in tweets: 
                out.write(t)
                out.write('\n')

class Geolocate(luigi.Task):
    id = luigi.Parameter(default='test')
    user = luigi.Parameter()
    password = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threads = 4
        self.service = service.HTTPService(
            "http://131.175.120.108:20007/e2mc/CIME/v1.0/tweet/twitter_json",
            service.HTTPMethod.POST,
            auth=(self.user, self.password), 
            timeout=200,
            headers={'Content-Type': 'application/json'},
        )

    def f(self, t):
        print("sending request...")
        js = json.loads(t)
        r = self.service.run(t)
        js["cime_geo"] = json.loads(r)
        return js

    def run(self):
        with self.input().open() as input_file, self.output().open('w') as output_file:
            if self.threads <= 1:
                results = [self.f(t) for t in input_file]
            else:
                with Pool(self.threads) as p: 
                    results = p.map(self.f, input_file)
            for js in results:
                output_file.write(json.dumps(js))
                output_file.write('\n')
        # self.input().remove()
               
    def output(self):
        return luigi.LocalTarget('output_files/twitter_results/{}/geolocated.txt'.format(self.id))

    def requires(self):
        return TwitterCrawler(path='output_files/twitter_results/{}/tweets.txt'.format(self.id), terms=[])

class PrintCrawled(luigi.WrapperTask):
    id = luigi.Parameter(default='test')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = service.PythonService("service_composition.python_services.print_it")

    def run(self):
        with self.input().open() as tweets_file:
            for t in tweets_file:
                self.service.run(t)

    def requires(self):
        return Geolocate(id=self.id)


PYBOSSA_CONFIG_PATH="../../../config/pybossa_config.json"
class ToPybossaProject(luigi.WrapperTask):
    id = luigi.Parameter(default='test')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = service.PythonService("service_composition.python_services.print_it")

    def run(self):
        with self.input().open() as tweets_file:
            for t in tweets_file:
                self.service.run(t)

    def requires(self):
        return Geolocate(id=self.id)

if __name__ == '__main__':
   luigi.run()
