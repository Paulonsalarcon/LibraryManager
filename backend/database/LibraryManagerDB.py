import os
from sqlalchemy import create_engine
import yaml

databasePath = os.path.abspath(os.getcwd())
currentPath = databasePath
backendPath = os.path.abspath(os.path.join(currentPath, os.pardir))
configPath = os.path.abspath(os.path.join(backendPath,"config"))


class LibraryManagerDB:
    def __init__(self):
        
        self.__loadDBConfig()

        engine = create_engine('postgresql://postgres:nimda@localhost:5432/LibraryManagement')
        print("success")

    def __loadDBConfig(self):
        with open(os.path.join(configPath,"DBConfig.yaml"), "r") as dbConfigFile:
            dbConfig = yaml.load(dbConfigFile)
        print(dbConfig)

if __name__ == "__main__":
    libraryManagerDB = LibraryManagerDB()    


