class ProtectoAPI:
    @staticmethod
    def insert_or_update_scan_metadata(object_name, fields_to_update):
        result = {"is_scan_submitted": True, "message": "Updated fields successfully and submitted to scan"}
        return result

    @staticmethod
    def get_list_of_objects():
        result = ["User", "Case"]
        return result

    @staticmethod
    def get_list_of_fields_for_object(object_name):
         """
         object_name: "User",
         page_no:1,
         page_size:10
         """
         result=[{"field":"Username","type":"Text","is_selected":False},{"field":"Email","type":"email","is_selected":True}]
         return result

    @staticmethod
    def is_scan_submitted(object_name):
        result = {"is_scan_submitted": True, "total_records": 1000}
        return result

    @staticmethod
    def submit_to_scan(object_name):
        result = {"is_scan_submitted": True}
        return result

    @staticmethod
    def get_scan_progress():
        result=[{
        "request_id":"12wer34kwq",
        "object_name":"User",
        "criteria":"case_date< 8/3/2015 AND geo=“EU”​",
        "total_count":200000,
        "scanned_count":20,
        "status":"Success",
        "last_updated_time":"22-04-2024T01:12:00.0000"
    },{
        "request_id":"12wer345kwq",
        "object_name":"Case",
        "criteria":"case_date< 8/3/2015 AND geo=“EU”​",
        "total_count":200000,
        "scanned_count":20,
        "status":"Failed",
        "last_updated_time":"22-04-2024T01:12:00.0000"
    }]
        return result

    @staticmethod
    def retry_failed_object(request_id):
        result = [{
            "request_id": "12wer34kwq",
            "object_name": "User",
            "total_count": 200000,
            "scanned_count": 20,
            "status": "Success",
            "last_updated_time": "22-04-2024T01:12:00.0000",
            "error": '',
            "retry": False
        }, {
            "request_id": "12wer345kwq",
            "object_name": "Case",
            "total_count": 200000,
            "scanned_count": 20,
            "status": "Retrying",
            "last_updated_time": "22-04-2024T01:12:00.0000",
            "error": '',
            "retry": True
        },{
            "request_id": "12wer345kw3",
            "object_name": "Case",
            "total_count": 20003440,
            "scanned_count": 700,
            "status": "Retrying",
            "last_updated_time": "22-04-2024T01:12:00.0000",
            "error": '',
            "retry": True
        }
        ]
        return result

    @staticmethod
    def update_mask_metadata(object_name, query, fields_to_update):
        result = {"is_rows_selected_for_masking": True, "message": "Updated Metadata successfully and scheduled rows for masking"}
        return result

    @staticmethod
    def get_metadata_for_mask(object_name):
        result = {
            "query": "case_date< 8/3/2015 AND geo='EU'", 
            "field_metadata": [{
                "field": "Username",
                "pii_identified": ["PERSON", "ORG"],
                "override_pii": "PERSON",
                "to_be_masked": False,
                "samples": ["John", "Adam", "Mary", "Jacob"]
            }, {
                "field": "Email",
                "pii_identified": ["Email"],
                "override_pii": None,
                "to_be_masked": True,
                "samples": ["john@email.com", "adam@email.com", "mary@email.com", "jacob@email.com"]
            }]
        }
        return result

    @staticmethod
    def is_rows_selected_for_masking(object_name):
        result = {
            "is_rows_selected_for_masking": False,
            "total_records": 1000,
            "override_pii_list": ["PERSON", "EMAIL", "NO PII", "URL", "ADDRESS", "PHONE"]
        }
        return result

    @staticmethod
    def select_rows_for_masking(object_name):
        result = {"is_rows_selected_for_masking": True}
        return result

    @staticmethod
    def get_objects_and_query_scheduled_for_masking():
        result = [
            {"object_name": "User", "query": "case_date< 8/3/2015 AND geo='EU'"},
            {"object_name": "Case", "query": "case_date< 8/3/2015 AND geo='EU'"}
        ]
        return result

    @staticmethod
    def is_approve_and_retry_enabled(object_name):
        result = {
            "total_records": 100,
            "is_retry_enabled": True,
            "is_approve_enabled": True,
            "is_masked_list": ["to_be_masked", "no_mask"]
        }
        return result

    @staticmethod
    def get_query_execution_result(object_name):
        result = {
            "records": [{
                "attributes": {
                    "type": "User",
                    "url": "/services/data/v42.0/sobjects/User/0053h000000QZL3AAO"
                },
                "Id": "0053h000000QZL3AAO",
                "Username": "gowtham.kamanaveera.ext@singlecrm.nokia.com.qa1",
                "LastName": "Kamanaveera",
                "FirstName": "Gowtham",
                "MiddleName": None,
                "Suffix": None,
                "Name": "Gowtham Kamanaveera",
                "CompanyName": "Nokia",
                "Division": "NSW Applications Services & Care",
                "Department": "NSW AS&C DE CC Central Del IOT",
                "Title": "EXT-Consultant",
                "Street": "Manyata Embassy Business Park",
                "City": "Bangalore",
                "State": None,
                "PostalCode": "560045",
                "Country": "India",
                "StateCode": None,
                "CountryCode": "IN",
                "Latitude": None,
                "Longitude": None,
                "GeocodeAccuracy": None,
                "Address": {
                    "city": "Bangalore",
                    "country": "India",
                    "countryCode": "IN",
                    "geocodeAccuracy": None,
                    "latitude": None,
                    "longitude": None,
                    "postalCode": "560045",
                    "state": None,
                    "stateCode": None,
                    "street": "Manyata Embassy Business Park"
                },
                "Email": "gowtham.kamanaveera.ext@nokia.com.invalid",
                "is_masked": "to_be_masked",
                "error": "",
                "retry": True
            }]
        }
        return result

    @staticmethod
    def update_no_mask_for_record(object_name, record_ids):
        result = {"message": "updated no_mask for selected records"}
        return result

    @staticmethod
    def approve_for_masking(object_name):
        result = {"is_approve_enabled": False, "message": "Approval in progress"}
        return result

    @staticmethod
    def retry_for_masking(object_name, retry_all, record_ids):
        result = {"is_retry_enabled": False, "message": "Retry in progress"}
        return result

    @staticmethod
    def get_mask_progress():
        result = [{
            "request_id": "12wer34kwq",
            "object_name": "User",
            "criteria": "case_date< 8/3/2015 AND geo='EU'",
            "status": "Success",
            "last_updated_time": "22-04-2024T01:12:00.0000",
            "total_no_of_rows_approved_for_masking": 100,
            "total_masked_value": 10
        }, {
            "request_id": "12wer345kwq",
            "object_name": "Case",
            "criteria": "case_date< 8/3/2015 AND geo='EU'",
            "status": "Failed",
            "last_updated_time": "22-04-2024T01:12:00.0000",
            "total_no_of_rows_approved_for_masking": 100,
            "total_masked_value": 10
        }]
        return result

    @staticmethod
    def download_records(object_name):
          """
          object_name: "User"
          """
          result=[{
          "attributes": {
            "type": "User",
            "url": "/services/data/v42.0/sobjects/User/0053h000000QZL3AAO"
          },
          "Id": "0053h000000QZL3AAO",
          "Username": "gowtham.kamanaveera.ext@singlecrm.nokia.com.qa1",
          "LastName": "Kamanaveera",
          "FirstName": "Gowtham",
          "MiddleName": None,
          "Suffix": None,
          "Name": "Gowtham Kamanaveera",
          "CompanyName": "Nokia",
          "Division": "NSW Applications Services & Care",
          "Department": "NSW AS&C DE CC Central Del IOT",
          "Title": "EXT-Consultant",
          "Street": "Manyata Embassy Business Park",
          "City": "Bangalore",
          "State": None,
          "PostalCode": "560045",
          "Country": "India",
          "StateCode": None,
          "CountryCode": "IN",
          "Latitude": None,
          "Longitude": None,
          "GeocodeAccuracy": None,
          "Address": {
            "city": "Bangalore",
            "country": "India",
            "countryCode": "IN",
            "geocodeAccuracy": None,
            "latitude": None,
            "longitude": None,
            "postalCode": "560045",
            "state": None,
            "stateCode": None,
            "street": "Manyata Embassy Business Park"
          },
          "Email": "gowtham.kamanaveera.ext@nokia.com.invalid",
          "protecto_status":"scanned",
          "error":"",
          "retry":True
        }
          ]
          return result