from abc import ABC, abstractmethod
import feedparser
from pprint import pprint 
import threading, queue

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
        self.threads =[threading.Thread(target=self.data_queue.put(strategy.parseRSS())) 
                       for strategy in self.strategies]
        for thread in self.threads:
            thread.start()


class FileWriter:
    def __init__(self, queue):
        self.queue = queue

    def writeFileFromQueue(self):
        while True:
            items = self.queue.get() 
            with open("output.txt", 'a', encoding="utf-8") as file:
                for item in items:
                    file.write(" ".join(item) + '\n')
            self.queue.task_done()
    
    def startWritingToFile(self):
        self.thread = threading.Thread(target=self.writeFileFromQueue, daemon=True)
        self.thread.start()


class Manager:
    def __init__(self):
        q = queue.Queue()
        strategyTUTBY = TUTBYStrategy('https://news.tut.by/rss/index.rss')
        strategyOnliner = OnlinerStrategy('https://people.onliner.by/feed')
        self.parser = Parser([strategyTUTBY, strategyOnliner], q)
        self.writer = FileWriter(q)

    def process(self):
        self.writer.startWritingToFile()
        self.parser.collectData()

        self.writer.queue.join()

manager = Manager()
manager.process()