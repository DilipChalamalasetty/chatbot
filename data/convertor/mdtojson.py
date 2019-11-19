'''this file converts our nlu md training files to nlu json training files which are used to store in
nosql databases'''

import json
import glob #used to read all file path in a specific directory
from rasa.nlu import training_data

nlu_mdfiles_path='../mdfiles/*.md'
nlu_jsonfiles_path='../nlu/'
files=glob.glob(nlu_mdfiles_path) #list of all the mdfile paths
for f in files:
    td = training_data.load_data(f)
    output = td.as_json()
    json_data = json.loads(output)
    filename_list=f.split('\\')
    filename=filename_list[-1].split('.')
    with open(nlu_jsonfiles_path+filename[0]+'.json','w') as f:
        json.dump(json_data,f,indent=4)