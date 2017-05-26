"""
This file contains all the HTTP routes for basic pages (usually HTML)
"""
import os
from flask import Blueprint, Response, request, render_template, send_from_directory
import functions

pages = Blueprint('routes', __name__)


@pages.route('/<string:uuid>')
def dataset(uuid):
    metadata = functions.get_metadata_fields_from_gn(uuid)
    import pprint
    pprint.pprint(metadata)
    html = functions.make_html(metadata)
    print html
    return Response(
        html
    )
