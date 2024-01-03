
import pyodbc

from utils.configloader         import ConfigUtil
import logging


class MSSQLUtil:
    """
    Utility class for connecting with MSSQL server and perform required operation
    """
    __instance  = None
    __sqlCxn    = None
    _sqlCursor  = None

    @staticmethod
    def getInstance():
        if MSSQLUtil.__instance == None:
            MSSQLUtil()
        return MSSQLUtil.__instance
    
    def __init__(self):
        """
        Constructor for initializing the database connection
        """
        if MSSQLUtil.__instance == None:
            MSSQLUtil.__instance = self
            self.__connect()

    def __connect(self):
        """
        Connect to the database server
        """
        logging.info("Connecting with database server")
        connString = "Driver={driver};Server={hostname},{port};Database={dbName};UID={userID};PWD={password};autocommit=True;".format(hostname=ConfigUtil.getInstance().configJSON["db.host"],                                                                                                                            
                                                                                                                                    port=ConfigUtil.getInstance().configJSON["db.port"],
                                                                                                                                    dbName=ConfigUtil.getInstance().configJSON["db.name"],
                                                                                                                                    userID=ConfigUtil.getInstance().configJSON["db.user"],
                                                                                                                                    password=ConfigUtil.getInstance().configJSON["db.password"],                                                                                                                                                              
                                                                                                                                    driver='ODBC Driver 17 for SQL Server')
        logging.debug("Connection string: {}".format(connString))                                                                                                                                                            
        self.__sqlCxn = pyodbc.connect(connString)
        self.__sqlCxn.timeout = ConfigUtil.getInstance().configJSON["db.stmttimeout"]                                                                                                                                                                                                        
        self._sqlCursor = self.__sqlCxn.cursor()
        logging.info("Connected with database server")

    def executeQuery(self, query, *parameters):
        """
        Execute the query and return the result
        @param query: Query to be executed
        """
        
        try:
            print("Executing query: {}".format(query))
            self._sqlCursor.execute(query, parameters)
            return self._sqlCursor.fetchall()
        except pyodbc.Error as ex:
            sqlstate = ex.args[1]
            sqlstate = sqlstate.split(".")
            logging.error(f"Error while validating the transaction SQL State: {sqlstate} - SQL Error: {ex}")
            raise Exception('Error while executing query')
        except Exception as ex:
            logging.error(f"Error while validating the transaction ")
            logging.error(ex)
            raise Exception('Error while executing query')        

    def executeDMLQuery(self, query, *parameters):
        """
        Execute the query
        @param query: Query to be executed
        """

        try:
            print("Executing query: {}".format(query))
            self._sqlCursor.execute(query, parameters)
            return self.__sqlCxn.commit()
        except pyodbc.Error as ex:
            sqlstate = ex.args[1]
            sqlstate = sqlstate.split(".")
            logging.error(f"Error while validating the transaction SQL State: {sqlstate} - SQL Error: {ex}")
            raise Exception('Error while executing query')
        except Exception as ex:
            logging.error(f"Error while validating the transaction ")
            logging.error(ex)
            raise Exception('Error while executing query')        


    @property
    def sqlCursor(self):
        return self._sqlCursor
    
    @property
    def sqlCxn(self):
        return self.__sqlCxn
        