#!/usr/bin/env python
from libs.gpt import Summarizer, GPT, Tokenizer
from libs.data import rss, article
from dotenv import load_dotenv
import os, logging, datetime, requests, openai

load_dotenv()
SLACK_WEBHOOKURL = os.getenv("SLACK_WEBHOOKURL")

def slack_link(text, url):
    # injection attack exists
    text = text.replace('>','.').replace('<','.')
    return f"<{url}|{text}>"

def send_to_slack(text):
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "type": "mrkdwn",
        "text": text
    }
    try:
        logging.info(f"Sent a message to {SLACK_WEBHOOKURL}")
        result = requests.post(SLACK_WEBHOOKURL, headers=headers, json=data)
        #assert result["ok"]
        logging.info(result)
    except Exception as e:
        logging.info(f'Error: {e}')
        # get the issues by version
def data_to_slack( list, delimiter='\n' ):
    result = ''
    for item in list:
        result += f"{slack_link(item['title'], item['link'])}：{item['summary']}\n\n"
    return result



if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # Initialize the GPT
    tokenizer = Tokenizer(platform='openai', model='gpt-3.5-turbo')
    summaryGPT = GPT(platform='openai', model='gpt-3.5-turbo', maxTokenLength=12, tokenizer=tokenizer)
    summaryGPT.createRole('system', 'Analyze and condense the content provided below. Return ONLY the 3-5 bullet point summaries in Traditional Chinese, with each bullet no more than 5 sentences. Omit promotional or unrelated information:\n\n')
    print("GPT UUID: ", summaryGPT.uuid)

    content = '\nHello! I’m ChatGPT, an advanced language model created by OpenAI, based on the GPT-4 architecture. My primary role is to assist users by providing detailed and accurate information, engaging in meaningful conversations, and helping with various tasks ranging from coding and debugging to general knowledge inquiries and creative writing.\nI’m equipped with a vast array of knowledge, updated as of July 2023, which enables me to offer insights on numerous topics. My capabilities include understanding and generating human-like text, solving complex problems, and adapting to a wide range of conversational contexts. I strive to be a cool, understanding, and helpful companion, especially for those who prefer a friendly, supportive interaction.\n\n'
    summaryGPT.createPrompt('summary')
    summaryGPT.fill(text=content) # that will fill the default input

    summaryBot = Summarizer(summaryGPT)
    links = [
        'https://abmedia.io/feed',
        'https://blockcast.it/feed/',
        'https://zombit.info/feed/',
    ]
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filter = lambda entry: datetime.datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d") == today
    entires = rss.rss_parser(links, filter)

    news = []
    for i in range(len(entires)):
    # for entry in entires:
        print(f'===== Summary post {i} =====')
        entry = entires[i]
        # merge the content
        if 'content' in entry:
            content = ''
            for c in entry.content:
                content += c.value
            md_content = article.custom_md(content)
            summary = summaryBot.summary(md_content)
            news.append({
                'title': entry.title,
                'link': entry.link,
                'summary': summary
            })
            print("summary: ", summary)
    
    # if news is empty, notify the user that no news today
    if len(news) == 0:
        news_sources = [slack_link(v, v) for v in links]
        news.append({
            'title': 'No news today',
            'link': '',
            'summary': 'No news today, please check the following links:\n' + '\n'.join(news_sources) + '\n\n'
        })
    data = data_to_slack(news, delimiter='\n\n')
    send_to_slack(data)
