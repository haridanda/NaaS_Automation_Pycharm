import json

UNI_ID = '12Shbaew'

f = open('test-2.json')
naas_dict = json.load(f)
#with open("test-2.json", "r") as naas:
 #   naas_dict = json.loads(naas.read())
print(naas_dict)
naas_dict['naas']['uni']['task_search']['filter']['job._id'] = UNI_ID
print(naas_dict)