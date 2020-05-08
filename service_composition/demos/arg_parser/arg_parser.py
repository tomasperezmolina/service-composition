import argparse
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