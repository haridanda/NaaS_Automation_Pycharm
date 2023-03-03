import json
from random import randint
import pytest
import requests
from pytest_bdd import given, when
import time
from NaaS_Automation.naas_test import NaaS_Test
from conf.data import constant
from NaaS_Automation.NaaSFlow.DIA.test.constants import *
from NaaS_Automation.NaaSFlow.DIA.test.utils import get_data, write_data_UNI_SL, post_Create_UNI, validate_status, \
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
def test_port_check_Mesh(naas_config):
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


@pytest.mark.parametrize("input_dict", get_data(file=path))
def test_Create_AUNI_SL(naas_config, data_provider, input_dict):
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    global id
    print("\n===================== SCENARIO :: ===========================================")
    print("Scenario :: ", input_dict)
    global PCID
    PCID = generate_uniqueId_str()

    id = post_Create_UNI(PCID, naas_config=naas_config, data_provider=data_provider, input_dict=input_dict)
    AP_status_Url = naas_config.get_server("autopilot") + workflow_status + id
    response = requests.get(AP_status_Url, verify=False, cookies=cdict)
    response_json = response.json()
    print("===================== Validate UNI Job Status Port - Autopilot  ===========================================")
    validate_status(response_json=response_json['tasks'], status='workflow_end', AP_status_Url=AP_status_Url,
                    cookies=cdict)
    dict_output = {}
    dict_output['sno'] = input_dict['sno']
    i = dict_output['sno']
    dict_output['id'] = id
    dict_output_final = Validate_UNI(naas_config, data_provider, dict_output)
    print(dict_output_final)
    input_dict["asriServiceAlias"] = dict_output_final["asriServiceAlias"]
    write_data_UNI_SL(path, input_dict['sno'], dict_output=dict_output_final)

    # FD validation
    UNI_FD = Validate_FD_Task(data_provider)

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
