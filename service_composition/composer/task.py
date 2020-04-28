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
    
    """
    Task dependencies that function as input for this task.
    """
    dependencies = luigi.Parameter(default=[], significant=False)

    """
    Transform the output of the task into the intermediate representation (IR) used by all tasks. 
    For example a task may return XML or JSON, these need to be transformed into the IR so the next task can access it.
    """
    output_data_type_map = luigi.Parameter(significant=False) 

    """
    How to transform the inputs of the task into a data structure that is fed into the service
    """
    input_map = luigi.Parameter(significant=False, default=lambda x: x)

    def run(self):
        if not self.dependencies:
            results = self.service.run()
        else:
            input_file = self.aggregate_inputs()
            if self.threads <= 1:
                results = [self.service.run(self.input_map(t)) for t in input_file]
            else:
                with Pool(self.threads) as p: 
                    results = p.map(self.service.run, list(map(self.input_map, input_file)))
        with self.output().open('w') as output_file:
            for r in results:
                if r is not None:
                    output_file.write(self.output_data_type_map(r))
                    output_file.write('\n')
               
    def output(self):
        return luigi.LocalTarget(self.path)

    def requires(self):
        return self.dependencies

    def aggregate_inputs(self):
        task_inputs = {}
        for target, task in zip(self.input(), self.requires()):
            with target.open() as input_file:
                inputs = []
                for i in input_file:
                    inputs.append(json.loads(i))
                task_inputs[task.name] = inputs
        input_size = len(task_inputs[list(task_inputs.keys())[0]])
        result = []
        for i in range(input_size):
            item = {}
            for k in task_inputs.keys():
                item[k] = task_inputs[k][i]
            result.append(item)
        return result

# For now the IR is JSON, it could be optimized by using another representation

def fromJSON(e):
    # Minimizes the json string
    return json.dumps(json.loads(e))

def fromDict(e):
    return json.dumps(e)
