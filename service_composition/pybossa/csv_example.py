import json, ast, csv, argparse, sys
from app import *

parser = argparse.ArgumentParser(description='Create a new event and import tasks from a CSV file')
parser.add_argument('action', choices=['create', 'delete'], default='create',
                   help='The action to be performed, which can be: create || delete')
parser.add_argument('categoryName', type=str,
                   help='The name of the event to be created')
parser.add_argument('--csvFile', type=str,
                   help='The name of CSV file containing the data to create tasks')
parser.add_argument('--lat', type=float,
                   help='The latitude of the disaster area')
parser.add_argument('--lon', type=float,
                   help='The longitude of the disaster area')
parser.add_argument('--place', type=str,
                   help='The name of the disaster area')

args = parser.parse_args()

if args.action == 'create' and args.csvFile is None:
    parser.error('You need to provide a CSV file to import tasks')

action = args.action
category_name = args.categoryName
csv_file = args.csvFile
lat = args.lat
lon = args.lon
place = args.place

def create_two_projects(category):
    """Create two projects for event."""
    projects = ['twitter', 'geolocation']
    for p in projects:
        slug = "%s-%s" % (category.short_name, p)
        project_create = pbclient.create_project(name=slug, short_name=slug, description=slug)
        print(project_create)
        project_id = project_create.id
        print('Created project: %s' % project_id)
        if p == 'twitter':
            webhook = settings.WEBHOOK_CSV
        else:
            webhook = ""
        project = pbclient.Project(data=dict(id=project_id, category_id=category.id, webhook=webhook, info=dict(task_presenter=p)))
        res = pbclient.update_project(project)
        print(res)
        if p == 'twitter':
            create_tasks(project_id, category.id)

def create_tasks(project_id, category_id):
    with open(csv_file, 'rb') as f:
        reader = csv.DictReader(f)
        print("Creating project tasks...")
        try:
            for row in reader:
                if bool('image' in row and row['image'] and row['image'].strip() and row['image'] != 'null'):
                    info=dict(importer='polling', url=row['tweetURL'], text=row['message'], author=row['userName'], media=[row['image']],
                        publication_date=row['createdAt'], date_created=row['createdAt'], place=place if place is not None else None, latitude=lat if lat is not None else None,
                        longitude=lon if lon is not None else None, language=row['language'] if 'language' in row else "",
                        link=[row['link'] if 'link' in row else ""], tags=[row['tags'] if 'tags' in row else ""], source='twitter', type='tweet', event=category_id)
                    n_answers = settings.REDUNDANCY_CSV
                    task = pbclient.create_task(project_id=project_id, info=info, n_answers=n_answers)
                    sys.stdout.write('.')
                    sys.stdout.flush()
        except csv.Error as e:
                sys.exit('ERROR in file %s, line %d: %s' % (csv_file, reader.line_num, e))

if action == 'create':
    print("Creating category: %s" % category_name)

    result = pbclient.create_category(name=category_name, description="The %s event" % category_name)

    try:
            json.dumps(result)

    except:
            print('Category "%s" was created' % category_name)
            category = result
            event_id = category.id

    else:
            print('Category "%s" already exists, recovering its id' % category_name)
            category = pbclient.find_category(name=category_name)[0]
            event_id = category.id

    projects = pbclient.find_project(category_id=event_id, all=1)
    print("project size: %s" % len(projects))
    projects = [project for project in projects if
            project.info['task_presenter'] in ['twitter',
                                              'geolocation']]
    if len(projects) == 0:
        print("Creating 2 projects for category '%s" % category)
        create_two_projects(category)
    else:
        print("This category already contains projects, please delete them first or use a different category name")
        #for project in projects:
            # if project.info['task_presenter'] == 'geolocation':
            #     create_tasks(project.id, project.info['task_presenter'],
            #                  event['id'])
            #create_tasks(project.id, project.info['task_presenter'], event['id'])

if action == 'delete':
    print("Deleting category '%s' and associated projects" % category_name)
    category_list = pbclient.find_category(name=category_name)
    if len(category_list) > 0:
        category = category_list[0]
        category_projects = pbclient.find_project(category_id=category.id, all=1)
        if len(category_projects) > 0:
            for project in category_projects:
                sys.stdout.write('.')
                sys.stdout.flush()
                project_tasks = pbclient.find_tasks(project_id=project.id, all=1)
                if len(project_tasks) > 0:
                    for task in project_tasks:
                        sys.stdout.write('.')
                        sys.stdout.flush()
                        pbclient.delete_task(task_id=task.id)
                pbclient.delete_project(project_id=project.id)
        pbclient.delete_category(category_id=category.id)
    else:
        print("Category '%s' does not exist!" % category_name)
