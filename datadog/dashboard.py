import os
from datadog import initialize, api

options = {
    'api_key': os.environ.get('DD_API'),
    'app_key': os.environ.get('DD_APP'),
}

initialize(**options)

title = "My Timeboard 2"
description = "A new and improved timeboard!"
graphs =  [{
    "definition": {
      'aggregator': 'avg',
        "events": [],
        "requests": [
          {"q": "avg:system.mem.free{*} by {host} / ( avg:system.mem.usable{*} by {host} + avg:system.mem.free{*} by {host} )"}
        ],
    "viz": "timeseries"
    },
    "title": "Average Memory Free By Host"
}]
template_variables = [{
	"name": "host1",
	"prefix": "host",
	"default": "host:my-host"
}]
read_only = True

all_dash = api.Timeboard.get_all()
to_delete = [dash for dash in all_dash['dashes'] if dash['title'].endswith('DP_AUTO')]
for dash in to_delete:
  api.Timeboard.delete(dash['id'])

print api.Timeboard.create(title=title + ' - DP_AUTO', description=description, graphs=graphs, template_variables=template_variables, read_only=read_only)

print 'All Done'
