from . import api
from .utils._seed_admin import ensure_admin

app = api.build_app()
ensure_admin()