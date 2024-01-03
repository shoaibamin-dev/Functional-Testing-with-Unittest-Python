


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


class TestUserManagement(unittest.TestCase):
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
        self.log.info('Testing usermanagement.mssql.sca service component')
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
   

    def test_CreateUpdateGetDeleteUser(self):
        logging.info("Post, Update, Get, Delete user")

        """ 
            [TEST-CASE-01]: 
            This test-case Logs in a user with a SIAM token.
            1. Get access token from test_generateToken.py
            2. Create User, set temp pass, reset password
            3. Update User
            4. Get created User
            5. Delete User 
            6. Verify if the user has been deleted from DB
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
            self.log.info(f"Get temporary policy from DB")

            getTempPolicy = f"SELECT TOP 1 policy_id from [INGAGESIAM].[dbo].[ING_Policy] where name like 'TEMP%'" 
            record = MSSQLUtil.getInstance().executeQuery(getTempPolicy)

            policy_id = record[0][0]
            self.log.info(f"Get admin policy from DB")

            getAdminPolicy = f"SELECT TOP 1 policy_id from [INGAGESIAM].[dbo].[ING_Policy] where name = 'SYS_API_ADMIN'" 
            record = MSSQLUtil.getInstance().executeQuery(getAdminPolicy)

            admin_policy_id = record[0][0]
            
            self.log.info(f"Create User")

            payload = {    
                "user_id":f"testadmin{rand}",        
                "first_name": "Admin",
                "last_name": "User",
                "email_id": f"testadmin{rand}@mail.com",
                "mobileNo": f"0000000{rand}",
                "meta": {
                    "user_policy": admin_policy_id
                },
                "policy_id": policy_id
            }

            postURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}"
            self.log.info(f"POST to: {postURL}")


            response = requests.request("POST", postURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 

            putURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/testadmin{rand}/password"

            self.log.info(f"PUT to: {putURL}")

            response = requests.request("PUT", putURL, headers=headers, timeout=self._POST_TIMEOUT)
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 


            temp_password = response.json()["password"]
           
            putURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/testadmin{rand}/reset/password"
            
            self.log.info(f"PUT to: {putURL}")

            payload = {  
                "oldPass": temp_password,
                "newPass": "P@ssw0rd$" 
            }

            response = requests.request("PUT", putURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
           
            getURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/testadmin{rand}"
            

            self.log.info(f"GET to: {getURL}")

            response = requests.request("GET", getURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
           
            dltURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/testadmin{rand}"
            


            response = requests.request("DELETE", dltURL, headers=headers, timeout=self._POST_TIMEOUT)
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
           
            self.log.info(f"Verify user deletion from DB")

            # select USER
            selectUser = f"SELECT TOP 1 policy_id from [INGAGESIAM].[dbo].[ING_USER] where user_id = 'testadmin{rand}'" 
            record = MSSQLUtil.getInstance().executeQuery(selectUser)
            if len(record) == 0:
                self.assertEqual(len(record), 0,
                        msg=f"User deleted successfully")



            
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

    def test_GetAllUsers(self):
        logging.info("Get all users")

        """ 
            [TEST-CASE-01]: 
            This test-case creates a SIAM token. 
        """

    
        headers = {
            'Content-Type': 'application/json',
            'X-Channel-ID': '',
            'Authorization': f"Bearer {self.token}"
        }

        getURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}"
        self.log.info(f"Get all users from API provided access token")

        self.log.info(f"GET to: {getURL}")

        try:
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