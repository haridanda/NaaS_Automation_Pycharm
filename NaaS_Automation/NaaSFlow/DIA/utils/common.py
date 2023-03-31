import os
from random import randint

import pytest
import requests
from NaaS_Automation.NaaSFlow.DIA.utils.constants import *
import time
from allure_commons._allure import *
import json
import yaml


def update_counter(counter):
    return counter


def generate_uniqueId_str():
    unique_value = randint(550000000, 558000000)
    return (str(unique_value))


def load_scenarios():
    file_path = os.path.join(os.getcwd(), "NaaS_Automation/NaaSFlow/DIA/test/data.yaml")
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    return data


def update_response_id(scenario_index, response_id):
    file_path = os.path.join(os.getcwd(), "NaaS_Automation/NaaSFlow/DIA/test/data.yaml")
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    data[scenario_index]["output_data"]["UNI_JobID"] = response_id
    file_path = os.path.join(os.getcwd(), "NaaS_Automation/NaaSFlow/DIA/test/data.yaml")
    with open(file_path, "w") as f:
        yaml.safe_dump(data, f)


def update_UNI_response(scenario_index, service_allias, act_id):
    file_path = os.path.join(os.getcwd(), "NaaS_Automation/NaaSFlow/DIA/test/data.yaml")
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    data[scenario_index]["output_data"]["UNI_Service_Allias"] = service_allias
    data[scenario_index]["output_data"]["UNI_ACT_ID"] = act_id
    file_path = os.path.join(os.getcwd(), "NaaS_Automation/NaaSFlow/DIA/test/data.yaml")
    with open(file_path, "w") as f:
        yaml.safe_dump(data, f)


def Update_SL_Response(scenario_index, pathServiceAlias, pathActTransactionId, asriServiceAlias, actId):
    file_path = os.path.join(os.getcwd(), "NaaS_Automation/NaaSFlow/DIA/test/data.yaml")
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    data[scenario_index]["output_data"]["Oline_ACT_ID"] = pathActTransactionId
    data[scenario_index]["output_data"]["Oline_Service_Allias"] = pathServiceAlias
    data[scenario_index]["output_data"]["Service_ACT_ID"] = actId
    data[scenario_index]["output_data"]["Service_Service_Allias"] = asriServiceAlias
    file_path = os.path.join(os.getcwd(), "NaaS_Automation/NaaSFlow/DIA/test/data.yaml")
    with open(file_path, "w") as f:
        yaml.safe_dump(data, f)


def update_service_response_id(scenario_index, response_id):
    file_path = os.path.join(os.getcwd(), "NaaS_Automation/NaaSFlow/DIA/test/data.yaml")
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    data[scenario_index]["output_data"]["Service_SL_JobID"] = response_id
    file_path = os.path.join(os.getcwd(), "NaaS_Automation/NaaSFlow/DIA/test/data.yaml")
    with open(file_path, "w") as f:
        yaml.safe_dump(data, f)


@description("GET Port Avalibility from Mesh")
@step
def get_port_Aval_MESH(naas_config):
    get_mesh = naas_config.get_server("sasi") + mesh_path
    print("\n ===================== Mesh - PORT Avalibility Check ===========================================")
    print("Sasi - Mesh URL", get_mesh)
    response = requests.get(get_mesh, verify=False)
    return response.json()


def get_cookies():
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    return cdict


@step("Create UNI request to AutoPilot")
def post_Create_UNI(PCID, naas_config, data_provider, input_dict, update_response_id, scenario_index):
    print("\n   ===================== Create Port - Autopilot  ===========================================")
    AP_start_job_url = naas_config.get_server("autopilot") + UNI_workflow
    print("AP UNI WF URL", AP_start_job_url)
    request_body = data_provider.get_nested_node(["naas", "uni", "create_uni_payload"])
    CID = request_body['options']['variables']['requestPayload']['parentCorrelationId']
    request_body['options']['variables']['requestPayload']['parentCorrelationId'] = CID.replace("PARENTCID", PCID)
    global UNI_PCID
    UNI_PCID = request_body['options']['variables']['requestPayload']['parentCorrelationId']
    request_body['options']['variables']['requestPayload']['serviceType'] = input_dict["serviceType"]
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
    print("UNI AP Job  ID -", response_id)

    # Load UNI ID  to Yaml file
    update_response_id(scenario_index, response_id)
    print("===================== Create Port - Autopilot  ===========================================")
    return id


