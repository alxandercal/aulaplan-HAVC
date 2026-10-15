from datetime import date, datetime
from flask import jsonify
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException
from src.core.errors import ApiError

def to_jsonable(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [to_jsonable(item) for item in value]
    return value

def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def api_error(exc):
        body = {'error': exc.code, 'message': exc.message}
        if exc.details is not None:
            body['details'] = to_jsonable(exc.details)
        return jsonify(body), exc.status_code

    @app.errorhandler(ValidationError)
    def validation_error(exc):
        details = [
            {'field': '.'.join(map(str, e['loc'])), 'message': e['msg']}
            for e in exc.errors()
        ]
        return jsonify({'error': 'VALIDATION_ERROR', 'message': 'Datos invalidos', 'details': details}), 422

    @app.errorhandler(HTTPException)
    def http_error(exc):
        return jsonify({'error': exc.name.replace(' ', '_').upper(), 'message': exc.description}), exc.code

    @app.errorhandler(Exception)
    def unexpected(exc):
        app.logger.exception('Unhandled error')
        return jsonify({'error': 'INTERNAL_ERROR', 'message': 'Error interno del servidor'}), 500
