from datetime import datetime


class New():
    def __init__(self,title:str=None, date:datetime=None, author:str=None, url:str =None):
        self.title = title
        self.date = date
        self.author = author
        self.url = url

