from sqlalchemy import Engine


class Crud:
    def __init__(self, engine: Engine):
        self._engine: Engine = engine
