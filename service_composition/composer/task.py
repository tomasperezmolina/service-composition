import luigi
from multiprocessing import Pool
from typing import List

from service_composition.composer.service import Service

class Task(luigi.Task):
    service = luigi.Parameter(significant=False)
    path = luigi.Parameter(significant=False)
    dependencies = luigi.Parameter(default=[], significant=False)
    threads = luigi.IntParameter(default=1)
    name = luigi.Parameter()

    def run(self):
        if not self.dependencies:
            with self.output().open('w') as output_file:
                results = self.service.run()
                for r in results:
                    output_file.write(r)
                    output_file.write('\n')
        else:
            with self.input()[0].open() as input_file, self.output().open('w') as output_file:
                if self.threads <= 1:
                    results = [self.service.run(t) for t in input_file]
                else:
                    with Pool(self.threads) as p: 
                        results = p.map(self.service.run, input_file)
                for r in results:
                    output_file.write(r)
                    output_file.write('\n')
               
    def output(self):
        return luigi.LocalTarget(self.path)

    def requires(self):
        return self.dependencies
    