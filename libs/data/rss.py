#!/usr/bin/env python
import feedparser
import logging

# filter is a lambda function
def rss_parser( links: list, filter=None):
    # filter lambda functions
    entires = []
    try:
        for link in links:
            rss = feedparser.parse(link)
            # merge rss.entries to entires
            entires = [*entires, *rss.entries]
    except Exception as e:
        logging.error(e)
    # run the filter
    result = []
    if filter:
        for i in range(len(entires)):
            try:
                if filter(entires[i]):
                    result.append(entires[i])
            except Exception as e:
                logging.error(e)
    return result

if __name__ == '__main__':
    import datetime
    links = [
        'https://abmedia.io/feed',
        'https://blockcast.it/feed/',
        'https://zombit.info/feed/',
    ]
    # filter = check it's today's news
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    # parse the published date
    # the date from published like 'Tue, 29 Aug 2023 08:44:25 +0000'
    filter = lambda entry: datetime.datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d") == today
    entires = rss_parser(links, filter)
    print("Today's news: ", len(entires))
    for i, entry in enumerate(entires):
        # print title
        print(f'{i+1}. ', entry.title)
        date = datetime.datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
        print("Date:", date.strftime("%Y-%m-%d %H:%M:%S"))
        print("=====================================")
