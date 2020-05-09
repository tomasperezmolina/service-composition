from service_composition.pybossa.pybossa_wrapper import PybossaWrapper
import json
import os

CONFIG_PATH="../config/pybossa_config.json"
TEST_TWEET_PATH="../../../data/test_tweet.json"

config = None
with open(os.path.abspath(CONFIG_PATH), 'r') as config_f:
    config = json.load(config_f)


pybossa = PybossaWrapper(config['endpoint'], config['apikey'])

project = pybossa.create_project('Test project name', 'Test project shortname', 'Test project description', 'service_composition/pybossa/json_presenter.html')

def run(tweet):
    pybossa.create_task(project.id, tweet)
