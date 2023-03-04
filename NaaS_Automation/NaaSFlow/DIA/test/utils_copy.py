from random import randint
import requests
from NaaS_Automation.NaaSFlow.DIA.test.constants import *
import time
from conf.data import constant
import yaml


def update_counter(counter):
    return counter


def get_data(file):
    import xlrd
    wb1 = xlrd.open_workbook(file)
    ws = wb1.sheet_by_index(0)
    total_records = ws.nrows
    for i in range(1, total_records):
        sno = update_counter(i)
        input_dict = {}
        input_dict['sno'] = sno
        input_dict['Scenario'] = ws.cell_value(i, 1)
        input_dict['serviceType'] = ws.cell_value(i, 2)
        input_dict['aEndClli'] = ws.cell_value(i, 3)
        input_dict['interfaceType'] = ws.cell_value(i, 4)
        input_dict['uniType'] = ws.cell_value(i, 5)
        yield input_dict


def get_port_Aval_MESH(naas_config):
    get_mesh = naas_config.get_server("sasi") + mesh_path
    print("\n ===================== Mesh - PORT Avalibility Check ===========================================")
    print("Sasi - Mesh URL", get_mesh)
    response = requests.get(get_mesh, verify=False)
    return response.json()


import json


def get_cookies():
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    return cdict


def write_data_UNI_SL(file, i, dict_output):
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


def write_data_Service_SL(file, i, dict_output):
    import xlrd
    from xlutils.copy import copy
    rb = xlrd.open_workbook(file)
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    sheet.write(i, 13, dict_output['pathActTransactionId'])
    sheet.write(i, 14, dict_output['pathServiceAlias'])
    sheet.write(i, 15, dict_output['actId'])
    sheet.write(i, 16, dict_output['asriServiceAlias'])
    # sheet.write(i, 11, service_alias['service_alias'])
    wb.save(file)


# @pytest.fixture(scope="session")
def get_AP_token(naas_config, data_provider):
    login_url = naas_config.get_server("autopilot") + login
    print("AP Login URL", login_url)
    request_body = {"user": {"username": constant.user, "password": constant.password}}
    print(request_body)
    headers = {"Content-Type": "application/json"}
    response = requests.post(login_url, json=request_body, headers=headers, verify=False)
    print(response.text)
    cookies_dict = response.cookies.get_dict()
    with open("API_token.json", "w") as token:
        token.write(json.dumps(cookies_dict))
    return response


def post_Create_UNI(PCID, naas_config, data_provider, input_dict, update_response_id, scenario_index  ):
    print("\n   ===================== Create Port - Autopilot  ===========================================")
    AP_start_job_url = naas_config.get_server("autopilot") + UNI_workflow
    print("input data 01 ", input_dict)
    print("AP UNI WF URL", AP_start_job_url)
    request_body = data_provider.get_nested_node(["naas", "uni", "create_uni_payload"])
    CID = request_body['options']['variables']['requestPayload']['parentCorrelationId']
    request_body['options']['variables']['requestPayload']['parentCorrelationId'] = CID.replace("PARENTCID", PCID)
    global UNI_PCID
    UNI_PCID = request_body['options']['variables']['requestPayload']['parentCorrelationId']
    request_body['options']['variables']['requestPayload']['serviceType'] = input_dict["uni_serviceType"]
    request_body['options']['variables']['requestPayload']['aEndClli'] = input_dict["aEndcilli"]
    request_body['options']['variables']['requestPayload']['portSpeed'] = input_dict["uni_Port_speed"]
    request_body['options']['variables']['requestPayload']['uniType'] = input_dict["uni_Type"]
    request_body['options']['variables']['requestPayload']['serviceOrderNumber'] = PCID
    request_body['options']['variables']['requestPayload']['interfaceType'] = input_dict["uni_interface_Type"]
    request_body['options']['variables']['requestPayload']['failFast'] = input_dict["fail_fast"]

    print("Request Payload ::", request_body)
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    response = requests.post(AP_start_job_url, json=request_body, headers=headers, verify=False, cookies=cdict)
    response_json = response.json()
    global id
    id = response_json["_id"]
    response_id = id
    print("resposne UNI ID", response_id)

    # Load UNI ID  to Yaml file
    update_response_id(scenario_index, response_id)
    print("===================== Create Port - Autopilot  ===========================================")
    return id


