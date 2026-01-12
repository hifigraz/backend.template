class Crud():
    def __init__(self, engine):
        self._engine =engine 

    def get_root(self):
        return { "message:": "Hello Root!" }
