import json


FOLDER_DATE = "rpa_orchestrator/files/tranvia/"
FILE      = "extractDates.json"
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class TranviaController(metaclass=Singleton):
    
    def get_dates_extract(self):
        try:
            with open(FOLDER_DATE+FILE) as dates_json:
                dates = json.load(dates_json)
                return json.dumps(dates)
        except:
            print("Error con el fichero tranvia")
            return None

    def get_data_date(self, date):
        if not date:
            return None
        try:
            with open(FOLDER_DATE+FILE) as dates_json:
                dates = json.load(dates_json)
        except:
            print("Error con el fichero tranvia")
            return None

        for d in dates['dates']:
            if date == d:
                print("Fecha encontrada")
                try:
                    with open(FOLDER_DATE+date+".json") as data_json:
                        data = json.load(data_json)
                        return json.dumps(data)
                except:
                    print("Error con el fichero de datos del tranvia "+date)
                    return None
        print("Datos con fecha "+date+" no encontrada")
        return None
        
    def write_date(self, date):
        try:
            with open(FOLDER_DATE+FILE, "r") as data_json:
                data = json.load(data_json)
            for d in data['dates']:
                if date == d:
                    print("La fecha ya existia")
                    return
                    
            data["dates"].append(date)

            with open(FOLDER_DATE+FILE, "w+") as data_json:
                json.dump(data, data_json)
        except Exception as e:
            print(e)
            print("Error intentado escribir en el fichero")

    def write_data(self, date, data):
        try:
            with open(FOLDER_DATE+date+".json", "w+") as data_json:
                json.dump(data, data_json)
        except Exception as e:
            print(e)
            print("Error intentado escribir en el fichero")

