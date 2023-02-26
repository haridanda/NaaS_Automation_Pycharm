import json
import pytest
import requests
from pytest_bdd import given, when
import time
from conf.data import constant




my_cookie = None
Uni_id = None
path = "//Users//haridanda//PycharmProjects//act//NaaS_Automation//NaaSFlow//DIA//test//Sample1.xls"
login = "/login"
UNI_workflow = "/workflow_engine/startJobWithOptions/LNAAS_CREATE_UNI_SL_V1"
skinny_workflow = "/workflow_engine/startJobWithOptions/Create_Resource_ASRI_AL"
SL_workflow = "/workflow_engine/startJobWithOptions/LNAAS_CREATE_DIA_SERVICE_SL_V1"
mesh_path = "/inventory/v1/mesh/paths?aend=LABBRMCO&product=ETHERNET&numpaths=1&bandwidth=100&diversity=No&interface=Optical&protection=No&productType=simple_ethernet&lowLatency=No&dwdmOnly=No&metroLevel=2.0"
workflow_status = "/workflow_engine/getJobShallow/"
workflow_search = "/workflow_engine/tasks/search"
sasi_asri = "/wrappers/asri/naming/generate"
assign_ip ="/wrappers/nisws/ipAssign"

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
        input_dict['ASRI_ID'] = ws.cell_value(i, 9)
       # input_dict['service_alias'] = ws.cell_value(i, 11)
       # input_dict['IP_Assign'] = ws.cell_value(i, 12)
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
    #sheet.write(i,13, dict_output['pathActTransactionId'])
    #sheet.write(i, 14, dict_output['pathServiceAlias'])
    #sheet.write(i, 15, dict_output['actId'])
    #sheet.write(i, 16, dict_output['asriServiceAlias'])
    #sheet.write(i, 11, service_alias['service_alias'])
    wb.save(file)


@pytest.fixture(scope="session")
def get_AP_token( naas_config, data_provider):
    login_url = naas_config.get_server("autopilot") + login
    print("AP Login URL",login_url)
    request_body = {"user": {"username": constant.user, "password":constant.password}}
    print(request_body)
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

def post_Create_UNI( naas_config, data_provider, input_dict):
    AP_start_job_url = naas_config.get_server("autopilot") + UNI_workflow
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
def test_Create_AUNI_SL ( naas_config, data_provider, input_dict):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print(cdict['token'])
    global id
    print("input idct", input_dict)
    id = post_Create_UNI(naas_config= naas_config, data_provider= data_provider, input_dict= input_dict)
    #Get call on UNI ID
    #id = '93986e931cc74eab851651fe'
    AP_status_Url = naas_config.get_server("autopilot")+ workflow_status + id
    response = requests.get(AP_status_Url, verify=False, cookies=cdict)
    response_json = response.json()
    validate_status(response_json = response_json['tasks'], status='workflow_end', AP_status_Url= AP_status_Url,cookies=cdict )
    dict_output= {}
    dict_output['sno'] = input_dict['sno']
    print(response_json["status"])
    print("UNI ID",id)
    dict_output['id'] = id
    dict_output_final = Validate_UNI(naas_config, data_provider,dict_output)
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

def Validate_UNI(naas_config, data_provider, dict_output):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    #id = '93986e931cc74eab851651fe'
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

def test_generate_service_alias( naas_config, data_provider):
    generate_servias_alias = naas_config.get_server("sasi-wrap") + sasi_asri
    request_body = data_provider.get_nested_node(["naas", "generate_alias"])
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    response = requests.put(generate_servias_alias, json= request_body, headers=headers, verify=False)
    #print("generate service allias", response.text)
    response_json = response.json()
    global service_alias
    service_alias = response_json["generatedName"]
    #print('service_alias:', dict_output)
    #return service_alias
    print(service_alias)
    return service_alias

def test_Create_skinny( naas_config, data_provider):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print(cdict['token'])
    AP_create_skinny= naas_config.get_server("autopilot") + skinny_workflow
    request_body = data_provider.get_nested_node(["naas", "Create_skinny"])
    request_body['options']['variables']['resourceData']['name'] = service_alias
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    print(request_body)
    response = requests.post(AP_create_skinny, json= request_body, headers=headers, verify=False, cookies=cdict)
    response_json = response.json()
    return response_json

