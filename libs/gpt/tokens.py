#!/usr/bin/env python
import tiktoken

class Tokenizer: # That should be a super class, but not now.
    def __init__(self, platform: str='openai', model: str="cl100k_base"):
        supported_tokenizer = {
            'openai': {
                'gpt-4': 'cl100k_base',
                'gpt-3.5-turbo': 'cl100k_base',
                'text-embedding-ada-002': 'cl100k_base',
                'text-davinci-003': 'p50k_base',
                'text-davinci-002': 'p50k_base',
                'text-curie-001': 'r50k_base',
                'text-babbage-001': 'r50k_base',
                'text-cushman-001': 'r50k_base',
                'davinci': 'r50k_base',
                'curie': 'r50k_base',
                'babbage': 'r50k_base',
                'ada': 'r50k_base',
            },
        }
        if platform not in supported_tokenizer:
            raise Exception(f'Platform {platform} is not supported yet')
        elif supported_tokenizer[platform] == None:
            raise Exception(f'Platform {platform} is not supported yet')
        if model not in supported_tokenizer[platform]:
            raise Exception(f'Model {model} is not supported yet')
        elif supported_tokenizer[platform][model] == None:
            raise Exception(f'Model {model} is not supported yet')
        tokenizer_model = supported_tokenizer[platform][model]
        self.enc = tiktoken.get_encoding(tokenizer_model)
        self.platform = platform
        self.model = model
        self.tokenizer_name = tokenizer_model
    
    def encode(self, text: str=None):
        return self.enc.encode(text)
    
    def decode(self, tokens: list=None):
        return self.enc.decode(tokens)
    
    def lenof(self, text: str=None): # Length Of text
        return len(self.encode(text))
    
    # Something like linux command cut, that can set a delimiter and split the text into chunks
    def cut(self, text: str=None, delimiter: str=None, maximumLength: int=2048, output_type: str='text'):
        # based on delim first, if that is over to maximumLength also cut it.
        token_buffer = self.encode(text)
        delim = self.encode(delimiter)
        chunks = []
        current_chunk = []
        current_length = 0
        delim_trigger = 0
        for token in token_buffer:
            # print("token: ", token, '\t', token == delim[delim_trigger], '\t', delim, '\t', self.decode([token]))
            if token == delim[delim_trigger]:
                delim_trigger += 1
                # print("delim_trigger: ", delim_trigger)
                if delim_trigger == len(delim) or current_length == maximumLength:
                    # print("Cut it!")
                    delim_trigger = 0
                    if len(current_chunk) > 0:
                        chunks.append(current_chunk)
                        current_chunk = []
                        current_length = 0
            else:
                delim_trigger = 0
                current_chunk.append(token)
                current_length += 1

        if len(current_chunk) > 0:
            chunks.append(current_chunk)

        if output_type == 'text':
            return [self.decode(chunk) for chunk in chunks]
        elif output_type == 'token':
            return chunks

def getTokenLength(msg: str=None, model: str="cl100k_base"):
    enc = tiktoken.get_encoding(model)
    assert enc.decode(enc.encode("hello world")) == "hello world"
    tokens = enc.encode(msg)
    return len(tokens)

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--message", dest="msg", default=None)
    parser.add_argument("--model", dest="model", default="cl100k_base")
    args = parser.parse_args()
    
    msg = "Hello world"
    print("msg: ", msg)
    print("msg length: ", len(msg))
    print("token length: ", getTokenLength(msg))