@step("Validate UNI JOb status")
def validate_status(response_json, status, AP_status_Url, cookies):
    for key in response_json:
        if key == status:
            print("{}: {}".format(status, response_json[key]['status']))
            if response_json[key]['status'] == 'complete':
                print(
                    "===================== Validate Job Status - Completed  ===========================================")
                break

            else:
                time.sleep(60)
                response = requests.get(AP_status_Url, verify=False, cookies=cookies)
                response_json = response.json()
                validate_status(response_json['tasks'], status, AP_status_Url, cookies)


@step("Validate UNI - fetch UNI Info")
def Validate_UNI(naas_config, data_provider, UNI_ID, dict_output, update_UNI_response, scenario_index):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    print("===================== Get UNI INFO - Autopilot  ===========================================")
    AP_validate_Url = naas_config.get_server("autopilot") + workflow_search
    request_body = data_provider.get_nested_node(["naas", "validate_UNI"])
    request_body['filter']['job._id'] = UNI_ID
    response = requests.post(AP_validate_Url, json=request_body, verify=False, cookies=dict)
    response_json = response.json()
    input_list = ['asriServiceAlias', 'actId']
    flag = 0
    for each in response_json['results']:
        if each['job']['task'] == '1540':
            flag = 1
            job_details = each['variables']['outgoing']['job_details']
            if job_details['status'] == 'complete':
                if 'error' in job_details.keys():
                    print("JOB Failed...!")
                    print("Error status CODE :", job_details['error']['data']['status'])
                    print("Error Status Message :", job_details['error']['data']['errorMessage'])
                else:
                    data = job_details['data']
                    for item in input_list:
                        print("UNI Data", data['response']['data'])
                        assert item in data['response']['data'].keys()
                        dict_output[item] = data['response']['data'][item]
            break

    assert flag == 1, "UNI create doesn't have 1540 task -- EXIT"
    print("===================== Get UNI INFO - Autopilot  ===========================================")
    print("UNI Response out put", dict_output)
    service_allias = dict_output['asriServiceAlias']
    act_id = dict_output['actId']
    # Load UNI ID  to Yaml file
    update_UNI_response(scenario_index, service_allias, act_id)
    return dict_output


def Validate_UNI_v2(naas_config, data_provider, UNI_ID, dict_output, update_UNI_response, scenario_index):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    print("===================== Get UNI INFO - Autopilot  ===========================================")
    AP_validate_Url = naas_config.get_server("autopilot") + workflow_searchV2
    request_body = data_provider.get_nested_node(["naas", "validate_UNI_v2"])
    request_body['options']['filter']['_id'] = UNI_ID
    print("Request Body", request_body)
    response = requests.post(AP_validate_Url, json=request_body, verify=False, cookies=dict)
    response_json = response.json()
    input_list = ['asriServiceAlias', 'actId']
    job_details = response_json['results'][0]['variables']

    if 'data' in job_details or 'response' in job_details:
        assert job_details['data']['response']['status'] == 'success'
        data = job_details['data']['response']['data']
        for item in input_list:
            assert item in data.keys()
            dict_output[item] = data[item]

        print("UNI Response out put", dict_output)
        service_allias = dict_output['asriServiceAlias']
        act_id = dict_output['actId']

        # Load UNI ID  to Yaml file
        update_UNI_response(scenario_index, service_allias, act_id)
        return dict_output
    else:
        print(job_details['error']['data']['status'])
        print(job_details['error']['data']['errorMessage'])
        print(job_details['error']['data']['actID'])
        pytest.xfail('UNI SL - JOB Failed')


@description("Validate UNI in ASRI Inventory")
@step("Validate UNI in ASRI Inventory")
def validate_UNI_ASRI(naas_config, data_provider, Uni_service_allias):
    print("===================== Get UNI INFO ASRI  - Autopilot  ===========================================")
    Asri_URL = naas_config.get_server("asri-url") + get_asri + Uni_service_allias
    print(Asri_URL)
    response = requests.get(Asri_URL, verify=False)
    response_json = response.json()
    assert response_json['resources'][0]["type"] == "UNI", "type Incorrect in ASRI"
    assert response_json['resources'][0]["status"] == "In Service", "status NOT IN Service"
    print("ASRI Validation Success")
    print("===================== Get UNI INFO ASRI  - Autopilot  ===========================================")

