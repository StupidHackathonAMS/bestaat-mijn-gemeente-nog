from flask import jsonify

from app import app, BmgnError


@app.route("/")
def index():
    return jsonify({})
