import pbclient

class PybossaWrapper:

    def __init__(self, endpoint, apikey):
        pbclient.set('endpoint', endpoint)
        pbclient.set('api_key', apikey)

    def get_projects(self):
        return pbclient.get_projects(last_id=0)

    def create_category(self, name, description):
        category = pbclient.create_category(name=name, description=description)
        return category

    def create_project(self, name, shortname, description):
        created = pbclient.create_project(name, shortname, description)
        project_id = created.id
        #replace the templates shortname with the actual shortname
        task_presenter = open('json_presenter.html').read().replace('[[shortname]]', shortname)
        #task_presenter=None
        project = pbclient.Project(data=dict(id=project_id, info=dict(task_presenter=task_presenter)))
        result = pbclient.update_project(project)
        return result

    def create_task(self, project_id, tweet):
        info=dict(tweet=tweet)
        task = pbclient.create_task(project_id=project_id, info=info)
        return task

    def create_tasks(self, project_id, tweets):
        return [create_task(project_id, tweet) for tweet in tweets]

    def delete_all_projects(self):
        projects = self.get_projects()
        for project in projects:
            pbclient.delete_project(project_id=project.id)


