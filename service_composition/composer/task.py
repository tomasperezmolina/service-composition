import luigi
from multiprocessing import Pool
from typing import List
import json

from service_composition.composer.service import Service

class Task(luigi.Task):
    service = luigi.Parameter(significant=False)
    path = luigi.Parameter(significant=False)
    dependencies = luigi.Parameter(default=[], significant=False)
    threads = luigi.IntParameter(default=1)
    name = luigi.Parameter()

    def run(self):
        if not self.dependencies:
            results = self.service.run()
        else:
            with self.input()[0].open() as input_file:
                if self.threads <= 1:
                    results = [self.service.run(t) for t in input_file]
                else:
                    with Pool(self.threads) as p: 
                        results = p.map(self.service.run, input_file)
        with self.output().open('w') as output_file:
            for r in results:
                if r:
                    js = json.loads(r)
                    output_file.write(json.dumps(js))
                    output_file.write('\n')
               
    def output(self):
        return luigi.LocalTarget(self.path)

    def requires(self):
        return self.dependencies
    