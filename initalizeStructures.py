import json
import os

cwd = os.getcwd()
sep = os.sep

def createStudentAccounts(dbPath, netIDPath):
    with open(netIDPath, "r") as idFile:
        ids = json.load(idFile)
        with open(dbPath, "w") as db:
            dbAccount = {}
            for keys in ids.keys():
                dbAccount.update(
                    {
                        keys:{
                            "salt" : "",
                            "hash" : ""
                        }
                    }
                )
            
            json.dump(dbAccount, db, indent=4)


#!! Set user and groups manually !!#
def createFolders(rootFolder, netIDpath, labs):
    with open(netIDpath, "r") as idFile:
        ids = json.load(idFile)
        for keys in ids.keys():
            for labNuber in labs:
                ipFolder = f'{rootFolder}{sep}{ids[keys]}'
                folderPath = f"{ipFolder}{sep}Lab-{labNuber}"
                os.makedirs(folderPath, exist_ok=True)

                #Full permisions for User and Group (77), for other users they can read and execute
                os.chmod(ipFolder, 0o775)

                #For other users, can write and enter the direcotry, but can not list the different files within it 
                os.chmod(folderPath, 0o773)
            

if __name__ == "__main__":
    student_Account_Path = f'{cwd}{sep}webapp{sep}JSONs{sep}studentAccounts.json'
    netID_Path = f'{cwd}{sep}webapp{sep}JSONs{sep}NetID-IP.json'
    student_Sumbissions_Path = f'{cwd}{sep}StudentSubmissions'
    list_Of_Lab_Numbers = [0, 1, 2, 3, 4, 5, 6]

    createStudentAccounts(student_Account_Path, netID_Path)
    createFolders(student_Sumbissions_Path, netID_Path, list_Of_Lab_Numbers)