def validate_status(response_json, status, AP_status_Url, cookies):
    for key in response_json:
        if key == status:
            print("{}: {}".format(status, response_json[key]['status']))
            if response_json[key]['status'] == 'complete':
                print(
                    "===================== Validate Job Status - Completed  ===========================================")
                break

            else:
                # print( "===================== Validate UNI Job Status Port - IN Progress  ===========================================")
                time.sleep(60)
                response = requests.get(AP_status_Url, verify=False, cookies=cookies)
                response_json = response.json()
                validate_status(response_json['tasks'], status, AP_status_Url, cookies)


def Validate_UNI(naas_config, data_provider,UNI_ID, dict_output, update_UNI_response, scenario_index):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    print("===================== Get UNI INFO - Autopilot  ===========================================")
    AP_validate_Url = naas_config.get_server("autopilot") + workflow_search
    request_body = data_provider.get_nested_node(["naas", "validate_UNI"])
    request_body['filter']['job._id'] = UNI_ID
    #request_body['filter']['job._id'] = input_dict["UNI_JobID"]
    response = requests.post(AP_validate_Url, json=request_body, verify=False, cookies=dict)
    response_json = response.json()
    input_list = ['asriServiceAlias', 'actId']
    flag = 0
    for each in response_json['results']:
        if each['job']['task'] == '1540':
            # print("print...", each['job']['task'])
            flag = 1
            job_details = each['variables']['outgoing']['job_details']
            if job_details['status'] == 'complete':
                if 'error' in job_details.keys():
                    print("JOB Failed...!")
                    print("Error status CODE :", job_details['error']['data']['status'])
                    print("Error Status Message :", job_details['error']['data']['errorMessage'])
                else:
                    # dict_output={}
                    data = job_details['data']
                    # print(data['response']['data'].keys())
                    for item in input_list:
                        print("UNI Data",data['response']['data'])
                        assert item in data['response']['data'].keys()

                        # print(data['response']['data'][item])
                        dict_output[item] = data['response']['data'][item]
            break

    assert flag == 1, "UNI create doesn't have 1540 task -- EXIT"
    # print(dict_output)
    print("===================== Get UNI INFO - Autopilot  ===========================================")
    print("UNI Response out put", dict_output)
    service_allias = dict_output['asriServiceAlias']
    act_id = dict_output['actId']
    # Load UNI ID  to Yaml file
    update_UNI_response(scenario_index, service_allias, act_id)
    return dict_output


def generate_service_alias(naas_config, data_provider):
    print("===================== Generate ASRI Service Allias - Autopilot  ===========================================")
    generate_servias_alias = naas_config.get_server("sasi-wrap") + sasi_asri
    request_body = data_provider.get_nested_node(["naas", "generate_alias"])
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    response = requests.put(generate_servias_alias, json=request_body, headers=headers, verify=False)
    response_json = response.json()
    global service_alias
    service_alias = response_json["generatedName"]
    print("Generated Service Alias", service_alias)
    print("===================== Generate Service Allias - Autopilot  ===========================================")
    return service_alias


def Create_skinny(naas_config, data_provider):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    # print(cdict['token'])
    print(
        "===================== Create Skinny Service Allias in ASRI - Autopilot  ===========================================")
    AP_create_skinny = naas_config.get_server("autopilot") + skinny_workflow
    request_body = data_provider.get_nested_node(["naas", "Create_skinny"])
    request_body['options']['variables']['resourceData']['name'] = service_alias
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    print("Request body", request_body)
    response = requests.post(AP_create_skinny, json=request_body, headers=headers, verify=False, cookies=cdict)
    print(response.status_code)
    response_json = response.json()
    print(
        "===================== Create Skinny Service Allias in ASRI - Autopilot  ===========================================")
    return response_json


