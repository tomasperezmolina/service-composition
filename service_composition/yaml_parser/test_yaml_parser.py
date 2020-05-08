from yaml_parser import parse_composition, ServiceType

services = parse_composition('test_composer.yaml', {'PYFILE': 'get_tweets.py', 'ARG2': 7, 'USERNAME': 'myuser'}, print_debug=True)

crawler = services[0]
geolocation = services[1]
printer = services[2]

assert(crawler.type == ServiceType.PYTHON)
assert(crawler.name == 'TwitterCrawler')
assert(crawler.file == 'get_tweets.py')

assert(geolocation.type   == ServiceType.HTTP)
assert(geolocation.name   == 'Geolocation')
assert(geolocation.method == 'POST')
assert('text'     in geolocation.connection_args['translator']['schema'])
assert('username' in geolocation.connection_args['translator']['schema'])
assert(geolocation.connection_args['translator']['exclusive'] == True)

assert(printer.type == ServiceType.PYTHON)
assert(printer.name == 'Print')
assert(printer.file == 'print_it.py')
