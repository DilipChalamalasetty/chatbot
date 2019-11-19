'''this file inserts all json files which are there in ./data/nlu folder to monogodb'''

import pymongo
import glob
import json

print("please_enter_initialize_code :")
password=input()
if(password=="12345"):
    myclient=pymongo.MongoClient("mongodb://localhost:27017/")
    nlu_jsonfiles_path='../nlu/*.json'
    dbname='testingDatabase'
    nlu_dir_path='../nlu/'
    #extracting intenst names to intent_names variable
    file_path_list=glob.glob(nlu_jsonfiles_path)
    intent_names=[]
    for f in file_path_list:
        file_name=f.split('\\')[-1]
        intent_names.append(file_name.split('.')[0]) #stores all the intent names which are extracted from the glob function
    intent_names.sort()

    #dealing with mongodb database
    if dbname not in myclient.list_database_names():
        mydb=myclient[dbname]
        collections_list=mydb.list_collection_names()
        for i in intent_names:
            if i not in collections_list:
                mycol=mydb[i]
                with open(nlu_dir_path+i+'.json') as file:
                    intent_data=json.load(file)
                    mycol.insert_one(intent_data)
    
    myclient.close()
    print("Inserted json data into mongodb")

else:
    print("wrong intialize code")
            



