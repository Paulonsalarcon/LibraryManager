from LibraryManagerDB import LibraryManagerDB

if __name__ == "__main__":
    libraryManagerDB = LibraryManagerDB()
    libraryManagerDB.Connect()
    libraryManagerDB.Create()
    libraryManagerDB.Migrate()

    
