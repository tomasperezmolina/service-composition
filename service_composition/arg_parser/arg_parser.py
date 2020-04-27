import argparse

"""
This will take a filename and read arguments from it, adding them to the command line parser and the help.
Ex:
$ python .\arg_parser.py --help  

usage: composer [-h] composer_file

positional arguments:
  composer_file  composer file describing the pipeline, invoke help along with
                 this argument to get a list of the arguments the file defines

optional arguments:
  -h, --help     show this help message and exit   

But if we give it a file, it will read the arguments it defines, and add them to the help:

$ $ python .\arg_parser.py args.txt --help  

usage: composer [-h] -argA ARGA -argB ARGB -argC ARGC composer_file

positional arguments:
  composer_file  composer file describing the pipeline, invoke help along with
                 this argument to get a list of the arguments the file defines

optional arguments:
  -h, --help     show this help message and exit
  -argA ARGA
  -argB ARGB
  -argC ARGC

Hard to make this reusable without complicating things further.
Use it template and replace the file open with the yaml parser.
That way you can send the arguments from the yaml parser to the command line parser and keep whatever else the yaml parser gets.

Making this reusable would probably require a stateful object, or somekind of lambda being passed, 
in order to do work between reading the file and reading the commandline arguments.
We cannot break the control flow after reading the filename, otherwise the help function won't work properly.
"""

if __name__ == "__main__":
    argfile_parser = argparse.ArgumentParser(add_help=False)
    argfile_parser.add_argument('composer_file', nargs='?')

    full_parser = argparse.ArgumentParser(prog="composer")
    full_parser.add_argument('composer_file', help='composer file describing the pipeline, invoke help along with this argument to get a list of the arguments the file defines')

    composer_file = argfile_parser.parse_known_args()[0].composer_file
    if composer_file is not None:
        # Just replace this open with yaml_parser.parse_composition
        with open(composer_file, 'r') as f:
            for arg in f:
                full_parser.add_argument('-' + arg.strip(), required=True)

    dynamic_args = full_parser.parse_args()

    # The filename is only needed to parse the yaml and read the arguments, not needed after that is done
    del dynamic_args.composer_file

    print(dynamic_args)