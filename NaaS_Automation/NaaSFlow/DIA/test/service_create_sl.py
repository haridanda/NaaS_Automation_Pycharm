import json
import pytest
import requests
from pytest_bdd import given, when, then
import time
from conf.data import constant
from NaaS_Automation.NaaSFlow.DIA.test.constants import *
from NaaS_Automation.NaaSFlow.DIA.test.utils import get_data,write_data,get_port_Aval_MESH,get_cookies


#@pytest.mark.parametrize("input_dict", get_data(file = path))
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
    request_body['options']['variables']['requestPayload']['serviceAlias'] = ""
    request_body['options']['variables']['requestPayload']['wanIPAddressBlocks'][0]['ipAddressBlock'] = ""
    # request_body['options']['variables']['requestPayload']['failFast'] = input_dict['failFast']
    print(request_body)
    headers = data_provider.get_nested_node(["naas", "requestHeaders"])
    response = requests.post(AP_start_job_url, json=request_body, headers=headers, verify=False, cookies=get_cookies())
    response_json = response.json()
    global SL_id
    SL_id = response_json["_id"]
    print("SL ID ", SL_id)
    return SL_id

@then (u'Validate Service SL')
@pytest.mark.parametrize("input_dict", get_data(file = path))
def test_Create_Service_SL ( naas_config, data_provider, input_dict):
    global SL_ID
    SL_ID = Create_DIA_Service_SL(naas_config= naas_config, data_provider= data_provider, input_dict= input_dict)
    AP_status_Url = naas_config.get_server("autopilot")+ workflow_status + SL_ID
    response = requests.get(AP_status_Url, verify=False, cookies=get_cookies())
    response_json = response.json()
    validate_status(response_json = response_json['tasks'], status='workflow_end', AP_status_Url= AP_status_Url,cookies=get_cookies() )
    dict_output= {}
    dict_output['sno'] = input_dict['sno']
    print(response_json["status"])
    print("Service ID",SL_ID)
    dict_output['id'] = SL_ID
    dict_output_final = Validate_SL(naas_config, data_provider,dict_output)
    write_data(path, input_dict['sno'], dict_output=dict_output_final)

def Validate_SL_Zero(naas_config, data_provider, dict_output):
    id = '6971e7a54cd0475a8de003ef'
    #ba97bfff9d7847d385591aaa ec7a110c60944746883e8507
    AP_validate_Url = naas_config.get_server("autopilot") + workflow_search
    request_body = data_provider.get_nested_node(["naas", "validate_UNI"])
    request_body['filter']['job._id'] = id
    response = requests.post(AP_validate_Url, json=request_body, verify=False, cookies=get_cookies())
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

def Validate_SL(naas_config, data_provider, dict_output):
    AP_validate_Url = naas_config.get_server("autopilot") + workflow_search
    request_body = data_provider.get_nested_node(["naas", "validate_UNI"])
    request_body['filter']['job._id'] = SL_ID
    print(request_body)
    response = requests.post(AP_validate_Url, json=request_body, verify=False, cookies=get_cookies())
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