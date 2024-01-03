


import unittest
import requests
import logging
import uuid
import json
import random
import os

from utils.configloader     import ConfigUtil
from utils.mssqlutil        import MSSQLUtil
from test_generateToken     import TestGenerateToken


class TestPolicyManagement(unittest.TestCase):
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    __envConfiguration = None  # Environment configuration object laoded from ConfigUtil
    _POST_TIMEOUT = 5
    _GET_TIMEOUT = 3
    _NUMBER_OF_USERS = 3 # Total number of users required to be created for paging test-case
    _PAGING_COUNT = f'1to{_NUMBER_OF_USERS}'
    token = ''
    

    @classmethod
    def setUpClass(self):
        instance = ConfigUtil.getInstance()
        self.__envConfiguration = instance.configJSON
        self.log.info('Testing policymanagement.mssql.sca service component')
        self.log.info('Special Config Params')
        self.log.info(f'POST Timeout {self._POST_TIMEOUT} GET Timeout {self._GET_TIMEOUT}')

        self.log.info('Getting access token from test_generateToken')
        TestGenerateToken()
        with open('token.txt', "r") as file:
            self.token = file.read()
            os.remove('token.txt') 

    @classmethod
    def tearDownClass(self):        
        pass

    def setUp(self):
        """ Get's environment variables from the configuration """
        pass
   

    def test_PostUpdateGetDeleteByIDPolicy(self):
        logging.info("Post, Update, Delete by Policy ID")

        """ 
            [TEST-CASE-03]: 
            This test-case Logs in a user with a SIAM token.
            1. Get access token from test_generateToken.py
            2. Create policy
            3. Update policy
            4. Get created policy
            5. Delete policy 
            6. Verify if the policy has been deleted from DB
        """

        rand = random.randint(10000,99999)

        headers = {
            'Content-Type': 'application/json',
            'X-Channel-ID': '',
            'Authorization': f"Bearer {self.token}"
        }
        postURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingagePolicyManagementSCAURL'] == '' else self.__envConfiguration['ingagePolicyManagementSCAURL']}{self.__envConfiguration['ingagePolicyManagementCTXRoot']}?getPolicy=Y"

        self.log.info(f"POST to: {postURL}")

        payload = {
            "name":f"TEMP_PASS_POLICY_TEST{rand}",
            "auth": {
                "customerId": "9211325",
                "authorities": {
                    "login/v2": {
                        "POST": [ "/" ]
                    }
                },
                "attributes": {
                    "passwordExpirySecs": "15552000",
                    "sessionExpirySecs": "900"
                }
            }
        }
        try:
            self.log.info(f"Create policy")

            response = requests.request("POST", postURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
            
            policy_id = response.json()["policy_id"]
            

            putURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingagePolicyManagementSCAURL'] == '' else self.__envConfiguration['ingagePolicyManagementSCAURL']}{self.__envConfiguration['ingagePolicyManagementCTXRoot']}/{policy_id}"
            
            self.log.info(f"PUT to: {putURL}")

            payload = {
                "name":f"UPDATED_TEMP_PASS_POLICY_TEST{rand}",
            }

            self.log.info(f"Updating policy")

            response = requests.request("PUT", putURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
            
            getURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingagePolicyManagementSCAURL'] == '' else self.__envConfiguration['ingagePolicyManagementSCAURL']}{self.__envConfiguration['ingagePolicyManagementCTXRoot']}/{policy_id}"
            self.log.info(f"GET to: {getURL}")

            self.log.info(f"Get policy from API")
            

            response = requests.request("GET", getURL, headers=headers, timeout=self._POST_TIMEOUT)
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}')
            
            dltURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingagePolicyManagementSCAURL'] == '' else self.__envConfiguration['ingagePolicyManagementSCAURL']}{self.__envConfiguration['ingagePolicyManagementCTXRoot']}/{policy_id}"
            self.log.info(f"DELETE to: {dltURL}")

            self.log.info(f"Delete policy")


            response = requests.request("DELETE", dltURL, headers=headers, timeout=self._POST_TIMEOUT)
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}')
            
            self.log.info(f"Check deleted policy from DB")

            selectPolicy = f"SELECT TOP 1 policy_id from [INGAGESIAM].[dbo].[ING_Policy] where policy_id = '{policy_id}'" 
            record = MSSQLUtil.getInstance().executeQuery(selectPolicy)
            if len(record) == 0:
                self.assertEqual(len(record), 0,
                        msg=f"Policy deleted successfully")

            
        except requests.exceptions.HTTPError as ex:
            self.fail(
                f"Error Received error response code form the backend system:{ex}")
        except requests.exceptions.ConnectionError as ex:
            self.fail(f"Error Connecting: {ex}")
        except requests.exceptions.Timeout as ex:
            self.log.error(ex)
            self.fail(f"Timeout Error: {ex}")
        except requests.exceptions.RequestException as ex:
            self.log.error(ex)
            self.fail(f"Request Exception: {ex}")
        except Exception as ex:
            self.log.error(ex)
            self.fail(f"Generic Exception: {ex}")

    def test_PostUpdateGetDeleteByNamePolicy(self):
        logging.info("Post, Update, Delete by Policy Name")

        """ 
            [TEST-CASE-03]: 
            This test-case Logs in a user with a SIAM token.
            1. Get access token from test_generateToken.py
            2. Create policy
            3. Update policy
            4. Get created policy
            5. Delete policy 
            6. Verify if the policy has been deleted from DB
        """

        rand = random.randint(10000,99999)

        headers = {
            'Content-Type': 'application/json',
            'X-Channel-ID': '',
            'Authorization': f"Bearer {self.token}"
        }
        postURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingagePolicyManagementSCAURL'] == '' else self.__envConfiguration['ingagePolicyManagementSCAURL']}{self.__envConfiguration['ingagePolicyManagementCTXRoot']}?getPolicy=Y"

        self.log.info(f"POST to: {postURL}")

        payload = {
            "name":f"TEMP_PASS_POLICY_TEST{rand}",
            "auth": {
                "customerId": "9211325",
                "authorities": {
                    "login/v2": {
                        "POST": [ "/" ]
                    }
                },
                "attributes": {
                    "passwordExpirySecs": "15552000",
                    "sessionExpirySecs": "900"
                }
            }
        }
        try:
            self.log.info(f"Create policy")

            response = requests.request("POST", postURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
            
            policy_id = response.json()["policy_id"]

            putURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingagePolicyManagementSCAURL'] == '' else self.__envConfiguration['ingagePolicyManagementSCAURL']}{self.__envConfiguration['ingagePolicyManagementCTXRoot']}/{policy_id}"
            self.log.info(f"PUT to: {putURL}")

            payload = {
                "name":f"UPDATED_TEMP_PASS_POLICY_TEST{rand}",
            }
            self.log.info(f"Updating policy")

            response = requests.request("PUT", putURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
            
            getURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingagePolicyManagementSCAURL'] == '' else self.__envConfiguration['ingagePolicyManagementSCAURL']}{self.__envConfiguration['ingagePolicyManagementCTXRoot']}/UPDATED_TEMP_PASS_POLICY_TEST{rand}"
            self.log.info(f"GET to: {getURL}")
            self.log.info(f"Get policy from API")

        

            response = requests.request("GET", getURL, headers=headers, timeout=self._POST_TIMEOUT)
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}')
            
            dltURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingagePolicyManagementSCAURL'] == '' else self.__envConfiguration['ingagePolicyManagementSCAURL']}{self.__envConfiguration['ingagePolicyManagementCTXRoot']}/UPDATED_TEMP_PASS_POLICY_TEST{rand}"

            self.log.info(f"DELETE to: {dltURL}")

            self.log.info(f"Delete policy")

            response = requests.request("DELETE", dltURL, headers=headers, timeout=self._POST_TIMEOUT)
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}')
            
            self.log.info(f"Check deleted policy from DB")

            selectPolicy = f"SELECT TOP 1 policy_id from [INGAGESIAM].[dbo].[ING_Policy] where name = 'UPDATED_TEMP_PASS_POLICY_TEST{rand}'" 
            record = MSSQLUtil.getInstance().executeQuery(selectPolicy)
            if len(record) == 0:
                self.assertEqual(len(record), 0,
                        msg=f"Policy deleted successfully")

            
        except requests.exceptions.HTTPError as ex:
            self.fail(
                f"Error Received error response code form the backend system:{ex}")
        except requests.exceptions.ConnectionError as ex:
            self.fail(f"Error Connecting: {ex}")
        except requests.exceptions.Timeout as ex:
            self.log.error(ex)
            self.fail(f"Timeout Error: {ex}")
        except requests.exceptions.RequestException as ex:
            self.log.error(ex)
            self.fail(f"Request Exception: {ex}")
        except Exception as ex:
            self.log.error(ex)
            self.fail(f"Generic Exception: {ex}")

    def test_GetAllPolicies(self):
        logging.info("Get all policies")

        """ 
            [TEST-CASE-03]: 
            1. Get access token from test_generateToken.py
            2. Get all policies

        """

    
        headers = {
            'Content-Type': 'application/json',
            'X-Channel-ID': '',
            'Authorization': f"Bearer {self.token}"
        }

        getURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingagePolicyManagementSCAURL'] == '' else self.__envConfiguration['ingagePolicyManagementSCAURL']}{self.__envConfiguration['ingagePolicyManagementCTXRoot']}"

        self.log.info(f"GET to: {getURL}")

        try:
            self.log.info(f"Get all policies")

            response = requests.request("GET", getURL, headers=headers, timeout=self._POST_TIMEOUT)
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
            
        except requests.exceptions.HTTPError as ex:
            self.fail(
                f"Error Received error response code form the backend system:{ex}")
        except requests.exceptions.ConnectionError as ex:
            self.fail(f"Error Connecting: {ex}")
        except requests.exceptions.Timeout as ex:
            self.log.error(ex)
            self.fail(f"Timeout Error: {ex}")
        except requests.exceptions.RequestException as ex:
            self.log.error(ex)
            self.fail(f"Request Exception: {ex}")
        except Exception as ex:
            self.log.error(ex)
            self.fail(f"Generic Exception: {ex}")


if __name__ == '__main__':
    unittest.main()