"""Cloud Function entrypoint; ejecutar python scripts/prepare_functions.py antes de deploy."""
from firebase_admin import initialize_app, get_app
from firebase_functions import https_fn
from firebase_functions.options import set_global_options
from src.http.app import create_app

set_global_options(max_instances=10)
try:
    get_app()
except ValueError:
    initialize_app()
app = create_app()

@https_fn.on_request(region='us-central1')
def api(req: https_fn.Request) -> https_fn.Response:
    with app.request_context(req.environ):
        return app.full_dispatch_request()
