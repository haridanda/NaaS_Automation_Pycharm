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
    request_body = {"user": {"username": "ac71601", "password": "ac71601"}}
    headers = {"Content-Type" : "application/json"}
    response = requests.post(login_url, json=request_body, headers= headers, verify=False)
    print("Response :: ", response)
    cookies_dict = response.cookies.get_dict()
    with open("API_token.json", "w") as token:
        token.write(json.dumps(cookies_dict))
    print(type(response.cookies))
    return response

@given('login AutoPilot')
def test_login (get_AP_token):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    print(dict['token'])
    #naas_test.is_http_200(response=get_AP_token.json())
    print("Logged Successfully")

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
        #assert get_port_Aval_MESH['resources'][0]['pathElements'][0]['subElements'][0]['aendPort']['name'] is not None
        print("Result ;;",result)
        attributes = response['resources'][0]['pathElements'][0]['subElements'][0]['aendPort']['attributes'][0]
        if attributes['name'] == 'Class':
            print(attributes['value'])
            assert attributes['value'] in ['Empty Slot']
            flag= True
    print(flag)
    return flag


#@pytest.fixture(scope="class")
def post_Create_UNI( naas_config, data_provider):
    AP_start_job_url = naas_config.get_server("autopilot") + workflow
    print("AP UNI WF URL", AP_start_job_url)
    request_body = data_provider.get_nested_node(["naas", "uni", "create_uni_payload"])
    #print("Request Body", request_body)
    headers = data_provider.get_nested_node(["naas","requestHeaders"])
    #print("headers", headers)
    #global my_cookie
    #my_cookie = get_AP_token.cookies
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    #print(dict)
    #print(dict['token'])
    #response = requests.post(AP_start_job_url, json=request_body, headers=headers, verify=False)
    response = requests.post(AP_start_job_url, json=request_body, headers=headers, verify=False, cookies=dict)
    #print(response.text)
    #print(response)
    response_json = response.json()
    #print("UNI Resposne ",response_json)
    global id
    id= response_json["_id"]
    print(id)
    #with open("response.json", "w") as UNI_ID:
     #   UNI_ID.write(response.json())
    #Uni_id= id
    return id
    #return id, my_cookie

#TODo - JOB Shallow - validate list[workflow_end] = "status": "complete",
#TODO - Job Search task :: list[job][task] = 1540, then list[variables][outgoing][job_details][data][response] == status = success & get [data] [asriServiceAlias] & [actId]
#TODO - Save the asriServiceAlias & actId

def fetch_id(dict, task='f33e'):
    print(dict['results'])
    for i in range(len(dict['results'])):
        print(dict['results'][i]['job']['task'])
        if dict['results'][i]['job']['task'] == task:
            print(dict['results'][i]["_id"])

#@pytest.fixture(scope="class")
def get_uni_info( naas_config, data_provider):
    AP_get_job_info_url = naas_config.get_server("autopilot") + workflow_search
    print("AP UNI WF URL", AP_get_job_info_url)
    request_body = data_provider.get_nested_node(["naas", "uni", "task_search"])
    request_body['filter']['job._id'] = data_provider.get_nested_node(["naas", "uni","response_data",'job_id'])[0]
   # print("request Body", request_body)
    headers = data_provider.get_nested_node(["naas","requestHeaders"])
    print("headers", headers)
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    print(dict['token'])
    response = requests.get(AP_get_job_info_url, json=request_body, headers=headers, verify=False, cookies=dict)
    print(response.text)
    response_json = response.json()
    id= response_json["_id"]
    print(id)
    global Uni_id
    Uni_id= id
    yield response.json()
    #return id, my_cookie


@pytest.mark.skipif (flag = False)
@then('create UNI')
def test_Create_UNI ( naas_config, data_provider):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    print(dict['token'])
    id = post_Create_UNI(naas_config= naas_config, data_provider= data_provider)
    #naas_test.is_http_200(post_Create_UNI)
    #if flag == True:
    print(flag)
    print("success")
    print("ID", id)
    ## Get end status
    AP_status_Url = naas_config.get_server("autopilot")+ workflow_status + id
    print(AP_status_Url)
    response = requests.get(AP_status_Url, verify=False, cookies=dict)
    #print("get response on status",response.json())
    response_json = response.json()
    print(response_json["status"])

    def validate_status(response_json, status):
        print("Enterned Validate_status")
        for key in response_json:
            print("Printing", key)
            if key == status:
                print("{}: {}".format(status, response_json[key]))
                if response_json[key] == 'complete':
                    break
                    return
                else:
                    time.sleep(10)
                    response = requests.get(AP_status_Url, verify=False, cookies=dict)
                    response_json = response.json()
                    validate_status(response_json, status)

    validate_status(response_json, 'status')

@then('Validate UNI')
def test_Validate_UNI(naas_config, data_provider):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    print(dict['token'])
    AP_validate_Url = naas_config.get_server("autopilot") + workflow_search
    print(AP_validate_Url)
    request_body = {
    "filter": {
      "job._id": "438ec0f6d3c44de9a8ee3f2f"
    },
    "options": {}
  }
    response = requests.post(AP_validate_Url, request_body, verify=False, cookies=dict)
    return response.json()
    input_list = ['asriServiceAlias', 'actId']
    for each in results:
        print(each['job']['task'])
        if each['job']['task'] == '1540':
            if each['variables']['outgoing']['job_details']['status'] == 'complete':
                data = each['variables']['outgoing']['job_details']['data']
                print(data['response']['data'].keys())
                assert input_list in data['response']['data'].keys()
                print(data['response']['data'][input_list][0])
                print(data['response']['data'][input_list][1])






    """
    import time
    time.sleep(15)
    response = requests.get(AP_status_Url, verify=False, cookies=dict)
    #print("get response on status", response.json())
    response_json = response.json()
    print("Second run",response_json["status"])

    # TODO  Implement Loop/Recursive function

    import time
    time.sleep(15)
    response = requests.get(AP_status_Url, verify=False, cookies=dict)
    # print("get response on status", response.json())
    response_json = response.json()
    print("Third run", response_json["status"])

    ## get job info
    print("Get job url info searhc")
    AP_task_job_url = naas_config.get_server("autopilot") + workflow_search
    request_body = data_provider.get_nested_node(["naas", "uni", "Request_Body"])
    #print(request_body)
    response = requests.post(AP_task_job_url, json=request_body, verify=False, cookies=dict)
    #print(response.json())
    fetch_id(dict = response.json())
"""

@pytest.mark.skipif (flag = False)
@then('get uni info')
def test_get_UNI_Job_info (naas_config, data_provider):
    """
    AP_task_job_url = naas_config.get_server("autopilot") + workflow_search
    print(AP_task_job_url)
    request_body = data_provider.get_nested_node(["naas", "uni", "Request_Body"])
    print(request_body)
    print(id)
    """
    print("success")
