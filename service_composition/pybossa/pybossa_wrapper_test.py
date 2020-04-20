from pybossa_wrapper import PybossaWrapper
import json
import os

CONFIG_PATH="../../config/pybossa_config.json"
TEST_TWEET_PATH="../../data/test_tweet.json"

config = None
with open(os.path.abspath(CONFIG_PATH), 'r') as config_f:
    config = json.load(config_f)

#load a test tweet from file
test_tweet = None
tweet_path = os.path.abspath(TEST_TWEET_PATH)
if (os.path.exists(tweet_path)):
    test_tweet = json.loads(open(tweet_path).read())
else:
    test_tweet = dict(text="test tweet", user="user123")

#initialize the pybossa client
pybossa = PybossaWrapper(config['endpoint'], config['apikey'])

#reset projects
pybossa.delete_all_projects()

print("-- initial state --")
print(pybossa.get_projects())

#create a project with two tasks
project = pybossa.create_project('Test project name', 'Test project shortname', 'Test project description')
pybossa.create_task(project.id, test_tweet)
pybossa.create_task(project.id, test_tweet)

print("-- final state --")
print(pybossa.get_projects())