@description("Validate UNI in ACT")
@step("Validate UNI in ACT")
def validate_UNI_ACT(naas_config, data_provider, output_dict):
    print(
        "===================== Validate UNI Service Allias in ACT - Autopilot  ===========================================")
    Uni_actID = output_dict['UNI_ACT_ID']
    ACT_validate = naas_config.get_server("act_validation") + Uni_actID
    print("ACT UNI Validaiton URL", ACT_validate)
    username = 'autopilot'
    password = 'TestNotProduction'
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    response = requests.get(ACT_validate, auth=(username, password), headers=headers, verify=False)
    print(response.text)
    response_json = response.json()

    job_details = response_json['actRequest']

    if job_details['status'] == 'complete':
        assert job_details['resultMessage'] == 'SUCCESS', "resultmessage not expected ..!"
        print("ACT Validation Success")
    else:
        pytest.xfail('UNI SL - ACT validation FAILED')


def generate_service_alias(naas_config, data_provider):
    print("===================== Generate ASRI Service Allias - Autopilot  ===========================================")
    generate_servias_alias = naas_config.get_server("sasi-wrap") + sasi_asri
    request_body = data_provider.get_nested_node(["naas", "generate_alias"])
    print("Request body",request_body)
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    response = requests.put(generate_servias_alias, json=request_body, headers=headers, verify=False)
    response_json = response.json()
    global service_alias
    service_alias = response_json["generatedName"]
    print("\n Generated Service Alias", service_alias)
    print("===================== Generate Service Allias - Autopilot  ===========================================")
    return service_alias


def Create_skinny(naas_config, data_provider):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print(
        "===================== Create Skinny Service Allias in ASRI - Autopilot  ===========================================")
    AP_create_skinny = naas_config.get_server("autopilot") + skinny_workflow
    request_body = data_provider.get_nested_node(["naas", "Create_skinny"])
    request_body['options']['variables']['resourceData']['name'] = service_alias
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    print("Request body", request_body)
    response = requests.post(AP_create_skinny, json=request_body, headers=headers, verify=False, cookies=cdict)
    print("Create skinny status: ", response.status_code)
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
    print('\ncidrRange:', cidrRange)
    print("===================== Assign IP - Autopilot  ===========================================")


def assign_Static_IP(naas_config, data_provider):
    print("===================== Assign IP - Autopilot  ===========================================")
    get_servias_alias = naas_config.get_server("sasi-wrap") + assign_ip
    request_body = data_provider.get_nested_node(["naas", "assign_Static_IP"])
    request_body['circuitId'] = service_alias
    print("Request Body", request_body)
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    response = requests.post(get_servias_alias, json=request_body, headers=headers, verify=False)
    print("generate service allias", response.text)
    response_json = response.json()
    global Static_cidrRange
    Static_cidrRange = response_json["ipBlock"][0]["cidrRange"]
    print('cidrRange:', Static_cidrRange)

    return Static_cidrRange
    print("===================== Assign IP - Autopilot  ===========================================")


def next_hop(static_ip):
    ip_address = static_ip.split("/")[0]
    last_val = int(ip_address.split(".")[-1])
    new_val = last_val + 2
    new_ip = ip_address.replace(ip_address.split(".")[-1], str(new_val))
    return new_ip


def Release_IP(naas_config, data_provider):
    print("===================== Release IP - Autopilot  ===========================================")
    get_servias_alias = naas_config.get_server("sasi-wrap") + release_ip
    request_body = data_provider.get_nested_node(["naas", "release_IP"])
    request_body['circuitId'] = service_alias
    request_body['cidrRange'] = cidrRange
    print("Request Body", request_body)
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    response = requests.post(get_servias_alias, json=request_body, headers=headers, verify=False)
    response_json = response.json()
    print("\n Release IP Response :", response_json)
    print("===================== Release IP - Autopilot  ===========================================")