def assign_IP(naas_config, data_provider):
    print("===================== Assign IP - Autopilot  ===========================================")
    get_servias_alias = naas_config.get_server("sasi-wrap") + assign_ip
    request_body = data_provider.get_nested_node(["naas", "assign_IP"])
    request_body['circuitId'] = service_alias
    print("Request Body", request_body)
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    response = requests.post(get_servias_alias, json=request_body, headers=headers, verify=False)
    print("generate service allias", response.text)
    response_json = response.json()
    global cidrRange
    cidrRange = response_json["ipBlock"][0]["cidrRange"]
    print('cidrRange:', cidrRange)
    print("===================== Assign IP - Autopilot  ===========================================")


def Create_DIA_Service_SL(PCID, naas_config, data_provider, input_dict):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print("===================== Create Service SL - Autopilot  ===========================================")
    print("input dict02: ", input_dict)
    AP_start_job_url = naas_config.get_server("autopilot") + SL_workflow
    print("AP UNI WF URL", AP_start_job_url)
    request_body = data_provider.get_nested_node(["naas", "DIA_SL", "Create_DIA_SL_Payload"])
    CID = request_body['options']['variables']['requestPayload']['parentCorrelationId']
    request_body['options']['variables']['requestPayload']['parentCorrelationId'] = CID.replace("PARENTCID", PCID)
    global Service_PCID
    Service_PCID = request_body['options']['variables']['requestPayload']['parentCorrelationId']
    request_body['options']['variables']['requestPayload']['productSubType'] = "fiber_plus"
    request_body['options']['variables']['requestPayload']['uniServiceAlias'] = input_dict['asriServiceAlias']
    request_body['options']['variables']['requestPayload']['serviceAlias'] = service_alias
    request_body['options']['variables']['requestPayload']['wanIPAddressBlocks'][0]['ipAddressBlock'] = cidrRange
    print("Request Body For Service SL", request_body)
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    response = requests.post(AP_start_job_url, json=request_body, headers=headers, verify=False, cookies=cdict)
    response_json = response.json()
    global SL_id
    SL_id = response_json["_id"]
    print("SL ID ", SL_id)
    print("===================== Create Service SL - Autopilot  ===========================================")
    return SL_id


def Create_Service_SL(PCID, naas_config, data_provider, input_dict, i):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    global SL_ID
    SL_ID = Create_DIA_Service_SL(PCID, naas_config=naas_config, data_provider=data_provider, input_dict=input_dict)
    # Get call on UNI ID
    AP_status_Url = naas_config.get_server("autopilot") + workflow_status + SL_ID
    response = requests.get(AP_status_Url, verify=False, cookies=cdict)
    response_json = response.json()
    print("===================== Validate  Status - Autopilot  ===========================================")
    validate_status(response_json=response_json['tasks'], status='workflow_end', AP_status_Url=AP_status_Url,
                    cookies=cdict)
    dict_output = {}
    dict_output['sno'] = input_dict['sno']
    #print(response_json["status"])
    print("Service ID", SL_ID)
    dict_output['id'] = SL_ID
    dict_output_final = Validate_SL(naas_config, data_provider, dict_output)
    write_data_Service_SL(path, i, dict_output=dict_output_final)
    print(
        "===================== Validate Service SL Job Status - Autopilot  ===========================================")


def Validate_SL(naas_config, data_provider, dict_output):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    print(
        "===================== Validate Service SL Fetch Service INFO - Autopilot  ===========================================")
    AP_validate_Url = naas_config.get_server("autopilot") + workflow_search
    request_body = data_provider.get_nested_node(["naas", "validate_UNI"])
    request_body['filter']['job._id'] = SL_ID
    print(request_body)
    response = requests.post(AP_validate_Url, json=request_body, verify=False, cookies=dict)
    response_json = response.json()
    input_list = ['asriServiceAlias', 'actId', 'pathServiceAlias', 'pathActTransactionId']
    flag = 0
    for each in response_json['results']:
        if each['job']['task'] == '1f19':
            print("print...", each['job']['task'])
            flag = 1
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
    print(
        "===================== Validate Service SL Fetch Service INFO - Autopilot  ===========================================")
    return dict_output


