


import unittest
import requests
import logging
import uuid
import json
import random

from utils.configloader     import ConfigUtil
from utils.mssqlutil        import MSSQLUtil


class TestGenerateToken(unittest.TestCase):
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    __envConfiguration = None  # Environment configuration object laoded from ConfigUtil
    _POST_TIMEOUT = 5
    _GET_TIMEOUT = 3
    _NUMBER_OF_USERS = 3 # Total number of users required to be created for paging test-case
    _PAGING_COUNT = f'1to{_NUMBER_OF_USERS}'

    @classmethod
    def setUpClass(self):
        instance = ConfigUtil.getInstance()
        self.__envConfiguration = instance.configJSON
        self.log.info('Generating and saving the token to a temporary file')
        self.log.info('Special Config Params')
        self.log.info(f'POST Timeout {self._POST_TIMEOUT} GET Timeout {self._GET_TIMEOUT}')

    @classmethod
    def tearDownClass(self):        
        pass

    def setUp(self):
        """ Get's environment variables from the configuration """
        pass
   

    def test_GenerateAndReturnToken(self):
        logging.info("Considering AUTHZ_ENABLED is false")

        """ 
            [TEST-CASE-01]: 
            This test-case creates a SIAM token.
            1. Create temporary policy
            2. Get Admin policy from DB
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
            'X-Channel-ID': ''
        }

        
        self.log.info(f"1. Create temporary policy")

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
            response = requests.request("POST", postURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
            
            policy_id = response.json()["policy_id"]

            self.log.info(f"2. Get SYS_API_ADMIN policy from DB")

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

            self.log.info(f"3. Create user")

            postURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}"

            self.log.info(f"POST to: {postURL}")


            response = requests.request("POST", postURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 


            self.log.info(f"4. Set Password")

            putURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/testadmin{rand}/password"
            self.log.info(f"PUT to: {putURL}")


            response = requests.request("PUT", putURL, headers=headers, timeout=self._POST_TIMEOUT)
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 


            temp_password = response.json()["password"]
            
            self.log.info(f"5. Reset Password")
           
            putURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/testadmin{rand}/reset/password"
            

            self.log.info(f"PUT to: {putURL}")

            payload = {  
                "oldPass": temp_password,
                "newPass": "P@ssw0rd$" 
            }

            response = requests.request("PUT", putURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
            
            self.log.info(f"Get log in policy")
            
            getLoginPolicy = f"SELECT TOP 1 policy_id from [INGAGESIAM].[dbo].[ING_Policy] where name = 'SYS_API_LOGINONLY'" 
            record = MSSQLUtil.getInstance().executeQuery(getLoginPolicy)

            login_policy_id = record[0][0]

            payload = {
                "policy_id": login_policy_id,    
                "meta": {
                    "description": "Token for testing purpose only"
                }
            }

            self.log.info(f"Create user token with temporary and user policies")

            postURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageUserManagementSCAURL'] == '' else self.__envConfiguration['ingageUserManagementSCAURL']}{self.__envConfiguration['ingageUserManagementCTXRoot']}/admin/token"


            self.log.info(f"POST to: {postURL}")
            

            response = requests.request("POST", postURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
            
            access_token = response.json()["access_token"]
           
            payload = {
                "login": {        
                    "client_secret": "none",
                    "grant_type": "password",
                    "username": f"testadmin{rand}",
                    "password": "P@ssw0rd$"
                }
            }
            self.log.info(f"Login user")

            postURL = f"{self.__envConfiguration['inagaeBaseURL'] if self.__envConfiguration['ingageLoginSCAURL'] == '' else self.__envConfiguration['ingageLoginSCAURL']}{self.__envConfiguration['ingageLoginCTXRoot']}"

            response = requests.request("POST", postURL, headers=headers, timeout=self._POST_TIMEOUT, data=json.dumps(payload))
            self.assertEqual(response.status_code, 200,
                                msg=f'Error response received from the server: {response.status_code} and {response.text}') 
            self.log.info(f"POST to: {postURL}")
            
            token = response.json()["token"]
            print('ACCESS TOKEN: ',token)
            with open('token.txt', "w") as file:
                file.write(token)
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