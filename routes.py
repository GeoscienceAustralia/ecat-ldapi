"""
This file contains all the HTTP routes for basic pages (usually HTML)
"""
import sys
from flask import request, Blueprint, Response
import functions

pages = Blueprint('routes', __name__)


@pages.route('/')
def index():
    return "Non-functional index page for the metataggen application"


@pages.route('/dataset/uuid/<string:uuid>')
def dataset_uuid(uuid):
    try:
        metadata = functions.get_metadata_fields_from_gn(uuid)
        html = functions.make_metatag_html(metadata)

        return Response(html)
    except Exception as e:
        return Response(
            'ERROR: likely the UUID does not exist.\n\nDetailed message:\n' + str(e),
            status=400,
            mimetype='text/plain'
        )


@pages.route('/dataset/<string:ecat_id>')
def dataset(ecat_id):
    if request.args.get('_view') == 'agls':
        try:
            metadata = functions.view_agls_dict_from_csw(ecat_id)
            xml = functions.make_agls_xml(metadata)

            return Response(xml, mimetype='text/xml')
        except Exception as e:
            return Response(
                'ERROR: likely the eCatID does not exist.\n\nDetailed message:\n' + str(e),
                status=400,
                mimetype='text/plain'
            )
    else:
        try:
            metadata = functions.view_metatag_dict_from_csw(ecat_id)
            html = functions.make_metatag_html(metadata)

            return Response(html)
        except Exception as e:
            return Response(
                'ERROR: likely the eCatID does not exist.\n\nDetailed message:\n' + str(e),
                status=400,
                mimetype='text/plain'
            )
