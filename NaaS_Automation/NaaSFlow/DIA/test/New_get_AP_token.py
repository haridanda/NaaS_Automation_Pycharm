import json
import pytest
import requests
from pytest_bdd import given, when
import time

my_cookie = None
Uni_id = None
path = "//Users//haridanda//PycharmProjects//act//NaaS_Automation//NaaSFlow//DIA//test//Sample1.xls"
login = "/login"
workflow = "/workflow_engine/startJobWithOptions/LNAAS_CREATE_UNI_SL_V1"
mesh_path = "/inventory/v1/mesh/paths?aend=LABBRMCO&product=ETHERNET&numpaths=1&bandwidth=100&diversity=No&interface=Optical&protection=No&productType=simple_ethernet&lowLatency=No&dwdmOnly=No&metroLevel=2.0"
workflow_status = "/workflow_engine/getJobShallow/"
workflow_search = "/workflow_engine/tasks/search"

def update_counter(counter):
    return counter

def get_data(file):
    import xlrd
    wb1 = xlrd.open_workbook(file)
    ws = wb1.sheet_by_index(0)
    total_records = ws.nrows
    for i in range(1,total_records):
        sno = update_counter(i)
        input_dict = {}
        input_dict['sno'] = sno
        input_dict['Scenario'] = ws.cell_value(i, 1)
        input_dict['serviceType'] = ws.cell_value(i, 2)
        input_dict['aEndClli'] = ws.cell_value(i, 3)
        input_dict['interfaceType'] = ws.cell_value(i, 4)
        input_dict['uniType'] = ws.cell_value(i, 5)
        yield input_dict

def write_data(file,i,dict_output):
    import xlrd
    from xlutils.copy import copy
    rb = xlrd.open_workbook(file)
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    sheet.write(i, 0, dict_output['sno'])
    sheet.write(i, 7, dict_output['id'])
    sheet.write(i, 8, dict_output['actId'])
    sheet.write(i, 9, dict_output['asriServiceAlias'])
    wb.save(file)

@pytest.fixture(scope="session")
def get_AP_token( naas_config, data_provider):
    login_url = naas_config.get_server("autopilot") + login
    print("AP Login URL",login_url)
    request_body = {"user": {"username": "ac71601", "password": "Mur@li$07#"}}
    headers = {"Content-Type" : "application/json"}
    response = requests.post(login_url, json=request_body, headers= headers, verify=False)
    print(response.text)
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

def test_post_Create_UNI( naas_config, data_provider, input_dict):
    AP_start_job_url = naas_config.get_server("autopilot") + workflow
    print("AP UNI WF URL", AP_start_job_url)
    request_body = data_provider.get_nested_node(["naas", "uni", "create_uni_payload"])
    request_body['options']['variables']['requestPayload']['serviceType'] = input_dict['serviceType']
    request_body['options']['variables']['requestPayload']['aEndClli'] = input_dict['aEndClli']
    request_body['options']['variables']['requestPayload']['interfaceType'] = input_dict['interfaceType']
    request_body['options']['variables']['requestPayload']['uniType'] = input_dict['uniType']
    #request_body['options']['variables']['requestPayload']['failFast'] = input_dict['failFast']
    print(request_body)
    headers = data_provider.get_nested_node(["naas","requestHeaders"])
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    response = requests.post(AP_start_job_url, json=request_body, headers=headers, verify=False, cookies=cdict)
    response_json = response.json()
    global id
    id= response_json["_id"]
    return id

#@pytest.mark.skipif (flag = True)
@pytest.mark.parametrize("input_dict", get_data(file = path))
def test_Create_UNI ( naas_config, data_provider, input_dict):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print(cdict['token'])
    global id
    id = test_post_Create_UNI(naas_config= naas_config, data_provider= data_provider, input_dict= input_dict)
    #Get call on UNI ID
    AP_status_Url = naas_config.get_server("autopilot")+ workflow_status + id
    response = requests.get(AP_status_Url, verify=False, cookies=cdict)
    response_json = response.json()
    validate_status(response_json = response_json['tasks'], status='workflow_end', AP_status_Url= AP_status_Url,cookies=cdict )
    dict_output= {}
    dict_output['sno'] = input_dict['sno']
    print(response_json["status"])
    print("UNI ID",id)
    dict_output['id'] = id
    dict_output_final = test_Validate_UNI(naas_config, data_provider,dict_output)
    write_data(path, input_dict['sno'], dict_output=dict_output_final)

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

def test_Validate_UNI(naas_config, data_provider, dict_output):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    #id = 'a3a6561efb74465b986a0afb'
    #74904fdd4c6e4fa78319979a ec7a110c60944746883e8507
    AP_validate_Url = naas_config.get_server("autopilot") + workflow_search
    request_body = data_provider.get_nested_node(["naas", "validate_UNI"])
    request_body['filter']['job._id'] = id
    response = requests.post(AP_validate_Url, json=request_body, verify=False, cookies=dict)
    response_json = response.json()
    input_list = ['asriServiceAlias', 'actId']
    flag = 0
    for each in response_json['results']:
        if each['job']['task'] == '1540':
            print("print...", each['job']['task'])
            flag =1
            job_details = each['variables']['outgoing']['job_details']
            if job_details['status'] == 'complete':
                if 'error' in job_details.keys():
                    print("JOB Failed...!")
                    print("Error status CODE :", job_details['error']['data']['status'])
                    print("Error Status Message :", job_details['error']['data']['errorMessage'])
                else:
                    #dict_output={}
                    data = job_details['data']
                    print(data['response']['data'].keys())
                    for item in input_list:
                        assert item in data['response']['data'].keys()
                        print(data['response']['data'][item])
                        dict_output[item] = data['response']['data'][item]
            break

    assert flag == 1, "UNI create doesn't have 1540 task -- EXIT"
    print(dict_output)
    return dict_output