def Create_DIA_Service_SL(PCID, Uni_service_allias, naas_config, data_provider, input_dict, scenario_index,
                          update_service_response_id):
    print("===================== Create Service SL - Autopilot  ===========================================")
    AP_start_job_url = naas_config.get_server("autopilot") + SL_workflow
    print("AP UNI WF URL", AP_start_job_url)
    request_body = data_provider.get_nested_node(["naas", "DIA_SL", "Create_DIA_SL_Payload"])
    CID = request_body['options']['variables']['requestPayload']['parentCorrelationId']
    request_body['options']['variables']['requestPayload']['parentCorrelationId'] = CID.replace("PARENTCID", PCID)
    global Service_PCID
    Service_PCID = request_body['options']['variables']['requestPayload']['parentCorrelationId']
    request_body['options']['variables']['requestPayload']['productSubType'] = input_dict["serviceType"]
    request_body['options']['variables']['requestPayload']['uniServiceAlias'] = Uni_service_allias
    request_body['options']['variables']['requestPayload']['serviceAlias'] = service_alias
    request_body['options']['variables']['requestPayload']['wanIPAddressBlocks'][0]['ipAddressBlock'] = cidrRange
    for k, v in input_dict.items():
        if k == 'static':
            if v == True:
                print(
                    "***********************************************Enter Static Block ***********************************************")
                request_body_static = data_provider.get_nested_node(["naas", "DIA_SL", "static"])
                request_body['options']['variables']['requestPayload']['staticRoutes'] = request_body_static
                static_ip = assign_Static_IP(naas_config=naas_config, data_provider=data_provider)
                request_body['options']['variables']['requestPayload']['staticRoutes'][0]['route'] = static_ip
                request_body['options']['variables']['requestPayload']['staticRoutes'][0]['nextHop'] = next_hop(
                    cidrRange)
                print(request_body)
        if k == 'bgp':
            if v == True:
                print(
                    "*********************************************** Enter BGP Block ***********************************************")
                request_body_bgp = data_provider.get_nested_node(["naas", "DIA_SL", "bgp"])
                request_body['options']['variables']['requestPayload']['bgps'] = request_body_bgp
                print(request_body)
                request_body['options']['variables']['requestPayload']['bgps'][0]['neighbor'] = next_hop(cidrRange)

    print(
        "*********************************************** Complete request ***********************************************")
    print("Request Body For Service SL", request_body)
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    response = requests.post(AP_start_job_url, json=request_body, headers=headers, verify=False, cookies=cdict)
    response_json = response.json()
    global SL_id
    SL_id = response_json["_id"]
    response_id = SL_id
    print("Service SL Job  ID", response_id)

    # Load UNI ID  to Yaml file
    update_service_response_id(scenario_index, response_id)
    print("===================== Create Service SL - Autopilot  ===========================================")
    return SL_id


@step
def Create_Service_SL(PCID, Uni_service_allias, naas_config, data_provider, input_dict, scenario_index,
                      update_service_response_id, Update_SL_Response):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    global SL_ID
    SL_ID = Create_DIA_Service_SL(PCID, Uni_service_allias, naas_config, data_provider, input_dict, scenario_index,
                                  update_service_response_id)
    # Get call on UNI ID
    AP_status_Url = naas_config.get_server("autopilot") + workflow_status + SL_ID
    response = requests.get(AP_status_Url, verify=False, cookies=cdict)
    response_json = response.json()
    print("===================== Validate  Job Status - Autopilot  ===========================================")
    validate_status(response_json=response_json['tasks'], status='workflow_end', AP_status_Url=AP_status_Url,
                    cookies=cdict)
    dict_output = {}
    dict_output['id'] = SL_ID
    dict_output_final = Validate_SL_v2(naas_config, data_provider, dict_output, scenario_index, Update_SL_Response)
    print(dict_output_final)
    print(
        "===================== Validate Service SL Job Status - Autopilot  ===========================================")


def Validate_SL(naas_config, data_provider, dict_output, scenario_index, Update_SL_Response):
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
    print("SL Response out put", dict_output)
    pathServiceAlias = dict_output['pathServiceAlias']
    pathActTransactionId = dict_output['pathActTransactionId']
    asriServiceAlias = dict_output['asriServiceAlias']
    actId = dict_output['actId']
    Update_SL_Response(scenario_index, pathServiceAlias, pathActTransactionId, asriServiceAlias, actId)
    print(
        "===================== Validate Service SL Fetch Service INFO - Autopilot  ===========================================")
    return dict_output


