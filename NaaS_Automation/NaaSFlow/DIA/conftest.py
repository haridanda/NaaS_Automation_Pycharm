import pytest

from NaaS_Automation.NaaSFlow.DIA.utils.common_asserts import CommonAsserts

@pytest.fixture(scope="module")
def dia_common_asserts():
    return CommonAsserts()