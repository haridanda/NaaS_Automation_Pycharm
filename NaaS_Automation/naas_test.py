import json
import jsonschema

class NaaS_Test():
  def validate_json_schema(self,json,schema):
      jsonschema.validate(json,schema)

  def is_http_200(self,response):
   assert response.status_code == 200

  def is_status_OK(self,response):
   assert response.status_code ==200

  def is_http_204(self,response):
   assert response.status_code == 204

  def is_http_400(self,response):
   assert response.status_code == 400

  def is_http_500(self,response):
   assert response.status_code == 500

  def is_http_422(self, response):
   assert response.status_code == 422

  def is_http_412(self, response):
   assert response.status_code == 412

  def check_error_message(self,response,message):
   assert response['errorDetails'][0]['message'] == message

  def check_no_errors(self, response):
   assert response['errorDetails'] == []

  def check_empty_response(self, response):
   #print("content of response ", response.content)
   #print("Status of response ", response.raise_for_status())
   assert response.raise_for_status() is None