def Validate_SL_v2(naas_config, data_provider, dict_output, scenario_index, Update_SL_Response):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    print(
        "===================== Validate Service SL Fetch Service INFO - Autopilot  ===========================================")
    AP_validate_Url = naas_config.get_server("autopilot") + workflow_searchV2
    request_body = data_provider.get_nested_node(["naas", "validate_UNI_v2"])
    request_body['options']['filter']['_id'] = SL_ID
    print(request_body)
    response = requests.post(AP_validate_Url, json=request_body, verify=False, cookies=dict)
    response_json = response.json()
    input_list = ['asriServiceAlias', 'actId', 'pathServiceAlias', 'pathActTransactionId']
    job_details = response_json['results'][0]['variables']

    if 'data' in job_details:
        assert job_details['data']['response']['status'] == 'success'
        data = job_details['data']['response']['data']
        for item in input_list:
            assert item in data.keys()
            print(data[item])
            dict_output[item] = data[item]

        print(dict_output)
        print("SL Response out put", dict_output)
        pathServiceAlias = dict_output['pathServiceAlias']
        pathActTransactionId = dict_output['pathActTransactionId']
        asriServiceAlias = dict_output['asriServiceAlias']
        actId = dict_output['actId']
        Update_SL_Response(scenario_index, pathServiceAlias, pathActTransactionId, asriServiceAlias, actId)
        print(
            "===================== Validate Service SL Fetch Service INFO - Autopilot  ===========================================")
        return dict_output
    else:
        #global oline_alias
        oline_alias = job_details['asriServiceAlias']
        dict_output['pathServiceAlias'] = oline_alias
        print("oline allias ::", oline_alias)
        print(job_details['error']['data']['status'])
        print(job_details['error']['data']['errorMessage'])
        print(job_details['error']['data']['actID'])


## Service SL  Delete functions
def Delete_DIA_Service_SL(naas_config, data_provider, input_dict):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print(
        "===================== Delete Service SL  - Autopilot  ===========================================")
    AP_start_job_url = naas_config.get_server("autopilot") + SL_D_workflow
    print("AP UNI WF URL", AP_start_job_url)
    request_body = data_provider.get_nested_node(["naas", "DIA_SL", "Delete_DIA_SL_Payload"])
    request_body['options']['variables']['requestPayload']['productSubType'] = "fiber_plus"
    request_body['options']['variables']['requestPayload']['serviceAlias'] = service_alias
    request_body['options']['variables']['requestPayload']['wanIPAddressBlocks'][0]['ipAddressBlock'] = cidrRange
    print("\nRequest payload :", request_body)
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    for k, v in input_dict.items():
        if k == 'static':
            if v == True:
                print(
                    "***********************************************Enter Static Block ***********************************************")
                request_body_static = data_provider.get_nested_node(["naas", "DIA_SL", "static"])
                request_body['options']['variables']['requestPayload']['staticRoutes'] = request_body_static
                request_body['options']['variables']['requestPayload']['staticRoutes'][0]['route'] = Static_cidrRange
                request_body['options']['variables']['requestPayload']['staticRoutes'][0]['nextHop'] = next_hop(
                    cidrRange)
                print(request_body)
        if k == 'bgp':
            if v == True:
                print(
                    "*********************************************** Enter BGP Block ***********************************************")
                request_body_bgp = data_provider.get_nested_node(["naas", "DIA_SL", "bgp"])
                request_body['options']['variables']['requestPayload']['bgps'] = request_body_bgp
                print(request_body)
                request_body['options']['variables']['requestPayload']['bgps'][0]['neighbor'] = next_hop(cidrRange)
    response = requests.post(AP_start_job_url, json=request_body, headers=headers, verify=False, cookies=cdict)
    response_json = response.json()
    global SL_Delete_ID
    SL_Delete_ID = response_json["_id"]
    print("\n SL_Delete_ID :: ", SL_Delete_ID)
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
    print(
        "===================== Validate Delete Service SL Fetch job INFO - Autopilot  ===========================================")
    AP_validate_Url = naas_config.get_server("autopilot") + workflow_searchV2
    request_body = data_provider.get_nested_node(["naas", "validate_UNI_v2"])
    request_body['options']['filter']['_id'] = SL_Delete_ID
    print(request_body)
    response = requests.post(AP_validate_Url, json=request_body, verify=False, cookies=dict)
    response_json = response.json()
    job_details = response_json['results'][0]['variables']

    if 'data' in job_details:
        assert job_details['data']['response']['status'] == 'success'
        data = job_details['data']['response']['data']
        print(data.keys())
        return dict_output
    else:

        data = job_details['error']
        print(data.keys())


