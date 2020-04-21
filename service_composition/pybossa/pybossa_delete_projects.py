from pybossa_wrapper import PybossaWrapper
import json
import os

CONFIG_PATH="../../../config/pybossa_config.json"

config = None
with open(os.path.abspath(CONFIG_PATH), 'r') as config_f:
    config = json.load(config_f)

pybossa = PybossaWrapper(config['endpoint'], config['apikey'])

pybossa.delete_all_projects()

