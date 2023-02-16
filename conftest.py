import pytest, os
from conf.config.naas_config import NaaSConfig
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
