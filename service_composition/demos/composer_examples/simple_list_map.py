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
    source2 = Task(
        service=FunctionService(lambda _: [{ "value": 2 }, { "value": 5 }, { "value": 10 }, { "value": 1 }]),
        name="source2",
        path="output_files/list_map/source2",
        output_data_type_map=fromDict
    )
    square = Task(
        service=FunctionService(lambda x: {
            "value": x["value1"]**2 + x["value2"]**2 
        }),
        name="square",
        path="output_files/list_map/square",
        dependencies=[source, source2],
        output_data_type_map=fromDict,
        input_map=lambda x: {
            "value1": x["source"]["value"],
            "value2": x["source2"]["value"],
        }
    )
    sink = Task(
        service=FunctionService(lambda x: print(repr(x["square"]))),
        name="sink",
        path="output_files/list_map/sink",
        dependencies=[square],
        output_data_type_map=None
    )

    luigi.build([sink])

