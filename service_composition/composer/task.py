import luigi
from multiprocessing import Pool
from typing import List
import json

from service_composition.composer.service import Service

class Task(luigi.Task):
    """Wrapper for a luigi task, capable of running a single service in a pipeline according to the given configuration"""

    """Name of the task"""
    name = luigi.Parameter()

    """Amount of threads to run the task in parallel"""
    threads = luigi.IntParameter(default=1)

    """Service to run in this task"""
    service = luigi.Parameter(significant=False)

    """Output path for the task execution"""
    path = luigi.Parameter(significant=False)
    
    """Task dependencies that function as input for this task."""
    dependencies = luigi.Parameter(default=[], significant=False)

    """
    Transform the output of the task into the intermediate representation (IR) used by all tasks. 
    For example a task may return XML or JSON, these need to be transformed into the IR so the next task can access it.
    """
    output_data_type_map = luigi.Parameter(significant=False) 

    """How to transform the inputs of the task into a data structure that is fed into the service"""
    input_map = luigi.Parameter(significant=False, default=lambda x: x)

    """Include data fed as input in the output of this task"""
    include_previous_data = luigi.BoolParameter(significant=False, default=False)

    def run(self):
        if not self.dependencies:
            results = map(self.to_IR, self.service.run())
        else:
            input_file = self.aggregate_inputs()
            adapted_inputs = map(self.input_map, input_file)
            if self.threads <= 1:
                service_outputs = [self.service.run(t) for t in adapted_inputs]
            else:
                with Pool(self.threads) as p: 
                    service_outputs = p.map(self.service.run, adapted_inputs)
            ir_outputs = list(map(self.to_IR, service_outputs))
            if self.include_previous_data:
                for (i, o) in zip(input_file, ir_outputs):
                    o["__input__"] = i
            results = ir_outputs
        with self.output().open('w') as output_file:
            for r in results:
                if r is not None:
                    output_file.write(json.dumps(r))
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

    def to_IR(self, e):
        if e is None:
            return None
        else:
            return self.output_data_type_map(e)

# For now the IR is a dict, it could be optimized by using another representation

def fromJSON(e):
    # Minimizes the json string
    return json.loads(e)

def fromDict(e):
    return e
