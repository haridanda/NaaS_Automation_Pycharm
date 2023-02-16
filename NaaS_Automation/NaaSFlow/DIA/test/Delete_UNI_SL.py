import pytest
import requests


@pytest.fixture(scope="class")
def Post_UNI_SL():
    url = "https://autopilotapp-test1-01.test.intranet:3443/workflow_engine/startJobWithOptions"
    path = "/LNAAS_DELETE_UNI_SL_V1"
    Host = url + path

    headers = {"Content-Type" : "application/json", "cookie": "token=NWJkMWM4YWQxOGE1N2E0NTZjMmE0MGJjOTFlMmIyYjA="}
    print(Host)
    request_body = {
   "options":{
      "description":"",
      "variables":{
  "requestPayload": {
    "parentCorrelationId": "AP-552694703-2-Pytest-DELETE-UNI-Hari004",
    "customerName": "Level 3 Demo and Testing",
    "customerEID": "966529",
    "orderSource": "AutoPilot",
    "productOfferName": "UNI",
    "productInstanceId": "10084-UNI01-1052",
    "serviceOrderNumber": "15678",
    "orderId": "552694703",
    "orderVersion": "1",
    "mainProductId": "15678",
    "fulfillmentRequestNumber": "15678",
    "customerRequestedDate": "2021-06-13",
    "customerCommittedDate": "2021-06-13",
    "productSubType": "port",
    "serviceAlias": "CO/KXFN/000809/LUMN"
  }
}
   },
   "groups":[

   ],
   "type":"automation"
}
    response = requests.post(Host, json=request_body, headers= headers, verify=False)
    print(response)
    print(response.status_code)
    print(response.text)
    yield response

def test_ap_token( Post_UNI_SL):
    if Post_UNI_SL.status_code == 200:
        print("succcess")
