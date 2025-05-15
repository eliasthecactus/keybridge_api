from flask import jsonify

def make_response(code, message, data=None, status_code=200, debug=False):
    """Standardized API response format."""
    response = {
        "code": code,
        "message": message,
        "data": data,
    }
    if debug:
        print(response)
    return jsonify(response), status_code