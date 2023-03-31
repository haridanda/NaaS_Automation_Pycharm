import json
import pytest
import requests
from pytest_bdd import given, when, then
from allure_commons._allure import story
from allure_commons._allure import description
from NaaS_Automation.NaaSFlow.DIA.utils.constants import *
from NaaS_Automation.NaaSFlow.DIA.utils.common import  post_Create_UNI, validate_status, \
    generate_service_alias, Create_skinny, assign_IP, \
    validate_UNI_ASRI, generate_uniqueId_str, load_scenarios, update_response_id, update_UNI_response,Validate_UNI_v2,validate_UNI_ACT,Validate_Delete_Oline, Create_Service_SL,Release_IP, Delete_Service_SL, Delete_UNI_SL,update_service_response_id, Update_SL_Response, get_port_Aval_MESH


@given('login AutoPilot')
@description ('Login AP')
def test_login(get_AP_token, naas_test):
    naas_test.is_http_200(get_AP_token)
    with open("API_token.json", "r") as etoken:
        cdict = json.loads(etoken.read())
    print("Login Token ", cdict['token'])
    print("===================== AP Login - Completed  ===========================================")


@when('validate Port avalibility')
@description ('Validate Mesh')
def test_port_check_Mesh(naas_config):
    global flag
    flag = False
    response = get_port_Aval_MESH(naas_config=naas_config)
    result = response['resources'][0]['pathElements'][0]['type']
    if result in ['ME', 'ENNI']:
        print("Device ;;", result)
        attributes = response['resources'][0]['pathElements'][0]['subElements'][0]['aendPort']['attributes'][0]
        if attributes['name'] == 'Class':
            assert attributes['value'] in ['Empty Slot', 'Physical']
            flag = True
            print(
                "===================== Mesh - PORT Avalibility Check Completed ===========================================")
    return flag


@then('DIA Product E2E Validation')
@story ("DIA Product E2E Validation")
@description ('DIA E2E')
@pytest.mark.parametrize("scenario_index", range(len(load_scenarios())))
def test_DIA_E2E_Flow(naas_config, data_provider, scenario_index):
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
    dict_output_final = Validate_UNI_v2(naas_config, data_provider,UNI_ID, dict_output = dict_output,scenario_index = scenario_index, update_UNI_response = update_UNI_response )
    global Uni_service_allias
    Uni_service_allias = dict_output_final["asriServiceAlias"]


    # ASRI Validation for UNI
    validate_UNI_ASRI(naas_config, data_provider, Uni_service_allias)

    # load Yaml
    scenarios = load_scenarios()
    scenario = scenarios[scenario_index]
    output_data = scenario["output_data"]
    print("lets check out put data for UNI SL", output_data)

    # ACT Validation for UNI
    validate_UNI_ACT(naas_config, data_provider, output_dict=output_data)

    # load Yaml
    scenarios = load_scenarios()
    scenario = scenarios[scenario_index]
    output_data = scenario["output_data"]
    print("lets check out put data for UNI SL",output_data)


    # FD validation
    #Validate_FD_Task(data_provider, naas_config)

    # Genereate Skinny
    generate_service_alias(naas_config, data_provider)

    # Create SKinny
    Create_skinny(naas_config, data_provider)

    # Assing IP
    assign_IP(naas_config, data_provider)

    # Create Service SL
    Create_Service_SL(PCID,Uni_service_allias, naas_config=naas_config, data_provider=data_provider, input_dict=input_data, scenario_index =scenario_index, update_service_response_id= update_service_response_id, Update_SL_Response = Update_SL_Response)

    # FD Validation
    #Validate_Service_FD_Task(data_provider, naas_config)

    # load Yaml
    scenarios = load_scenarios()
    scenario = scenarios[scenario_index]
    output_data1 = scenario["output_data"]
    print("lets check out put data for service SL", output_data1)


    #Delete Service
    Delete_Service_SL(naas_config=naas_config, data_provider=data_provider, input_dict=input_data)

    #Delete Oline
    Validate_Delete_Oline(naas_config=naas_config, data_provider=data_provider, output_dict1=output_data1)

    #Delete UNI
    Delete_UNI_SL(Uni_service_allias, naas_config=naas_config, data_provider=data_provider)

    #Release IP
    Release_IP(naas_config, data_provider)
