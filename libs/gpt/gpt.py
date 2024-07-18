import openai
from libs.gpt.prompt import Prompt
from libs.gpt.tokens import Tokenizer

class GPT:
    def __init__(self, platform: str = None, model: str = None, prompts: dict = {}, temperature: float = 0.0, divide: bool = False, force_merge: bool = False, maxTokenLength: int=1024, tokenizer: Tokenizer=None) -> None:
        import uuid
        self.uuid = uuid.uuid4()
        self.chat_history = [] # Did I need to allow user to set the chat history? Not sure.
        # need to support role play
        self.platform = platform
        self.model = model
        self.maxTokenLength = maxTokenLength
        self.selected_prompt = None
        self.prompts = prompts
        self.temperature = temperature
        self.roles = {}
        self.inputs = {}
        # tokenizer, that should be a union type
        self.tokenizer = tokenizer if tokenizer != None else Tokenizer(platform=platform, model=model)


    def createPrompt(self, name, *args, **kwargs) -> None:
        self.prompts[name] = Prompt(*args, **kwargs)
        self.selected_prompt = name
    
    def createRole(self, name, *args, **kwargs) -> None:
        prompt = Prompt(*args, **kwargs)
        self.roles[name] = prompt

    def ChatCompletion(self) -> str:
        if self.selected_prompt == None:
            raise Exception('No prompt is selected')
        # return 'ChatCompletion is called'
        if self.platform == 'openai':
            system_prompt = self.roles['system'].gen()
            user_prompt = self.gen()
            if len(user_prompt) == 0:
                return ''

            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ]
            openai_chat_completion_config = {
                'model': self.model,
                'messages': messages,
                'temperature': self.temperature,
            }
            # print(openai_chat_completion_config)
            # return 'ChatCompletion is called'
            response = openai_chat_completion(openai_chat_completion_config)
            result = openai_response_normalize(response)
            return result
        else:
            raise Exception(f'Platform {self.platform} is not supported yet')

        # return self.gen()
    
    def fill(self, text: str=None):
        # print("Debug: ", self.selected_prompt, self.prompts[self.selected_prompt])
        self.prompts[self.selected_prompt].fill(text)

    def fill(self, keyword: str=None, text: str=None) -> None:
        if keyword == None:
            keyword = self.prompts[self.selected_prompt].default_input
            # raise Exception('Keyword is required')
        if keyword not in self.prompts[self.selected_prompt].keywords:
            raise Exception(f'Invalid keyword: {keyword}')
        self.inputs[keyword] = text
    
    def clean(self) -> None:
        self.inputs = {}

    def getPrompt(self) -> Prompt:
        if self.selected_prompt == None:
            raise Exception('No prompt is selected')
        return self.prompts[self.selected_prompt]

    def gen(self) -> str: return self.generate()
    def generate(self) -> str:
        # fill with the inputs
        if self.selected_prompt == None:
            raise Exception('No prompt is selected')
        for keyword in self.inputs:
            self.prompts[self.selected_prompt].fill(keyword, self.inputs[keyword])        
        return self.prompts[self.selected_prompt].generate()

def openai_chat_completion( config: dict, force_merge=False ):
    __slot__ = ['config']
    __config_slots__ = ['model', 'messages', 'temperature']
    __config_defaults__ = {
        'model': 'gpt-3.5-turbo',
        'temperature': 0.0,
    }
    # merge the config
    for key in __config_defaults__:
        # check is in __config_slots__
        if force_merge == False and key not in __config_slots__:
            raise Exception(f'Invalid config key: {key}')
        # merge the config
        if key not in config:
            config[key] = __config_defaults__[key]
    # print("Debug: ", config)
    # chat completion
    response = openai.ChatCompletion.create(
        model=config['model'],
        messages=config['messages'],
        temperature=config['temperature'],
        # max_tokens=150,
        # top_p=1,
        # frequency_penalty=0,
        # presence_penalty=0,
        stop=['\n'],
    )
    # return the response, I might want to create another function to normalize the response
    return response

def openai_response_normalize( response ):
    # Now only support the ChatCompletion (model: gpt-3.5-turbo)
    return response['choices'][0]['message']['content']