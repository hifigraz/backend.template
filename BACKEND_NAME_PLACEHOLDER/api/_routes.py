from ..engine import get_engine
from ..crud import Crud

def define_routes(app):
    @app.get("/")
    def get_root():
        crud = Crud(get_engine())
        return crud.get_root()
