class MongoImporter(TrainingDataImporter):
    def __init__(self,database_name,
                config_file: Optional[Text] = None,
                 domain_path: Optional[Text] = None,
                 training_data_paths: Optional[Union[List[Text], Text]] = None,
                 ):
        self.database_name=database_name
        db=MongoTraining(database_name)
        self.temp_directory_path=db.retrive_files()
        print(self.temp_directory_path)
        self.story_files=""
        self.nlu_files=rasa.data.get_nlu_directory(self.temp_directory_path)
        print(self.nlu_files)

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

    # def get_content(self, path: Text, ) -> Text:
    #     file = self.repository.get_contents(path)
    #     return file.decoded_content.decode("utf-8")

    async def get_nlu_data(self, language: Optional[Text] = "en") -> TrainingData:
        from rasa.importers import utils

        return utils.training_data_from_paths(self.nlu_files, language)

    async def get_domain(self) -> Domain:
        domain_as_yaml = self.get_content("domain.yml")
        return Domain.from_yaml(domain_as_yaml)

