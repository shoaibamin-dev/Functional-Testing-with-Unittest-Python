


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
        self.log.info('Testing login.mssql.sca service component')
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
   

    def test_LoginWithInvalidCredentials(self):
        logging.info("Login with invalid credentials user")

        """ 
            [TEST-CASE-02]: 
            This test-case Logs in a user with a SIAM token.
            1. Get access token from test_generateToken.py
            2. Get temp policy from DB
            3. Creater User
            4. Set user password
            5. Reset user password 
            6. Get Login policy from DB
            7. Create user token through temporary and user policies
            8. Login user with invalid and receive access token

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
            self.log.info(f"Get temp policy from DB")

            getTempPolicy = f"SELECT TOP 1 policy_id from [INGAGESIAM].[dbo].[ING_Policy] where name like 'TEMP%'" 
            record = MSSQLUtil.getInstance().executeQuery(getTempPolicy)

            policy_id = record[0][0]
            self.log.info(f"Get admin policy from DB")

            getAdminPolicy = f"SELECT TOP 1 policy_id from [INGAGESIAM].[dbo].[ING_Policy] where name = 'SYS_API_ADMIN'" 
            record = MSSQLUtil.getInstance().executeQuery(getAdminPolicy)

            admin_policy_id = record[0][0]

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
            self.log.info(f"Create User")

            postURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}"

            self.log.info(f"POST to: {postURL}")

            response = requests.request("POST", postURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
            self.log.info(f"Set user password")

            putURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/testadmin{rand}/password"
            self.log.info(f"PUT to: {putURL}")

            response = requests.request("PUT", putURL, headers=headers, timeout=self._POST_TIMEOUT)
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 


            temp_password = response.json()["password"]
           
            putURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/testadmin{rand}/reset/password"
            

            payload = {  
                "oldPass": temp_password,
                "newPass": "P@ssw0rd$" 
            }
            self.log.info(f"Reset user password")

            response = requests.request("PUT", putURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
           
            payload = {
                "login": {        
                    "client_secret": "none",
                    "grant_type": "password",
                    "username": f"testadmin{rand}",
                    "password": "P@ssw0rd$err"
                }
            }

            postURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageLoginSCAURL'] == '' else self.__envConfiguration['ingageLoginSCAURL']}{self.__envConfiguration['ingageLoginCTXRoot']}"

            self.log.info(f"POST to: {postURL}")
            response = requests.request("POST", postURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 404,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 

            self.log.info(f"Delete user")

            dltURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/testadmin{rand}"
            
            self.log.info(f"DELETE to: {dltURL}")


            response = requests.request("DELETE", dltURL, headers=headers, timeout=self._POST_TIMEOUT)
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
           
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

    def test_LoginWithValidCredentials(self):
        logging.info("Login with vvalid credentials user")

        """ 
            [TEST-CASE-01]: 
            This test-case Logs in a user with a SIAM token.
            1. Get access token from test_generateToken.py
            2. Get temp policy from DB
            3. Creater User
            4. Set user password
            5. Reset user password 
            6. Get Login policy from DB
            7. Create user token through temporary and user policies
            8. Login user and receive access token

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
            
            self.log.info(f"Get temp policy from DB")

            getTempPolicy = f"SELECT TOP 1 policy_id from [INGAGESIAM].[dbo].[ING_Policy] where name like 'TEMP%'" 
            record = MSSQLUtil.getInstance().executeQuery(getTempPolicy)

            policy_id = record[0][0]

            self.log.info(f"Get admin policy from DB")

            getAdminPolicy = f"SELECT TOP 1 policy_id from [INGAGESIAM].[dbo].[ING_Policy] where name = 'SYS_API_ADMIN'" 
            record = MSSQLUtil.getInstance().executeQuery(getAdminPolicy)

            admin_policy_id = record[0][0]

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


            self.log.info(f"Create User")

            postURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}"

            self.log.info(f"POST to: {postURL}")

            response = requests.request("POST", postURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 

            self.log.info(f"Set user password")

            putURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/testadmin{rand}/password"

            self.log.info(f"PUT to: {putURL}")

            response = requests.request("PUT", putURL, headers=headers, timeout=self._POST_TIMEOUT)
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 


            temp_password = response.json()["password"]
           
            putURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/testadmin{rand}/reset/password"
            

            payload = {  
                "oldPass": temp_password,
                "newPass": "P@ssw0rd$" 
            }

            self.log.info(f"Reset user password")

            response = requests.request("PUT", putURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
           
            payload = {
                "login": {        
                    "client_secret": "none",
                    "grant_type": "password",
                    "username": f"testadmin{rand}",
                    "password": "P@ssw0rd$"
                }
            }

            postURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageLoginSCAURL'] == '' else self.__envConfiguration['ingageLoginSCAURL']}{self.__envConfiguration['ingageLoginCTXRoot']}"

            self.log.info(f"POST to: {postURL}")

            response = requests.request("POST", postURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 

            self.log.info(f"Delete user")

            dltURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/testadmin{rand}"
            
            self.log.info(f"DELETE to: {dltURL}")


            response = requests.request("DELETE", dltURL, headers=headers, timeout=self._POST_TIMEOUT)
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
           
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

    def test_LockUser(self):
        logging.info("Lock user by logging in multiple times")

        """ 
            [TEST-CASE-03]: 
            This test-case Logs in a user with a SIAM token.
            1. Get access token from test_generateToken.py
            2. Get temp policy from DB
            3. Creater User
            4. Set user password
            5. Reset user password 
            6. Get Login policy from DB
            7. Create user token through temporary and user policies
            8. Login multiple times user and receive access token

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
            self.log.info(f"Get temp policy from DB")

            getTempPolicy = f"SELECT TOP 1 policy_id from [INGAGESIAM].[dbo].[ING_Policy] where name like 'TEMP%'" 
            record = MSSQLUtil.getInstance().executeQuery(getTempPolicy)

            policy_id = record[0][0]

            getAdminPolicy = f"SELECT TOP 1 policy_id from [INGAGESIAM].[dbo].[ING_Policy] where name = 'SYS_API_ADMIN'" 
            record = MSSQLUtil.getInstance().executeQuery(getAdminPolicy)

            admin_policy_id = record[0][0]

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
            self.log.info(f"Create User")

            postURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}"


            response = requests.request("POST", postURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
            self.log.info(f"POST to: {postURL}")

            putURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/testadmin{rand}/password"

            response = requests.request("PUT", putURL, headers=headers, timeout=self._POST_TIMEOUT)
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 

            self.log.info(f"Set user password")
            self.log.info(f"PUT to: {putURL}")

            temp_password = response.json()["password"]
            
        
            putURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/testadmin{rand}/reset/password"
            

            payload = {  
                "oldPass": temp_password,
                "newPass": "P@ssw0rd$" 
            }
            self.log.info(f"Reset user password")

            response = requests.request("PUT", putURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
        
            payload = {
                "login": {        
                    "client_secret": "none",
                    "grant_type": "password",
                    "username": f"testadmin{rand}",
                    "password": "P@ssw0rd$err"
                }
            }

            self.log.info(f"POST to: {postURL}")

            postURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageLoginSCAURL'] == '' else self.__envConfiguration['ingageLoginSCAURL']}{self.__envConfiguration['ingageLoginCTXRoot']}"
            
            for i in range(3):
                response = requests.request("POST", postURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            
            
            self.assertEqual(response.status_code, 404,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 

            self.log.info(f"Delete user")

            dltURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/testadmin{rand}"
            
            self.log.info(f"DELETE to: {dltURL}")


            response = requests.request("DELETE", dltURL, headers=headers, timeout=self._POST_TIMEOUT)
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
        
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


if __name__ == '__main__':
    unittest.main()