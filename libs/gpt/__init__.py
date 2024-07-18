from libs.gpt.gpt import GPT
from libs.gpt.prompt import Prompt
from libs.gpt.tokens import Tokenizer
from libs.gpt.tokens import getTokenLength

class Summarizer:
    # this class should use the GPT class as a super class
    def __init__(self, gpt: GPT=None) -> None:
        if gpt == None:
            self.gpt = GPT()
            self.gpt.createRole('system', 'Analyze and condense the content provided below. Return ONLY the 3-5 bullet point summaries in Traditional Chinese, with each bullet no more than 5 sentences. Omit promotional or unrelated information:\n\n')
        else:
            self.gpt = gpt
        

    def summary( self, text: str=None ):
        # Workflow:
        # 1. Check the size of the text
        # 2. Chop the text into chunks
        # 3. Generate the summary for each chunk until the total length of the summary is less than maximum tokens length (maxTokenLength)
        # 4. Return the summary
        # I don't want to check the text now.
        # self.maxTokenLength might be repalce by self.gpt.maxTokenLength
        chunks = self.divideText(text, self.gpt.maxTokenLength)
        summarizes = self.getSummaryByChunks(chunks)
        return summarizes[0]


    def getSummaryByChunks( self, chunks, recursiveCount=0 ):
        # recursiveCount can not be greater than 6
        if recursiveCount > 6:
            return chunks[0]
        recursiveCount += 1
        # print("Current chunks size: ", len(chunks))
        # print("All chunks size:", [getTokenLength(chunk) for chunk in chunks])
        chunks = self.mergeChunks(chunks)
        # print("Merged chunks size: ", len(chunks))
        # print("All chunks size:", [getTokenLength(chunk) for chunk in chunks])
        summarys = []
        for chunk in chunks:
            self.gpt.fill(text=chunk)
            summary = self.gpt.ChatCompletion()
            summarys.append(summary)
        # get lines of summarys[0]
        lines = summarys[0].split("\n")
        # print("Recursive count: ", recursiveCount)
        return summarys if len(summarys) == 1 and len(lines) == 1 else self.getSummaryByChunks(summarys, recursiveCount)
    
    def mergeChunks( self, chunks, maxTokenLength=2048 ):
        mergedChunks = []
        currentChunk = ""
        for chunk in chunks:
            if getTokenLength(currentChunk + chunk) <= maxTokenLength:
                currentChunk += chunk
            else:
                mergedChunks.append(currentChunk)
                currentChunk = chunk
        if currentChunk:
            mergedChunks.append(currentChunk)
        
        return mergedChunks

    
    def divideText(self, text: str, maxTokenLength=2048):
        tokenLength = getTokenLength(text)
        chunks = []
        # seprate text based on newline and token length
        if tokenLength > maxTokenLength:
            lines = text.split("\n")
            currentChunk = ""
            for line in lines:
                if getTokenLength(currentChunk) + getTokenLength(line) > maxTokenLength:
                    chunks.append(currentChunk)
                    currentChunk = ""
                currentChunk += line + "\n"
            chunks.append(currentChunk)
        else:
            chunks.append(text)

        return chunks
        
