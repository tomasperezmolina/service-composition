import argparse
import luigi
import sys
import json
import uuid

from service_composition.composer.task import Task, fromJSON
from service_composition.composer.service import HTTPService, HTTPMethod, PythonService
from service_composition.yaml_parser import yaml_parser

def serializer_for_content_type(content_type):
    if content_type is None:
        return lambda x: x
    if content_type == 'json':
        return json.dumps
    else:
        raise RuntimeError(f"Unknown content-type {content_type}")

def header_for_content_type(content_type):
    if content_type is None:
        return 'text/plain'
    if content_type == 'json':
        return 'application/json'
    else:
        raise RuntimeError(f"Unknown content-type {content_type}")

if __name__ == "__main__":
    run_id = uuid.uuid4()

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
                serializer=serializer_for_content_type(s.content_type),
                auth=(s.auth["user"], s.auth["password"]),
                headers={'Content-Type': header_for_content_type(s.content_type)},
                **s.extra_args,
            )
        elif s.type == yaml_parser.ServiceType.PYTHON:
            service = PythonService(s.file)
        else:
            raise RuntimeError(f"Service type {s.type} is not recognized!")

        if current_task is not None:
            flatten = (lambda y: lambda x: x[y])(current_task.name)
        else:
            flatten = lambda x: x

        current_task = Task(
            service=service,
            path=f'output_files/results/{run_id}/{s.name}',
            name=s.name,
            threads=s.threads,
            output_data_type_map=fromJSON,
            dependencies=[current_task] if current_task is not None else [],
            input_map=flatten,
            include_previous_data=s.connection_args.get("include-previous", False)
        )

    luigi.build([current_task])

    print(f"RUN ID: {run_id}")