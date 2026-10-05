from flask import Blueprint,jsonify

health_bp=Blueprint("health",__name__,)
@health_bp.get("/health")

def test_health():
    return(
        jsonify({
            "status":"ok",
            "service":"aulaplan-api",
            "runtime":"pyhton",
        }),
        200,
        )