def Delete_Service_SL(naas_config, data_provider, input_dict):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    global SL_Delete_ID
    SL_Delete_ID = Delete_DIA_Service_SL(naas_config, data_provider, input_dict)
    AP_status_Url = naas_config.get_server("autopilot") + workflow_status + SL_Delete_ID
    response = requests.get(AP_status_Url, verify=False, cookies=cdict)
    response_json = response.json()
    print("===================== Validate Delete  SL job Status - Autopilot  ===========================================")
    validate_DL_SL_status(response_json=response_json, status='status', AP_status_Url=AP_status_Url, cookies=cdict)
    print("===================== Validate Delete  SL job Status - Autopilot  ===========================================")
    dict_output = {}
    print("Service ID", SL_Delete_ID)
    dict_output['id'] = SL_Delete_ID
    Validate_DL_SL(naas_config, data_provider, dict_output)


def Validate_Delete_Oline(naas_config, data_provider,output_dict1):
    print("===================== Get Oline INFO ASRI  - Autopilot  ===========================================")
    oline_alias = output_dict1['Oline_Service_Allias']
    Asri_URL = naas_config.get_server("asri-url") + get_asri + oline_alias
    print(Asri_URL)
    response = requests.get(Asri_URL, verify=False)
    if response.status_code == 200:
        response_json = response.json()
        type = response_json['resources'][0]["type"]
        print(type)
        status = response_json['resources'][0]["status"]
        print(status)
        with open("API_token.json", "r") as etoken:
            cdict = json.loads(etoken.read())
        print(cdict['token'])
        if type == "O Line" and status == "In Service":
            SL_Delete_Oline_ID = Delete_online_wf(naas_config, data_provider, output_dict1)
            AP_status_Url = naas_config.get_server("autopilot") + workflow_status + SL_Delete_Oline_ID
            response = requests.get(AP_status_Url, verify=False, cookies=cdict)
            response_json = response.json()
            validate_DL_SL_status(response_json=response_json, status='status', AP_status_Url=AP_status_Url, cookies=cdict)
            dict_output = {}
            print(response_json["status"])
            print("Delete Oline ID", SL_Delete_Oline_ID)
            dict_output['id'] = SL_Delete_Oline_ID
            Validate_DL_Oline_TL(naas_config, data_provider, dict_output)

        else :
            print(response_json)

    else:
        print("Oline De activated successfully")


def Delete_online_wf(naas_config, data_provider, output_dict1):
    AP_start_job_url = naas_config.get_server("autopilot") + SL_DOnline_workflow
    print("AP UNI WF URL", AP_start_job_url)
    #
    oline_alias = output_dict1['Oline_Service_Allias']
    request_body = data_provider.get_nested_node(["naas", "DIA_SL", "Delete_Oline_TL_Payload"])
    request_body['options']['variables']['requestPayload']['serviceAlias'] = oline_alias
    print(request_body)
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])

    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    response = requests.post(AP_start_job_url, json=request_body, headers=headers, verify=False, cookies=cdict)
    response_json = response.json()
    global SL_Delete_Oline_ID
    SL_Delete_Oline_ID = response_json["_id"]
    print("SL_Delete_ID :: ", SL_Delete_Oline_ID)
    return SL_Delete_Oline_ID


def Validate_DL_Oline_TL(naas_config, data_provider, dict_output):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    AP_validate_Url = naas_config.get_server("autopilot") + workflow_searchV2
    request_body = data_provider.get_nested_node(["naas", "validate_UNI_v2"])
    request_body['options']['filter']['_id'] = SL_Delete_Oline_ID
    print(request_body)
    response = requests.post(AP_validate_Url, json=request_body, verify=False, cookies=dict)
    response_json = response.json()
    job_details = response_json['results'][0]['variables']
    if 'data' in job_details:
        assert job_details['data']['response']['status'] == 'success'
        data = job_details['data']['response']['data']
        print(data.keys())
        return dict_output
    else:

        data = job_details['error']
        print(data.keys())


