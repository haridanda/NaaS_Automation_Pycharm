import json
import time

import pytest
import requests
from pytest_bdd import scenario, given, when , then

my_cookie = None
Uni_id = None

login = "/login"
workflow = "/workflow_engine/startJobWithOptions/LNAAS_CREATE_UNI_SL_V1"
mesh_path = "/inventory/v1/mesh/paths?aend=LABBRMCO&product=ETHERNET&numpaths=1&bandwidth=100&diversity=No&interface=Optical&protection=No&productType=simple_ethernet&lowLatency=No&dwdmOnly=No&metroLevel=2.0"
workflow_status = "/workflow_engine/getJobShallow/"
workflow_search = "/workflow_engine/tasks/search"

@pytest.fixture(scope="session")
def get_AP_token( naas_config, data_provider):
    login_url = naas_config.get_server("autopilot") + login
    print("AP Login URL",login_url)
    request_body = {"user": {"username": "ac71601", "password": "Mur@li$07#"}}
    headers = {"Content-Type" : "application/json"}
    response = requests.post(login_url, json=request_body, headers= headers, verify=False)
    cookies_dict = response.cookies.get_dict()
    with open("API_token.json", "w") as token:
        token.write(json.dumps(cookies_dict))
    return response

@given('login AutoPilot')
def test_login (get_AP_token):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print(cdict['token'])

#@pytest.fixture(scope="class")
def get_port_Aval_MESH( naas_config):
    get_mesh = naas_config.get_server("sasi") + mesh_path
    print("Sasi - Mesh URL", get_mesh)
    response = requests.get(get_mesh, verify=False)
    return response.json()

@when('validate Port avalibility')
def test_port_check_Mesh ( naas_config):
    global flag
    flag = False
    response = get_port_Aval_MESH(naas_config = naas_config)
    result = response['resources'][0]['pathElements'][0]['type']
    if result in ['ME', 'ENNI']:
        print("Result ;;",result)
        attributes = response['resources'][0]['pathElements'][0]['subElements'][0]['aendPort']['attributes'][0]
        if attributes['name'] == 'Class':
            assert attributes['value'] in ['Empty Slot', 'Physical']
            flag= True
    return flag

#@pytest.fixture(scope="class")
def post_Create_UNI( naas_config, data_provider):
    AP_start_job_url = naas_config.get_server("autopilot") + workflow
    print("AP UNI WF URL", AP_start_job_url)
    request_body = data_provider.get_nested_node(["naas", "uni", "create_uni_payload"])
    headers = data_provider.get_nested_node(["naas","requestHeaders"])
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    response = requests.post(AP_start_job_url, json=request_body, headers=headers, verify=False, cookies=cdict)
    response_json = response.json()
    global id
    id= response_json["_id"]
    return id

#@pytest.mark.skipif (flag = True)
def test_Create_UNI ( naas_config, data_provider):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print(cdict['token'])
    global id
    id = post_Create_UNI(naas_config= naas_config, data_provider= data_provider)
    AP_status_Url = naas_config.get_server("autopilot")+ workflow_status + id
    response = requests.get(AP_status_Url, verify=False, cookies=cdict)
    response_json = response.json()
    validate_status(response_json = response_json['tasks'], status='workflow_end', AP_status_Url= AP_status_Url,cookies=cdict )
    print(response_json["status"])
    print("UNI ID",id)

def validate_status(response_json, status, AP_status_Url, cookies):
    for key in response_json:
        #x = input("enter Value :")
        if key == status:
            print("{}: {}".format(status, response_json[key]['status']))
            if response_json[key]['status'] == 'complete':
                break
            else:
                time.sleep(60)
                response = requests.get(AP_status_Url, verify=False, cookies = cookies)
                response_json = response.json()
                validate_status(response_json['tasks'], status, AP_status_Url, cookies)

def fetch_id(dict, task='f33e'):
    for i in range(len(dict['results'])):
        if dict['results'][i]['job']['task'] == task:
            print(dict['results'][i]["_id"])

#@pytest.fixture(scope="class")
def get_uni_info( naas_config, data_provider):
    AP_get_job_info_url = naas_config.get_server("autopilot") + workflow_search
    print("AP UNI WF URL", AP_get_job_info_url)
    request_body = data_provider.get_nested_node(["naas", "uni", "task_search"])
    request_body['filter']['job._id'] = data_provider.get_nested_node(["naas", "uni","response_data",'job_id'])[0]
    headers = data_provider.get_nested_node(["naas","requestHeaders"])
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    response = requests.get(AP_get_job_info_url, json=request_body, headers=headers, verify=False, cookies=dict)
    response_json = response.json()
    id= response_json["_id"]
    global Uni_id
    Uni_id= id
    yield response.json()

def test_Validate_UNI(naas_config, data_provider):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    #id = 'ec7a110c60944746883e8507'
    #74904fdd4c6e4fa78319979a ec7a110c60944746883e8507
    AP_validate_Url = naas_config.get_server("autopilot") + workflow_search
    request_body = data_provider.get_nested_node(["naas", "validate_UNI"])
    request_body['filter']['job._id'] = id
    response = requests.post(AP_validate_Url, json=request_body, verify=False, cookies=dict)
    response_json = response.json()
    #print(response_json)
    input_list = ['asriServiceAlias', 'actId']
    flag = 0
    for each in response_json['results']:
        if each['job']['task'] == '1540':
            print("print...", each['job']['task'])
            flag =1
            if each['variables']['outgoing']['job_details']['status'] == 'complete':
                data = each['variables']['outgoing']['job_details']['data']
                print(data['response']['data'].keys())
                for item in input_list:
                    assert item in data['response']['data'].keys()
                    print(data['response']['data'][item])
            break
    assert flag == 1, "UNI create doesn't have 1540 task -- EXIT"






