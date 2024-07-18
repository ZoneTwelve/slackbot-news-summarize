class Prompt:
    def __init__(self, template: str='', strict: bool=True, keywords: list=[], temperature: float=0.0, quotes: dict={'start': '[', 'end': ']'}) -> None:
        self.quotes = quotes
        self.default_input = '__DEFAULT__'
        self.template = template + self.quote(self.default_input)
        self.inputs = {self.default_input: ''}
        self.strict = strict
        self.keywords = [self.default_input, *keywords]
        for keyword in self.keywords:
            self.inputs[keyword] = None

    def fill(self, keyword: str=None, text: str=None) -> None:
        if keyword == None:
            keyword = self.default_input
            # raise Exception('Keyword is required')
        if keyword not in self.keywords:
            raise Exception(f'Invalid keyword: {keyword}')
        self.inputs[keyword] = text
    
    def clean(self) -> None:
        for keyword in self.keywords:
            self.inputs[keyword] = None
        self.inputs[self.default_input] = ''
        print(self.inputs)

    def quote(self, text):
        return self.quotes['start'] + text + self.quotes['end']

    def gen(self) -> str: return self.generate()
    def generate(self) -> str:
        prompt = self.template
        for keyword in self.keywords:
            if self.strict and self.inputs[keyword] == None and keyword != self.default_input:
                raise Exception(f'Keyword {keyword} is not filled')
            key = self.quote(keyword)
            value = '' if self.inputs[keyword] == None else self.inputs[keyword]
            prompt = prompt.replace(key, value)
        return prompt