from pymongo import MongoClient

client=MongoClient("localhost",27017)

database=client.testingDatabase

collection=database.dummy

rec={ 
'title': 'MongoDB and Python',  
'description': 'MongoDB is no SQL database',  
'tags': ['mongodb', 'database', 'NoSQL'],  
'viewers': 104 
} 

record = database.dummy.insert(rec)

