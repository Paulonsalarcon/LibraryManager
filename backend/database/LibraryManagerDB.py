from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import yaml
import logging
import pathlib
from tables import User, Author, Book, CoAuthorBook, Borrowing, LibraryHistory, Reservation


databasePath = pathlib.Path(__file__).parent.absolute()
currentPath = databasePath
backendPath = databasePath.parent.absolute()
configPath = backendPath.joinpath("config").absolute()
dbConfigPath = configPath.joinpath("DBConfig.yaml").absolute()


class LibraryManagerDB:
    def __init__(self):
        logging.debug("Creating instance of LibraryManagerDB")
        try:
            self.dbConfig = self.__loadDBConfig()

            engineParameters = "".join([self.dbConfig["dbms"],"://",self.dbConfig["user"],":",self.dbConfig["pswd"],"@",self.dbConfig["host"],":",str(self.dbConfig["port"]),"/"+self.dbConfig["db"]])
            self.engine = create_engine(engineParameters)
            logging.info("Engine created for: "+engineParameters)

            self.meta = MetaData(bind=self.engine, reflect=True)
            Base.metadata = self.meta
            logging.debug("Instance of LibraryManagerDB created successfully")
        except:
            logging.critical("Failed create instance of LibraryManagerDB")

    def __loadDBConfig(self):
        logging.debug("loadDBConfig started")
        try:
            with open(dbConfigPath, "r") as dbConfigFile:
                dbConfig = yaml.load(dbConfigFile)
            logging.info("Loaded Database Configuration: "+dbConfigPath._str)
        except:
            logging.critical("Error loading Database Configuration:"+dbConfigPath._str)

        logging.debug("loadDBConfig finished")
        return dbConfig

    def Connect(self):
        logging.debug("Connect started")
        try:
            self.engine.connect()
            logging.info("Connected to database: ", self.dbConfig["db"])
        except:
            logging.critical("Unable to connect to database: ", self.dbConfig["db"])

        logging.debug("Connect finished")
    
    def Create(self):
        logging.debug("Create started")
        User().create(self.engine, self.meta)
        Author().create(self.engine, self.meta)
        Book().create(self.engine, self.meta)
        CoAuthorBook().create(self.engine, self.meta)
        Borrowing().create(self.engine, self.meta)
        LibraryHistory().create(self.engine, self.meta)
        Reservation().create(self.engine, self.meta)



    
    def Migrate(self):
        logging.debug("Migrate started")
        User().migrate(self.engine)
        Author().migrate(self.engine)
        Book().migrate(self.engine)
        CoAuthorBook().migrate(self.engine)

    def OpenSession():
        logging.debug("OpenSession started")
        try:
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            logging.info("Session created")
            return self.session
        except:
            logging.critical("Unable to create session in database: ", self.dbConfig["db"])
            return None





if __name__ == "__main__":
    libraryManagerDB = LibraryManagerDB()    
    libraryManagerDB.Connect()


