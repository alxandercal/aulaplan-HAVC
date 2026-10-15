"""Contrato reservado para integracion IA posterior. No simula inteligencia artificial."""
from flask import Blueprint, jsonify
from src.auth.security import require_roles
ai_bp = Blueprint('ai', __name__)

@ai_bp.post('/ai/constraints/parse')
@require_roles('ADMIN', 'COORDINATOR')
def parse_constraints():
    return jsonify({
        'error': 'AI_NOT_CONFIGURED',
        'message': 'La interpretacion con IA es la unica integracion pendiente. Ver docs/INTEGRACION-IA.md.',
    }), 501
