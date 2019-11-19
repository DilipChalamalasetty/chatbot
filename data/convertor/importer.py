#This file is used for training rasa models by extracting data from the server

import pymongo
import json
import os
import tempfile
import glob
from shutil import copyfile
import rasa.data
from rasa.core.domain import Domain
from rasa.core.interpreter import RegexInterpreter, NaturalLanguageInterpreter
from rasa.core.training.structures import StoryGraph
from rasa.core.training.dsl import StoryFileReader
from typing import Optional, Text, Dict, List, Union
import rasa.utils.io as io_utils
from rasa.nlu.training_data import TrainingData
from rasa.importers.importer import TrainingDataImporter
path=""
pwd=os.getcwd()
class MongoTraining:
    def __init__(self,dbname):
        self.dbname=dbname
    
    def retrive_files(self):
        myclient=pymongo.MongoClient("mongodb://localhost:27017/")
        
        try:
            mydb=myclient[self.dbname]
            collections_list=mydb.list_collection_names()
            self.tempdir = tempfile.mkdtemp()
            path = os.path.join(self.tempdir)
            os.chdir(path)
            path=os.getcwd()
            os.mkdir("data")
            os.chdir(path+"/data")
            os.mkdir("nlu")
            for i in collections_list:
                collection=mydb[i]
                json_doc=collection.find_one({})
                temp_dic={}
                temp_dic['rasa_nlu_data']=json_doc['rasa_nlu_data']
                
                with open(path+'/data/nlu/'+i+'.json','w') as file:
                    json.dump(temp_dic,file)
            myclient.close()
            os.chdir(pwd)
            self.story_files() 
            return path
        except:
            os.chdir(pwd)
            myclient.close()
            print("error occured while connecting to database")
            exit()

    def story_files(self):
        file_loc="E:/DILIP/dummy/data/core/*.md"
        file_temp_loc=self.tempdir+"/data"
        os.chdir(file_temp_loc)
        os.mkdir("core")
        story_files_list=glob.glob(file_loc)
        for files in story_files_list:
            files.replace("""\""",""\\""")
            print(files)
            # copyfile(files, file_temp_loc+"/core/")
            
        print(story_files_list)




db=MongoTraining("testingDatabase")
print(db.retrive_files())

        

class MonImporter(TrainingDataImporter):

    def __init__(self,database_name,
                 config_file: Optional[Text] = None,
                 domain_path: Optional[Text] = None,
                 training_data_paths: Optional[Union[List[Text], Text]] = None,
                 repository: Text = ""):
        self.database_name=database_name
        db=MongoTraining(self.database_name)        
        self.repository = db.retrive_files()

        data_files = self.get_files_from("data")
        directory = tempfile.mkdtemp()
        for f in data_files:
            with open(os.path.join(directory, f.name), "w+b") as file:
                file.write(f.decoded_content)

        self.story_files, self.nlu_files = rasa.data.get_core_nlu_files([directory])

    def get_files_from(self, directory: Text) -> List:
        files = []
        for file in self.repository.get_contents(directory):
            if file.type == "file":
                files.append(file)
            else:  # it's another directory
                files += self.get_files_from(file.path)
        return files

    async def get_stories(self,
                          interpreter: "NaturalLanguageInterpreter" = RegexInterpreter(),
                          template_variables: Optional[Dict] = None,
                          use_e2e: bool = False,
                          exclusion_percentage: Optional[int] = None) -> StoryGraph:
        story_steps = await StoryFileReader.read_from_files(
            self.story_files,
            await self.get_domain(),
            interpreter,
            template_variables,
            use_e2e,
            exclusion_percentage,
        )
        return StoryGraph(story_steps)

    async def get_config(self) -> Dict:
        config_as_yaml = self.get_content("config.yml")
        return io_utils.read_yaml(config_as_yaml)

    def get_content(self, path: Text, ) -> Text:
        file = self.repository.get_contents(path)
        return file.decoded_content.decode("utf-8")

    async def get_nlu_data(self, language: Optional[Text] = "en") -> TrainingData:
        from rasa.importers import utils

        return utils.training_data_from_paths(self.nlu_files, language)

    async def get_domain(self) -> Domain:
        domain_as_yaml = self.get_content("domain.yml")
        return Domain.from_yaml(domain_as_yaml)