## Service SL  Delete functions
def Delete_DIA_Service_SL(naas_config, data_provider):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print(cdict['token'])
    # print("input dict02: ", input_dict)
    AP_start_job_url = naas_config.get_server("autopilot") + SL_D_workflow
    print("AP UNI WF URL", AP_start_job_url)
    request_body = data_provider.get_nested_node(["naas", "DIA_SL", "Delete_DIA_SL_Payload"])
    request_body['options']['variables']['requestPayload']['productSubType'] = "fiber_plus"
    request_body['options']['variables']['requestPayload']['serviceAlias'] = service_alias
    request_body['options']['variables']['requestPayload']['wanIPAddressBlocks'][0]['ipAddressBlock'] = cidrRange
    # request_body['options']['variables']['requestPayload']['failFast'] = input_dict['failFast']
    print(request_body)
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    response = requests.post(AP_start_job_url, json=request_body, headers=headers, verify=False, cookies=cdict)
    response_json = response.json()
    global SL_Delete_ID
    SL_Delete_ID = response_json["_id"]
    print("SL_Delete_ID :: ", SL_Delete_ID)
    return SL_Delete_ID


def validate_DL_SL_status(response_json, status, AP_status_Url, cookies):
    for key in response_json:
        if key == status:
            print("{}: {}".format(status, response_json['status']))
            if response_json['status'] == 'complete':
                break
            else:
                time.sleep(60)
                response = requests.get(AP_status_Url, verify=False, cookies=cookies)
                response_json = response.json()
                validate_DL_SL_status(response_json, status, AP_status_Url, cookies)


def Validate_DL_SL(naas_config, data_provider, dict_output):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    global SL_Delete_ID
    # SL_Delete_ID = "b51ed6e8c80148f292ec9396"
    AP_validate_Url = naas_config.get_server("autopilot") + workflow_search
    request_body = data_provider.get_nested_node(["naas", "validate_UNI"])
    request_body['filter']['job._id'] = SL_Delete_ID
    print(request_body)
    response = requests.post(AP_validate_Url, json=request_body, verify=False, cookies=dict)
    response_json = response.json()
    flag = 0
    for each in response_json['results']:
        # c5b , 1f19,
        if each['job']['task'] == '1f19':
            print("print...", each['job']['task'])
            flag = 1
            job_details = each['variables']['outgoing']['job_details']['data']['response']
            if job_details['status'] == 'success':
                data = job_details['data']
                print(data.keys())
                break
            else:
                print("JOB Failed...!")
                print("Error status CODE :")
                print("Error Status Message :")

    assert flag == 1, "Service create doesn't have 1f19 task -- EXIT"
    print(dict_output)
    return dict_output


def Delete_Service_SL(naas_config, data_provider):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print(cdict['token'])
    global SL_Delete_ID
    # SL_Delete_ID = "b51ed6e8c80148f292ec9396"
    SL_Delete_ID = Delete_DIA_Service_SL(naas_config=naas_config, data_provider=data_provider)
    AP_status_Url = naas_config.get_server("autopilot") + workflow_status + SL_Delete_ID
    response = requests.get(AP_status_Url, verify=False, cookies=cdict)
    response_json = response.json()
    validate_DL_SL_status(response_json=response_json, status='status', AP_status_Url=AP_status_Url, cookies=cdict)
    dict_output = {}
    # dict_output['sno'] = input_dict['sno']
    print(response_json["status"])
    print("Service ID", SL_Delete_ID)
    dict_output['id'] = SL_Delete_ID
    Validate_DL_SL(naas_config, data_provider, dict_output)
    # write_data_Service_SL(path, i, dict_output=dict_output_final)


## UNI Delete functions
def validate_UNI_Service_SL(naas_config, data_provider, dict_output):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
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
            flag = 1
            job_details = each['variables']['outgoing']['job_details']
            if job_details['status'] == 'complete':
                if 'error' in job_details.keys():
                    print("JOB Failed...!")
                    print("Error status CODE :", job_details['error']['data']['status'])
                    print("Error Status Message :", job_details['error']['data']['errorMessage'])
                else:
                    # dict_output={}
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


