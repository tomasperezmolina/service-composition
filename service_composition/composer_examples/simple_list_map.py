import luigi
import json

from service_composition.composer.task import Task, fromDict
from service_composition.composer.service import FunctionService

if __name__ == "__main__":

    source = Task(
        service=FunctionService(lambda _: [{ "value": 1 }, { "value": 2 }, { "value": 3 }, { "value": 4 }]),
        name="source",
        path="output_files/list_map/source",
        output_data_type_map=fromDict
    )
    square = Task(
        service=FunctionService(lambda x: {"value": json.loads(x)["value"]**2 }),
        name="square",
        path="output_files/list_map/square",
        dependencies=[source],
        output_data_type_map=fromDict
    )
    sink = Task(
        service=FunctionService(lambda x: print(repr(x))),
        name="sink",
        path="output_files/list_map/sink",
        dependencies=[square],
        output_data_type_map=None
    )

    luigi.build([sink])

