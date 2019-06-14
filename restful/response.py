import json

class ResponseBody(object):

    def __init__(self, error, data):
        self.error_code = error
        self.data = data

    def toJson(self):
        return json.dumps(self.__dict__)