from service_composition.pybossa.pybossa_wrapper import PybossaWrapper
import json
import os

CONFIG_PATH="config/pybossa_config.json"

config = None
with open(os.path.abspath(CONFIG_PATH), 'r') as config_f:
    config = json.load(config_f)

pybossa = PybossaWrapper(config['endpoint'], config['apikey'])

project = None

def run(tweet, **kwargs):
    global project
    if project is None:
        project = pybossa.create_project(kwargs["project_name"], kwargs["project_short_name"], kwargs["project_description"], 'service_composition/pybossa/json_presenter.html', title=kwargs["question"])

    pybossa.create_task(project.id, tweet)
