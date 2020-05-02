import argparse
import luigi
import sys
import json

from service_composition.composer.task import Task, fromJSON
from service_composition.composer.service import HTTPService, HTTPMethod, PythonService
from service_composition.yaml_parser import yaml_parser

if __name__ == "__main__":
    argfile_parser = argparse.ArgumentParser(add_help=False)
    argfile_parser.add_argument('composer_file', nargs='?')

    full_parser = argparse.ArgumentParser(prog="composer")
    full_parser.add_argument('composer_file', help='composer file describing the pipeline, invoke help along with this argument to get a list of the arguments the file defines')

    composer_file = argfile_parser.parse_known_args()[0].composer_file
    if composer_file is not None:
        f = yaml_parser.get_variables(composer_file)
        composition_args = full_parser.add_argument_group('composition arguments')
        for arg in f:
            composition_args.add_argument(f"-{arg}", required=True)

    dynamic_args = full_parser.parse_args()

    # The filename is only needed to parse the yaml and read the arguments, not needed after that is done
    del dynamic_args.composer_file

    composition = yaml_parser.parse_composition(composer_file, vars(dynamic_args), print_debug=True)

    current_task = None
    
    for s in composition:
        if s.type == yaml_parser.ServiceType.HTTP:
            service = HTTPService(
                s.url,
                HTTPMethod(s.method),
                auth=(s.auth["user"], s.auth["password"]),
                timeout=200,
                headers={'Content-Type': 'application/json'},
            )
        elif s.type == yaml_parser.ServiceType.PYTHON:
            service = PythonService(s.file)
        else:
            raise RuntimeError(f"Service type {s.type} is not recognized!")
        if current_task is not None:
            dump_lambda = (lambda y: lambda x: json.dumps(x[y]))(current_task.name)
        id_lambda = lambda x: x
        current_task = Task(
            service=service,
            path=f'output_files/results/{s.name}',
            name=s.name,
            output_data_type_map=fromJSON,
            dependencies=[current_task] if current_task is not None else [],
            input_map=dump_lambda if s.type == yaml_parser.ServiceType.HTTP else id_lambda,
        )

    luigi.build([current_task])