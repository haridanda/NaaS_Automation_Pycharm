import json
from random import randint
import pytest
import requests
from pytest_bdd import given, when
import time
import yaml
from NaaS_Automation.naas_test import NaaS_Test
from conf.data import constant
from NaaS_Automation.NaaSFlow.DIA.test.constants import *
from NaaS_Automation.NaaSFlow.DIA.test.utils_copy import get_data, write_data_UNI_SL, post_Create_UNI, validate_status, \
    Validate_UNI, Validate_Service_FD_Task, Validate_FD_Task, generate_service_alias, Create_skinny, assign_IP, \
    Create_Service_SL, Delete_Service_SL, Delete_UNI_SL, write_data_Service_SL, get_port_Aval_MESH, get_cookies


@pytest.fixture(scope="session")
def get_AP_token(naas_config, data_provider):
    login_url = naas_config.get_server("autopilot") + login
    print("\n===================== AP Login ===========================================")
    print("AP Login URL", login_url)
    request_body = {"user": {"username": constant.user, "password": constant.password}}
    headers = {"Content-Type": "application/json"}
    response = requests.post(login_url, json=request_body, headers=headers, verify=False)
    cookies_dict = response.cookies.get_dict()
    with open("API_token.json", "w") as token:
        token.write(json.dumps(cookies_dict))
    yield response


@given('login AutoPilot')
def test_login(get_AP_token, naas_test):
    naas_test.is_http_200(get_AP_token)
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print("Login Token ", cdict['token'])
    print("===================== AP Login - Completed  ===========================================")


@when('validate Port avalibility')
def port_check_Mesh(naas_config):
    global flag
    flag = False
    response = get_port_Aval_MESH(naas_config=naas_config)
    result = response['resources'][0]['pathElements'][0]['type']
    if result in ['ME', 'ENNI']:
        print("Result ;;", result)
        attributes = response['resources'][0]['pathElements'][0]['subElements'][0]['aendPort']['attributes'][0]
        if attributes['name'] == 'Class':
            assert attributes['value'] in ['Empty Slot', 'Physical']
            flag = True
            print(
                "===================== Mesh - PORT Avalibility Check Completed ===========================================")
    return flag


def generate_uniqueId_str():
    unique_value = randint(550000000, 558000000)
    return (str(unique_value))


import yaml

def load_scenarios():
    with open("/Users/haridanda/PycharmProjects/act/NaaS_Automation/NaaSFlow/DIA/test/data.yaml", "r") as f:
        data = yaml.safe_load(f)
    return data

def update_response_id(scenario_index, response_id):
    with open("/Users/haridanda/PycharmProjects/act/NaaS_Automation/NaaSFlow/DIA/test/data.yaml", "r") as f:
        data = yaml.safe_load(f)
    data[scenario_index]["output_data"]["UNI_JobID"] = response_id
    with open("/Users/haridanda/PycharmProjects/act/NaaS_Automation/NaaSFlow/DIA/test/data.yaml", "w") as f:
        yaml.safe_dump(data, f)

def update_UNI_response(scenario_index, service_allias, act_id):
    with open("/Users/haridanda/PycharmProjects/act/NaaS_Automation/NaaSFlow/DIA/test/data.yaml", "r") as f:
        data = yaml.safe_load(f)
    data[scenario_index]["output_data"]["UNI_Service_Allias"] = service_allias
    data[scenario_index]["output_data"]["UNI_ACT_ID"] = act_id
    with open("/Users/haridanda/PycharmProjects/act/NaaS_Automation/NaaSFlow/DIA/test/data.yaml", "w") as f:
        yaml.safe_dump(data, f)

@pytest.mark.parametrize("scenario_index", range(len(load_scenarios())))
def test_Create_AUNI_SL(naas_config, data_provider, scenario_index):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    global id
    print("\n===================== SCENARIO :: ===========================================")

    global PCID
    PCID = generate_uniqueId_str()
    scenarios = load_scenarios()
    scenario = scenarios[scenario_index]
    input_data = scenario["input_data"]
    print("Scenario :: ", input_data)

    global UNI_ID
    UNI_ID = post_Create_UNI(PCID, naas_config=naas_config, data_provider=data_provider, input_dict=input_data, update_response_id = update_response_id, scenario_index = scenario_index)

    print("===================== Validate UNI Job Status Port - Autopilot  ===========================================")
    AP_status_Url = naas_config.get_server("autopilot") + workflow_status + UNI_ID
    response = requests.get(AP_status_Url, verify=False, cookies=cdict)
    response_json = response.json()
    validate_status(response_json=response_json['tasks'], status='workflow_end', AP_status_Url=AP_status_Url,
                    cookies=cdict)
    dict_output = {}
    #dict_output['sno'] = input_dict['sno']
    #i = dict_output['sno']
    #dict_output['id'] = id
    #UNI_ID = "998c7f3fab834fc9b4bfbb85"
    print(UNI_ID)
    dict_output_final = Validate_UNI(naas_config, data_provider,UNI_ID, dict_output = dict_output,scenario_index = scenario_index, update_UNI_response = update_UNI_response )
    print(dict_output_final)
    #input_dict["asriServiceAlias"] = dict_output_final["asriServiceAlias"]
    #write_data_UNI_SL(path, input_dict['sno'], dict_output=dict_output_final)

    # FD validation
    UNI_FD = Validate_FD_Task(data_provider)
    """
    # Genereate Skinny
    generate_service_alias(naas_config, data_provider)

    # Create SKinny
    Create_skinny(naas_config, data_provider)

    # Assing IP
    assign_IP(naas_config, data_provider)

    # Create Service SL
    Create_Service_SL(PCID, naas_config=naas_config, data_provider=data_provider, input_dict=input_dict, i=i)

    # FD Validation
    Service_FD = Validate_Service_FD_Task(data_provider)

    #Delete Service
    Delete_Service_SL(naas_config=naas_config, data_provider=data_provider)

    #Delete UNI
    Delete_UNI_SL(naas_config=naas_config, data_provider=data_provider, input_dict=input_dict)
"""
