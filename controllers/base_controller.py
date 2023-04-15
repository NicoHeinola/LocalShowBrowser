from flask import request


class BaseController:
    def __init__(self, app) -> None:
        self._app = app
        self._register_routes()

    def _register_routes(self):
        pass

    def _return_response(self, response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