## UNI Delete functions
def validate_UNI_Service_SL(naas_config, data_provider, dict_output):
    with open("API_token.json", "r") as etoken:
        dict = json.loads(etoken.read())
    print(
        "\n ===================== Delete UNI SL Job Info - Autopilot  ===========================================")
    AP_validate_Url = naas_config.get_server("autopilot") + workflow_searchV2
    request_body = data_provider.get_nested_node(["naas", "validate_UNI_v2"])
    request_body['options']['filter']['_id'] = SL_Delete_UNI_ID
    print(request_body)
    response = requests.post(AP_validate_Url, json=request_body, verify=False, cookies=dict)
    response_json = response.json()
    job_details = response_json['results'][0]['variables']

    if 'result' in job_details:
        assert job_details['result']['response']['status'] == 'success'
        data = job_details['result']['response']['data']
        print(data.keys())
        return dict_output
    else:

        print(job_details['error']['code'])
        print(job_details['error']['statusCode'])
        print(job_details['error']['message'])


def Delete_UNI_Service_SL(Uni_service_allias, naas_config, data_provider):
    print(
        "===================== Delete UNI SL - Autopilot  ===========================================")
    AP_start_job_url = naas_config.get_server("autopilot") + SL_DUNI_workflow
    print("AP UNI WF URL", AP_start_job_url)
    request_body = data_provider.get_nested_node(["naas", "uni", "delete_uni_payload"])
    request_body['options']['variables']['requestPayload']['serviceAlias'] = Uni_service_allias
    print("\n Delete UNI Request Body", request_body)
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    response = requests.post(AP_start_job_url, json=request_body, headers=headers, verify=False, cookies=cdict)
    response_json = response.json()
    global SL_Delete_UNI_ID
    SL_Delete_UNI_ID = response_json["_id"]
    print("SL_Delete_UNI_ID :: ", SL_Delete_UNI_ID)
    print(
        "===================== Delete UNI SL - Autopilot  ===========================================")
    return SL_Delete_UNI_ID


def Delete_UNI_SL(Uni_service_allias, naas_config, data_provider):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    global SL_Delete_UNI_ID
    SL_Delete_UNI_ID = Delete_UNI_Service_SL(Uni_service_allias, naas_config=naas_config, data_provider=data_provider)
    AP_status_Url = naas_config.get_server("autopilot") + workflow_status + SL_Delete_UNI_ID
    response = requests.get(AP_status_Url, verify=False, cookies=cdict)
    response_json = response.json()
    validate_DL_SL_status(response_json=response_json, status='status', AP_status_Url=AP_status_Url, cookies=cdict)
    dict_output = {}
    print(response_json["status"])
    print("Service ID", SL_Delete_UNI_ID)
    dict_output['id'] = SL_Delete_UNI_ID
    validate_UNI_Service_SL(naas_config, data_provider, dict_output)


def Validate_FD_Task(data_provider, naas_config):
    print("===================== Flight Desk Validation - UNI  ===========================================")
    time.sleep(60)
    FD_validate_Url = naas_config.get_server("fd_url")
    print("FD URL", FD_validate_Url)
    request_body = data_provider.get_nested_node(["naas", "FD_Validate_Payload"])
    job_ID = request_body['searchFields'][0]['value']
    job_ID.append(UNI_PCID)
    print("Request Body", request_body)
    headers = {"x-Username": "AC71601"}
    response = requests.post(FD_validate_Url, json=request_body, headers=headers, verify=False)
    response_json = response.json()
    for each in response_json['taskResults']:
        job_details = each['TASK_STATUS']
        assert job_details == 'Completed', "Task status is not in Right Status"
    print("===================== Flight Desk Validation - UNI Completed ===========================================")
    return response_json


def Validate_Service_FD_Task(data_provider, naas_config):
    print("===================== Flight Desk Validation - Service  ===========================================")
    time.sleep(60)
    FD_validate_Url = naas_config.get_server("fd_url")
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
        assert job_details == 'Completed', "Task status is not in Right Status"
    return response_json
