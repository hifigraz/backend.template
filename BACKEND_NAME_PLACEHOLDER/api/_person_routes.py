from fastapi import FastAPI

from ..crud import Crud


def define_routes(app: FastAPI, crud: Crud) -> None:
    pass
