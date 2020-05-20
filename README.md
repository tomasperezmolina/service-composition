# Service composition prototype

## Requirements
- Python 3.7
- Pipenv

## Installation

```bash
$ pipenv install
```

### Setup environment to run luigi workflows
```bash
$ pipenv shell
$ luigid
```
The following commands assume that the environment is setup correctly

## Run Composer
Add -h, --help to show help about parameters

```bash
$ python -m service_composition.composer.composer
```

## Demo Workflows
### Luigi Hello world
```bash
$ cd service_composition/demos/hello_world
$ python hello_world.py HelloWorldTask
```

### Twitter example
```bash
$ python -m service_composition.demos.twitter_example.luigi.twitter PrintCrawled --Geolocate-user=$CIME_USERNAME --Geolocate-password=$CIME_PASSWORD
```

### Service Composer with services
Twitter example but services objects that abstract each type of service are used instead of the actual code to run each one.

```bash
$ python -m service_composition.demos.twitter_example.luigi.composer_with_services PrintCrawled --Geolocate-user=$CIME_USERNAME --Geolocate-password=$CIME_PASSWORD
```

### Service Composer with tasks
Twitter example but now instead of creating luigi tasks, the pipeline is described with Task objects that run each service and are chained via array of dependencies.

```bash
$ python -m service_composition.demos.twitter_example.luigi.composer_with_tasks $CIME_USERNAME $CIME_PASSWORD
```

### Simple list map
Simple example applying functions to a list of numbers.

```bash
$ python -m service_composition.demos.composer_examples.simple_list_map
```

### Yaml parser
Function that parses a yaml composer file into an array of ServiceData in the pipeline order.

To test:
```bash
service_composition/yaml_parser $ python test_yaml_parser.py
```

### Command line parser 
Parse command line arguments, reading a composer file along with values for the variables specified in the file with "$".
Help argument (-h, --help) is available to see how it works.

```bash
$ python -m service_composition.demos.arg_parser.arg_parser
```

To run it with the test yaml file:
```bash
$ python -m service_composition.demos.arg_parser.arg_parser .\service_composition\yaml_parser\test_composer.yaml
```

### Composer
Read a yaml pipeline configuration file from the commandline, along with the arguments specified in it.
Then, run a luigi pipeline based on that configuration.

```
$ python -m service_composition.composer.composer .\data\composer\test_composer.yaml -USERNAME $CIME_USERNAME -PASSWORD $CIME_PASSWORD
```
