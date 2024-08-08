from langchain_community.llms import Ollama
# from tokenizers import Tokenizer
from langchain_text_splitters import CharacterTextSplitter

class LlmManager():

    # Using a finger in the air estimate of 10000 characters per split.
    # Based of the context length of 16384 (codellama), a tokens per word 
    # estimate of 2, and a word length estimate of 5.5 characters.
    # This will hopefully allow us to assign about half of the context 
    # window to transcript sample, and half can be used for instructions
    # and other context (i.e. sumary of earlier debate).
    SPLIT_LENGTH = 10000

    SAMPLE_JSON = """
        ´´´json
        {
            "debate_summary": string,
            "speakers": [
                {"name": string, "party": string},
                {"name": string, "party": string"},
                ...
            ],
            "categories": [string, string,...]
        }
        ´´´
    """


    def __init__(self):
        ollama_host = '192.168.100.62'
        ollama_port = '11434'
        ollama_url = f"http://{ollama_host}:{ollama_port}"

        self.llm = Ollama(base_url=ollama_url, model="llama3.1")

    def test(self, input):


        # Split the input into words in order to get a word count.
        words = input.split()

        # Set a text splitter to split the input into chunks.
        text_splitter = CharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size=self.SPLIT_LENGTH,
            chunk_overlap=0,
            length_function=len,
            is_separator_regex=False,
        )

        splits = text_splitter.split_text(input)
        
        # If there is only one split, then we can process the input as is.
        if len(splits) == 1:
            self.processFullDebate(input)
            print("LLM'd a debate")
        else:
            self.processSplitDebate(splits)

    
    def processFullDebate(self, full_debate):
        



        instruction = f"""
            Extract metrics from Hansard transcript data. Given the following sample transcript:

            {full_debate}

            ----

            Extract the following metrics and output them in JSON format with no additional text:

            Speakers: List of each speaker in the transcript, along with their party affiliation (if available)
            Debate Summary: A paragraph outlining the content of this debate. This should be a summary of the transcript, 
            not a verbatim description.
            Categories: a list of political categories relevant to the transcript, drawn from the following fixed list:
                - Macroeconomics
                - Civil Rights, Minority Issues, Immigration and Civil Liberties
                - Health
                - Agriculture
                - Labour and Employment
                - Education
                - Environment
                - Energy
                - Transportation
                - Law, Crime, and Family Issues
                - Social Welfare
                - Community Development, Planning and Housing Issues
                - Banking, Finance, and Domestic Commerce
                - Defence
                - Space, Science, Technology and Communications
                - Foreign Trade
                - International Affairs and Foreign Aid
                - Government Operations
                - Public Lands and Water Management (Territorial Issues)
            
            Output the extracted metrics in the following JSON format:

            {self.SAMPLE_JSON}

            Note: the output should be a single JSON object with no additional text or formatting.
        """


        response = self.llm.invoke(instruction)
        return
    

    def processSplitDebate(self, splits):
        max = len(splits) - 1
        for i, split in enumerate(splits):
            
            # Instruction for the first split.
            if i == 0:
                instruction = f"""
                    You are processing a sample of a debate from the UK Parliament transcript. 
                    
                    The sample is part of a larger debate. 
                    
                    Your task is to generate a summary of the sample so that we can pass the summary to
                    the next sample to provide context, and so that the final sample can be used to
                    extract metrics from the entire debate.

                    The summary you generate should be no more than four paragraphs.

                    The metrics we are interested in are the speakers, the debate summary, and the categories, 
                    so please make sure to include these in your summary.

                    Here is the sample transcript:
                    {split}
                """
                summary = self.llm.invoke(instruction)

            # Instruction for the middle splits.
            elif i != 0 and i != max:
                instruction = f"""
                    You are processing a sample of a debate from the UK Parliament transcript. 
                    
                    The sample is part of a larger debate and you will provided with a summary of the previous 
                    samples in the debate for context.
                    
                    Your task is to generate a summary of the sample so that we can pass the summary to
                    the next sample to provide context, and so that the final sample can be used to
                    extract metrics from the entire debate.

                    The new summary you generate should be no more than four paragraphs.

                    The metrics we are interested in are the speakers, the debate summary, and the categories, 
                    so please make sure to include these in your summary.

                    Here is the summary of the previous samples:
                    {summary}
                    ----

                    Here is the sample transcript:
                    {split}
                """
                summary = self.llm.invoke(instruction)

            # Instruction for the last split.
            else:
                instruction = f"""
                    Extract metrics from Hansard transcript data. Given the following summary of the debate so far:

                    {summary}

                    ----

                    And the following sample transcript, which is the last in the debate:

                    {split}

                    ----

                    Extract the following metrics and output them in JSON format with no additional text:

                    Speakers: List of each speaker in the transcript, along with their party affiliation (if available)
                    Debate Summary: A paragraph outlining the content of this debate. This should be a summary of the transcript, 
                    not a verbatim description.
                    Categories: a list of political categories relevant to the transcript, drawn from the following fixed list:
                        - Macroeconomics
                        - Civil Rights, Minority Issues, Immigration and Civil Liberties
                        - Health
                        - Agriculture
                        - Labour and Employment
                        - Education
                        - Environment
                        - Energy
                        - Transportation
                        - Law, Crime, and Family Issues
                        - Social Welfare
                        - Community Development, Planning and Housing Issues
                        - Banking, Finance, and Domestic Commerce
                        - Defence
                        - Space, Science, Technology and Communications
                        - Foreign Trade
                        - International Affairs and Foreign Aid
                        - Government Operations
                        - Public Lands and Water Management (Territorial Issues)
                    
                    Output the extracted metrics in the following JSON format:

                    {self.SAMPLE_JSON}

                    Note: the output should be a single JSON object with no additional text or formatting.
                """

                response = self.llm.invoke(instruction)