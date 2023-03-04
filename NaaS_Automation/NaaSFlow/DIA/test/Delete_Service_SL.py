import pytest
import requests


@pytest.fixture(scope="class")
def Post_Service_SL():
    url = "https://autopilotapp-test2-01.test.intranet:3443/workflow_engine/startJobWithOptions"
    path = "/LNAAS_DELETE_DIA_SERVICE_SL_V1"
    Host = url + path

    headers = {"Content-Type" : "application/json", "cookie": "token=MjY5YTkyYWIyOWEzMGI1NDU1MzgyN2QyZWI5ZmJlNWQ="}
    print(Host)
    request_body ={
   "options":{
      "description":"",
      "variables":{
         "requestPayload":{
    "parentCorrelationId": "AP-5517337et-0903-DIA-Service-Delete_Hari004",
    "customerName": "SUNDAY UAT",
	"customerNumber": "1-T8BD",
	"orderSource": "SwIFT",
    "productOfferName": "UNI",
	"productInstanceId": "442887980",
	"serviceOrderNumber": "551883180",
	"orderId": "551883180",
    "orderVersion": "1",
    "mainProductId": "442887975",
    "productSubType": "fiber_plus",
    "fulfillmentRequestNumber": "FR0014427-1",
    "customerRequestedDate": "2023-02-19",
    "customerCommittedDate": "2023-02-19",
    "serviceAlias": "CO/IRXX/000330/LUMN",
    "mtu": 1500,
    "wanIPAddressBlocks": [
		{
			"ipVersion":"IPv4",
            "ipAddressBlock":"131.119.27.100/30"
    }
  ],

	"rateLimit": 100

}
      }
   },
   "groups":[

   ],
   "type":"automation"
}
    response = requests.post(Host, json=request_body, headers= headers, verify=False)
    #print(response)
    print(response.status_code)
    #print(response.text)
    yield response

def test_ap_token( Post_Service_SL):
    if Post_Service_SL.status_code == 200:
        print("succcess")