def test_assign_IP( naas_config, data_provider):
    get_servias_alias = naas_config.get_server("sasi-wrap") + assign_ip
    request_body = data_provider.get_nested_node(["naas", "assign_IP"])
    request_body['circuitId']= service_alias
    print(request_body)
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    response = requests.post(get_servias_alias, json= request_body, headers=headers, verify=False)
    print("generate service allias", response.text)
    response_json = response.json()
    global cidrRange
    cidrRange = response_json["ipBlock"][0]["cidrRange"]
    print('cidrRange:', cidrRange)

@pytest.mark.parametrize("input_dict", get_data(file = path))
def Create_DIA_Service_SL(naas_config, data_provider, input_dict):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print(cdict['token'])
    print("input dict02: ", input_dict)
    AP_start_job_url = naas_config.get_server("autopilot") + SL_workflow
    print("AP UNI WF URL", AP_start_job_url)
    request_body = data_provider.get_nested_node(["naas", "DIA_SL", "Create_DIA_SL_Payload"])
    request_body['options']['variables']['requestPayload']['productSubType'] = "fiber_plus"
    request_body['options']['variables']['requestPayload']['uniServiceAlias'] = input_dict['ASRI_ID']
    request_body['options']['variables']['requestPayload']['serviceAlias'] = service_alias
    request_body['options']['variables']['requestPayload']['wanIPAddressBlocks'][0]['ipAddressBlock'] = cidrRange
    # request_body['options']['variables']['requestPayload']['failFast'] = input_dict['failFast']
    print(request_body)
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    response = requests.post(AP_start_job_url, json=request_body, headers=headers, verify=False, cookies=cdict)
    response_json = response.json()
    global SL_id
    SL_id = response_json["_id"]
    print("SL ID ", SL_id)
    return SL_id

@pytest.mark.parametrize("input_dict", get_data(file = path))
def test_Create_Service_SL ( naas_config, data_provider, input_dict):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print(cdict['token'])
    global SL_ID
    SL_ID = Create_DIA_Service_SL(naas_config= naas_config, data_provider= data_provider, input_dict= input_dict)
    #Get call on UNI ID
    #SL_ID = '6971e7a54cd0475a8de003ef'
    AP_status_Url = naas_config.get_server("autopilot")+ workflow_status + SL_ID
    response = requests.get(AP_status_Url, verify=False, cookies=cdict)
    response_json = response.json()
    validate_status(response_json = response_json['tasks'], status='workflow_end', AP_status_Url= AP_status_Url,cookies=cdict )
    dict_output= {}
    dict_output['sno'] = input_dict['sno']
    print(response_json["status"])
    print("Service ID",SL_ID)
    dict_output['id'] = SL_ID
    dict_output_final = Validate_SL(naas_config, data_provider,dict_output)
    write_data(path, input_dict['sno'], dict_output=dict_output_final)

def Validate_SL_Zero(naas_config, data_provider, dict_output):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    id = '6971e7a54cd0475a8de003ef'
    #ba97bfff9d7847d385591aaa ec7a110c60944746883e8507
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


def Validate_SL(naas_config, data_provider, dict_output):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    #id = "6971e7a54cd0475a8de003ef"
    #74904fdd4c6e4fa78319979a ec7a110c60944746883e8507
    AP_validate_Url = naas_config.get_server("autopilot") + workflow_search
    request_body = data_provider.get_nested_node(["naas", "validate_UNI"])
    request_body['filter']['job._id'] = SL_ID
    print(request_body)
    response = requests.post(AP_validate_Url, json=request_body, verify=False, cookies=dict)
    response_json = response.json()
    input_list = ['asriServiceAlias', 'actId', 'pathServiceAlias', 'pathActTransactionId']
    flag = 0
    for each in response_json['results']:
        #c5b , 1f19,
        if each['job']['task'] == '1f19':
            print("print...", each['job']['task'])
            flag =1
            job_details = each['variables']['outgoing']['job_details']['data']['response']
            if job_details['status'] == 'success':
                    data = job_details['data']
                    print(data.keys())
                    for item in input_list:
                        assert item in data.keys()
                        print(data[item])
                        dict_output[item] = data[item]

            break
        else:
            print("JOB Failed...!")
            print("Error status CODE :")
            print("Error Status Message :")

    assert flag == 1, "Service create doesn't have 6142 task -- EXIT"
    print(dict_output)
    return dict_output






