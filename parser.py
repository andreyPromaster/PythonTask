from abc import ABC, abstractmethod
import feedparser
from pprint import pprint 
import threading, Queue

class AbstractStrategy(ABC):
    def __init__(self, url):
        self.url = url

    @abstractmethod
    def parseRSS(self):
        pass



class TUTBYStrategy(AbstractStrategy):
    def __init__(self, url):
        super().__init__(url)

    def parseRSS(self):
        data = feedparser.parse(self.url)
        return [(item['title'], item['published']) for item in data["entries"]]


class OnlinerStrategy(AbstractStrategy):
    def __init__(self, url):
        super().__init__(url)
    
    def parseRSS(self):
        data = feedparser.parse(self.url)
        return [(item['title'], item['published']) for item in data["entries"]]


class Parser:
    def __init__(self, strategies, queue):
        self.strategies = strategies
        self.data_queue = queue

    def collectData(self):
        threads =[threading.Thread(target=self.queue.put(strategy.parseRSS()))  for strategy in self.strategies]
        # for strategy in self.strategies:
        #     #тут завернуть в новый поток
        #     self.queue.put(strategy.parseRSS()) 
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()


class FileWriter:
    def __init__(self, queue):
        self.queue = queue

    def writeFileFromQueue(self):
        while True:
            items = self.queue.get() 
            with open("output.txt", 'a') as file:
                for item in items:
                    file.write(" ".join(item) + '\n')
            self.queue.task_done()
    
    def startWritingTOFile(self):
        thread = threading.Thread(target=writeFileFromQueue)
        thread.start()
        thread.join()


strategy = TUTBYStrategy('https://news.tut.by/rss/index.rss')
strategy = OnlinerStrategy('https://people.onliner.by/feed')
parser = Parser(strategy)
parser.getData()