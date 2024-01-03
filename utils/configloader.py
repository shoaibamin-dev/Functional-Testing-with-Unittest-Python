
from environs               import Env
from marshmallow.validate   import Length

class ConfigUtil:

    __instance      = None
    configJSON     = {
        ## Load all configurations here        
        "module.description": "", # PIN_MODULE_DESCRIPTION
        "module.version": "", # PIN_MODULE_VERSION
        "db.host": "",      # PIN_MSSQL_HOST
        "db.name": "",      # PIN_MSSQL_NAME
        "db.port": 0,       # PIN_MSSQL_PORT
        "db.user": "",      # PIN_MSSQL_USER
        "db.password": "",  # PIN_MSSQL_PASS
        "db.stmttimeout": "", # PIN_MSSQL_STMT_TIMEOUT
        "inagaeBaseURL": "", #  ING_UT_BASE_URL
        "ingageUserMgmtSCAURL" : "", # ING_UT_USERMGMTSCA_URL
        "ingageUserMgmtCTXRoot": "", # ING_UT_USERMGMTSCA_CTX
        "ingageUserMgmtTimeout": 0 # ING_UT_USERMGMTSCA_TIMEOUT
        }
        
    @staticmethod
    def getInstance():
        """ Static access method for gettign the class isntance """
        if ConfigUtil.__instance == None:
            ConfigUtil()
        return ConfigUtil.__instance        

    def __init__(self):
        if ConfigUtil.__instance == None:
            ConfigUtil.__instance = self            
            self.__loadEnvironmentVariables()            

    def __loadEnvironmentVariables(self):
        """ Loads environment variables in configJSON dictionary """        
        env = Env()
        env.read_env()
        # Database Related Variablees
        self.configJSON['module.description'] = env.str('PIN_MODULE_DESCRIPTION',default='auditlog.processor',validate=[Length(min=1,max=128, error='Invalid module name. Should not be > 128 chars')])
        self.configJSON['module.version'] = env.str('PIN_MODULE_VERSION',default='0.1.0-alpha.02',validate=[Length(min=1,max=128, error='Invalid module version. Should not be > 128 chars')])        
        self.configJSON['db.host'] = env.str('PIN_MSSQL_HOST',validate=[Length(min=1,max=128, error='Invalid datbase hostname')])
        self.configJSON['db.name'] = env.str('PIN_MSSQL_NAME',validate=[Length(min=1,max=128, error='Invalid datbase name')])
        self.configJSON['db.port'] = env.int('PIN_MSSQL_PORT')
        self.configJSON['db.user'] = env.str('PIN_MSSQL_USER',validate=[Length(min=1,max=128, error='Invalid datbase username')])
        self.configJSON['db.password'] = env.str('PIN_MSSQL_PASS',validate=[Length(min=1,max=128, error='Invalid datbase password')])
        self.configJSON['db.stmttimeout'] = env.int('PIN_MSSQL_STMT_TIMEOUT',60)
        # Write project specific configuration items below:
        self.configJSON['inagaeBaseURL'] = env.str('ING_UT_BASE_URL',default='')
        # User Management Service Component
        self.configJSON['ingageUserMgmtSCAURL'] = env.str('ING_UT_USERMGMTSCA_URL',default='')
        self.configJSON['ingageUserMgmtCTXRoot'] = env.str('ING_UT_USERMGMTSCA_CTX')        
        self.configJSON['ingageUserMgmtTimeout'] = env.int('ING_UT_USERMGMTSCA_TIMEOUT', default=3)
        # Login Service Component
        self.configJSON['ingageLoginSCAURL'] = env.str('ING_UT_LOGIN_URL',default='')
        self.configJSON['ingageLoginCTXRoot'] = env.str('ING_UT_LOGIN_CTX')        
        self.configJSON['ingageLoginTimeout'] = env.int('ING_UT_LOGIN_TIMEOUT', default=3)
        # Image Store Service Component
        self.configJSON['ingageImageRepoSCAURL'] = env.str('ING_UT_IMAGESTORE_URL',default='')
        self.configJSON['ingageImageRepoCTXRoot'] = env.str('ING_UT_IMAGESTORE_CTX')        
        self.configJSON['ingageImageRepoTimeout'] = env.int('ING_UT_IMAGESTORE_TIMEOUT', default=3)
        # Account Service Component
        self.configJSON['ingageAcctSCAURL'] = env.str('ING_UT_ACCT_URL',default='')
        self.configJSON['ingageAcctCTXRoot'] = env.str('ING_UT_ACCT_CTX')        
        self.configJSON['ingageAcctTimeout'] = env.int('ING_UT_ACCT_TIMEOUT', default=3)
        # Business Params Service Component
        self.configJSON['ingageBusinessParamsSCAURL'] = env.str('ING_UT_BUSINESSPARAMS_URL',default='')
        self.configJSON['ingageBusinessParamsCTXRoot'] = env.str('ING_UT_BUSINESSPARAMS_CTX')        
        self.configJSON['ingageBusinessParamsTimeout'] = env.int('ING_UT_BUSINESSPARAMS_TIMEOUT', default=3)
        # Transaction Insight Service Component
        self.configJSON['ingageTxnInsightSCAURL'] = env.str('ING_UT_TXNINSIGHT_URL',default='')
        self.configJSON['ingageTxnInsightCTXRoot'] = env.str('ING_UT_TXNINSIGHT_CTX')        
        self.configJSON['ingageTxnInsightTimeout'] = env.int('ING_UT_TXNINSIGHT_TIMEOUT', default=3)
        # Product Service Component
        self.configJSON['ingageProductSCAURL'] = env.str('ING_UT_PRODUCT_URL',default='')
        self.configJSON['ingageProductCTXRoot'] = env.str('ING_UT_PRODUCT_CTX')        
        self.configJSON['ingageProductTimeout'] = env.int('ING_UT_PRODUCT_TIMEOUT', default=3)
        # Enrich Transaction Service Component
        self.configJSON['ingageEnrichTransactionSCAURL'] = env.str('ING_UT_ENRICHTRANSACTION_URL',default='')
        self.configJSON['ingageEnrichTransactionCTXRoot'] = env.str('ING_UT_ENRICHTRANSACTION_CTX')        
        self.configJSON['ingageEnrichTransactionTimeout'] = env.int('ING_UT_ENRICHTRANSACTION_TIMEOUT', default=3)
        # Policy Management Service Component
        self.configJSON['ingagePolicyManagementSCAURL'] = env.str('ING_UT_POLICYMANAGEMENT_URL',default='')
        self.configJSON['ingagePolicyManagementCTXRoot'] = env.str('ING_UT_POLICYMANAGEMENT_CTX')        
        self.configJSON['ingagePolicyManagementTimeout'] = env.int('ING_UT_POLICYMANAGEMENT_TIMEOUT', default=3)
        # User Management Service Component
        self.configJSON['ingageUserManagementSCAURL'] = env.str('ING_UT_USERMANAGEMENT_URL',default='')
        self.configJSON['ingageUserManagementCTXRoot'] = env.str('ING_UT_USERMANAGEMENT_CTX')        
        self.configJSON['ingageUserManagementTimeout'] = env.int('ING_UT_USERMANAGEMENT_TIMEOUT', default=3)
        # Login Service Component
        self.configJSON['ingageLoginSCAURL'] = env.str('ING_UT_LOGIN_URL',default='')
        self.configJSON['ingageLoginCTXRoot'] = env.str('ING_UT_LOGIN_CTX')        
        self.configJSON['ingageLoginTimeout'] = env.int('ING_UT_LOGIN_TIMEOUT', default=3)

        # END