def Delete_UNI_Service_SL(naas_config, data_provider, input_dict):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print(cdict['token'])
    # print("input dict02: ", input_dict)
    AP_start_job_url = naas_config.get_server("autopilot") + SL_DUNI_workflow
    print("AP UNI WF URL", AP_start_job_url)
    request_body = data_provider.get_nested_node(["naas", "uni", "delete_uni_payload"])
    request_body['options']['variables']['requestPayload']['serviceAlias'] = input_dict['asriServiceAlias']
    # request_body['options']['variables']['requestPayload']['failFast'] = input_dict['failFast']
    print(request_body)
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    response = requests.post(AP_start_job_url, json=request_body, headers=headers, verify=False, cookies=cdict)
    response_json = response.json()
    global SL_Delete_UNI_ID
    SL_Delete_UNI_ID = response_json["_id"]
    print("SL_Delete_UNI_ID :: ", SL_Delete_UNI_ID)
    return SL_Delete_UNI_ID


def Delete_UNI_SL(naas_config, data_provider, input_dict):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print(cdict['token'])
    global SL_Delete_UNI_ID
    # SL_Delete_ID = "b51ed6e8c80148f292ec9396"
    SL_Delete_UNI_ID = Delete_UNI_Service_SL(naas_config=naas_config, data_provider=data_provider,
                                             input_dict=input_dict)
    AP_status_Url = naas_config.get_server("autopilot") + workflow_status + SL_Delete_UNI_ID
    response = requests.get(AP_status_Url, verify=False, cookies=cdict)
    response_json = response.json()
    validate_DL_SL_status(response_json=response_json, status='status', AP_status_Url=AP_status_Url, cookies=cdict)
    dict_output = {}
    # dict_output['sno'] = input_dict['sno']
    print(response_json["status"])
    print("Service ID", SL_Delete_UNI_ID)
    dict_output['id'] = SL_Delete_UNI_ID
    validate_UNI_Service_SL(naas_config, data_provider, dict_output)


def Validate_FD_Task(data_provider):
    # UNI_PCID = "AP-554909596-pytest-DIA-UNI-Hari004"
    print("===================== Flight Desk Validation - UNI  ===========================================")
    FD_validate_Url = "http://workmate-svc-test2.kubeodc-test.corp.intranet/RestService/Enterprise/v4/Work/task/advancedSearch?include=p,aa"
    print("FD URL", FD_validate_Url)
    request_body = data_provider.get_nested_node(["naas", "FD_Validate_Payload"])
    job_ID = request_body['searchFields'][0]['value']
    job_ID.append(UNI_PCID)
    print("Request Body", request_body)
    headers = {"x-Username": "AC71601"}
    response = requests.post(FD_validate_Url, json=request_body, headers=headers, verify=False)
    response_json = response.json()
    # print("WHole Response", response_json)
    for each in response_json['taskResults']:
        # print("Only Task Results", response_json['taskResults'])
        job_details = each['TASK_STATUS']
        # print("Task Name", each['TASK_NAME'])
        # print("Status", job_details)
        assert job_details == 'Completed', "Task status is not in Right Status"
    print("===================== Flight Desk Validation - UNI Completed ===========================================")
    return response_json


def Validate_Service_FD_Task(data_provider):
    FD_validate_Url = "http://workmate-svc-test2.kubeodc-test.corp.intranet/RestService/Enterprise/v4/Work/task/advancedSearch?include=p,aa"
    print(FD_validate_Url)
    request_body = data_provider.get_nested_node(["naas", "FD_Validate_Payload"])
    job_ID = request_body['searchFields'][0]['value']
    job_ID.append(Service_PCID)
    print(request_body)
    headers = {"x-Username": "AC71601"}
    response = requests.post(FD_validate_Url, json=request_body, headers=headers, verify=False)
    response_json = response.json()
    for each in response_json['taskResults']:
        job_details = each['TASK_STATUS']
        #print(job_details)
        assert job_details == 'Completed', "Task status is not in Right Status"
    return response_json
