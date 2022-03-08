import time


class New():
    def __init__(self, id:int=0,title:str=None, date:str=None, author:str=None, url:str =None):
        self.id = id
        self.title = title
        self.date = date
        self.author = author
        self.url = url
    

    def get_timemark(self):
        return time.mktime(time.strptime(self.date, '%d/%m/%Y'))

