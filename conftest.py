import json
import pytest
import requests
from NaaS_Automation.NaaSFlow.DIA.utils.constants import login
from conf.config.naas_config import NaaSConfig
from conf.data import constant
from conf.data.dataprovider import DataProvider
from NaaS_Automation.naas_test import NaaS_Test

@pytest.fixture(scope="session")
def naas_config():
    """All Config in conf diretory are loaded to this object"""
    return NaaSConfig()

@pytest.fixture(scope="session")
def data_provider():
    """Data in conf/data are avalible in this object"""
    return DataProvider()

@pytest.fixture(scope="session")
def naas_test():
    """Data in conf/data are avalible in this object"""
    return NaaS_Test()

@pytest.fixture(scope="session")
def get_AP_token(naas_config, data_provider):
    print("\n ===================== AP Login  ===========================================")
    login_url = naas_config.get_server("autopilot") + login
    print("AP Login URL", login_url)
    request_body = {"user": {"username": constant.user, "password": constant.password}}
    headers = {"Content-Type": "application/json"}
    response = requests.post(login_url, json=request_body, headers=headers, verify=False)
    cookies_dict = response.cookies.get_dict()
    with open("API_token.json", "w") as token:
        token.write(json.dumps(cookies_dict))
    return response

