# Service composition prototype

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

## Workflows
### Luigi Hello world
```bash
$ cd service_composition/hello_world
$ python hello_world.py HelloWorldTask
```

### Twitter example
```bash
$ python -m service_composition.twitter_example.luigi.twitter PrintCrawled --Geolocate-user=$CIME_USERNAME --Geolocate-password=$CIME_PASSWORD
```

### Service Composer with services
Twitter example but services objects that abstract each type of service are used instead of the actual code to run each one.

```bash
$ python -m service_composition.twitter_example.luigi.composer_with_services PrintCrawled --Geolocate-user=$CIME_USERNAME --Geolocate-password=$CIME_PASSWORD
```

### Service Composer with tasks
Twitter example but now instead of creating luigi tasks, the pipeline is described with Task objects that run each service and are chained via array of dependencies.

```bash
$ python -m service_composition.twitter_example.luigi.composer_with_tasks $CIME_USERNAME $CIME_PASSWORD
```