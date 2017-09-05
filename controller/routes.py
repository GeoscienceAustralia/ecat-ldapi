"""
This file contains all the HTTP routes for basic pages (usually HTML)
"""
import sys
from flask import request, Blueprint, Response, render_template
import functions

pages = Blueprint('routes', __name__)


@pages.route('/')
def index():
    return "Non-functional index page for the metataggen application"


@pages.route('/dataset/<string:ecat_id>')
def dataset(ecat_id):
    if request.args.get('_view') == 'alternates':
        # render a static resource pre-configured with all values
        if request.args.get('_format') in ['text/xml', 'application/xml']:
            m = request.args.get('_format')
        else:
            m = request.accept_mimetypes.best_match(['text/html', 'application/xml', 'text/xml'])

        if m is None:
            m = 'text/html'

        if m in ['application/xml', 'text/xml']:
            return Response(render_template('alternates.xml'), mimetype=m)
        else:
            return Response(render_template('alternates.html'), mimetype=m)
    elif request.args.get('_view') == 'agls':
        try:
            metadata = functions.get_view_agls_dict_from_csw(ecat_id)
            xml = functions.render_agls_xml(metadata)

            return Response(xml, mimetype='text/xml')
        except Exception as e:
            return Response(
                'ERROR: likely the eCatID does not exist.\n\nDetailed message:\n' + str(e),
                status=400,
                mimetype='text/plain'
            )
    else:  # view == 'metatag'
        try:
            metadata = functions.get_view_metatag_dict_from_csw(ecat_id)
            html = functions.render_metatag_html(metadata)

            return Response(html)
        except Exception as e:
            return Response(
                'ERROR: likely the eCatID does not exist.\n\nDetailed message:\n' + str(e),
                status=400,
                mimetype='text/plain'
            )
