import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.runners.portability.fn_api_runner import FnApiRunner
import requests
import json

from ...twitter_example import get_tweets, print_it

class Geolocate(beam.DoFn):
    def process(self, js):
        def f():
            print("sending request...")
            r = requests.post(
                "http://131.175.120.108:20007/e2mc/CIME/v1.0/tweet/twitter_json", 
                json=js, 
                auth=("cime", "cime"), 
                timeout=200
            )
            js["cime_geo"] = r.json() if r.ok else "null"
            return js
        yield f()

def run():
    with beam.Pipeline(runner=FnApiRunner()) as p:
        (p | beam.Create(get_tweets.run())
                    | beam.ParDo(Geolocate())
                    | beam.Map(print))

if __name__ == '__main__':
    run()