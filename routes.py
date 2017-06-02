"""
This file contains all the HTTP routes for basic pages (usually HTML)
"""
import sys
from flask import Blueprint, Response
import functions

pages = Blueprint('routes', __name__)


@pages.route('/')
def index():
    return "soon to be the static meta index page"


@pages.route('/dataset/uuid/<string:uuid>')
def dataset(uuid):
    try:
        metadata = functions.get_metadata_fields_from_gn(uuid)
        html = functions.make_html(metadata)

        return Response(html)
    except Exception as e:
        return Response(
            'ERROR: likely the UUID does not exist.\n\nDetailed message:\n' + str(e),
            status=400,
            mimetype='text/plain'
        )


@pages.route('/dataset/<string:ecat_id>')
def dataset(ecat_id):
    try:
        metadata = functions.get_metadata_fields_from_gn_dev(ecat_id)
        html = functions.make_html(metadata)

        return Response(html)
    except Exception as e:
        return Response(
            'ERROR: likely the eCatID does not exist.\n\nDetailed message:\n' + str(e),
            status=400,
            mimetype='text/plain'
        )
