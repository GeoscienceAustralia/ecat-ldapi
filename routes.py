"""
This file contains all the HTTP routes for basic pages (usually HTML)
"""
from flask import Blueprint, Response
import functions

pages = Blueprint('routes', __name__)


@pages.route('/')
def index():
    return "soon to be the static meta index page"


@pages.route('/dataset/<string:uuid>')
def dataset(uuid):
    try:
        metadata = functions.get_metadata_fields_from_gn(uuid)
        html = functions.make_html(metadata)

        return Response(html)
    except Exception as e:
        return Response(e.message, status=400)
