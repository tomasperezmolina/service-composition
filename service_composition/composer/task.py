import luigi
from multiprocessing import Pool
from typing import List
import json

from service_composition.composer.service import Service

class Task(luigi.Task):
    name = luigi.Parameter()
    threads = luigi.IntParameter(default=1)

    service = luigi.Parameter(significant=False)
    path = luigi.Parameter(significant=False)
    '''
    Task dependencies that function as input for this task.

    TODO: each dependency should come with a mapping function to map the output of the dependency to the input this task needs.
    Or should there be a single mapping function gathering all inputs? In that case after the mapping we get an item that can be fed directly into the task's service.
    '''
    dependencies = luigi.Parameter(default=[], significant=False)

    '''
    Transform the output of the task into the intermediate representation (IR) used by all tasks. 
    For example a task may return XML or JSON, these need to be transformed into the IR so the next task can access it.
    '''
    output_data_type_map = luigi.Parameter(significant=False) 

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
                if r is not None:
                    output_file.write(self.output_data_type_map(r))
                    output_file.write('\n')
               
    def output(self):
        return luigi.LocalTarget(self.path)

    def requires(self):
        return self.dependencies

# For now the IR is JSON, it could be optimized by using another representation

def fromJSON(e):
    # Minimizes the json string
    return json.dumps(json.loads(e))

def fromDict(e):
    return json.dumps(e)
