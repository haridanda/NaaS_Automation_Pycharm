import json
result = open("newseach.json")
response_json = json.load(result)
input_list = ['asriServiceAlias', 'actId']
for each in response_json['results']:
    if each['job']['task'] == '1540':
        if each['variables']['outgoing']['job_details']['status'] == 'complete':
            data = each['variables']['outgoing']['job_details']['data']
            for item in input_list:
                assert item in data['response']['data'].keys()
                print(data['response']['data'][item])
"""
 input_list = ['asriServiceAlias', 'actId']
    for each in response_json['results']:
        if each['job']['task'] == '1540':
            if each['variables']['outgoing']['job_details']['status'] == 'complete':
                data = each['variables']['outgoing']['job_details']['data']
                for item in input_list:
                    assert item in data['response']['data'].keys()
                    print(data['response']['data'][item])
"""