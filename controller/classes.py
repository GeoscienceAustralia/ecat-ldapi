"""
This file contains only an HTTP route for Dataset & Record objects, which are synonyms here
"""
from flask import Blueprint, render_template, request, Response
from .functions import render_alternates_view, client_error_Response
import _config as config
from _ldapi import LDAPI, LdapiParameterError
import urllib.parse as uparse

classes = Blueprint('classes', __name__)


@classes.route('/doc/dataset/ga/')
def datasets():
    """
    Register of all Datasets

    :return: LDAPI views of the Dataset register
    """
    class_uri = 'http://purl.org/linked-data/registry#Register'
    
    # lists the views and mimetypes available for an Address Register (a generic Register)
    views_formats = LDAPI.get_classes_views_formats() \
        .get(class_uri)

    try:
        view, mime_format = LDAPI.get_valid_view_and_format(
            request.args.get('_view'),
            request.args.get('_format'),
            views_formats
        )

        # if alternates model, return this info from file
        if view == 'alternates':
            del views_formats['renderer']
            return render_alternates_view(
                class_uri,
                uparse.quote_plus(class_uri),
                None,
                None,
                views_formats,
                request.args.get('_format')
            )
        else:
            from model import register

            # pagination
            page = int(request.args.get('page')) if request.args.get('page') is not None else 1
            per_page = int(request.args.get('per_page')) if request.args.get('per_page') is not None else 100

            if per_page > 100:
                return Response(
                    'You must enter either no value for per_page or an integer <= 100.',
                    status=400,
                    mimetype='text/plain'
                )

            links = []
            links.append('<http://www.w3.org/ns/ldp#Resource>; rel="type"')
            links.append(
                '<http://www.w3.org/ns/ldp#Page>; rel="type"')  # signalling that this is, in fact, a resource described in pages
            links.append('<{}?per_page={}>; rel="first"'.format(config.URI_DATASET_INSTANCE_BASE, per_page))

            # if this isn't the first page, add a link to "prev"
            if page != 1:
                prev_page = page - 1
                links.append('<{}?per_page={}&page={}>; rel="prev"'.format(
                    config.URI_DATASET_INSTANCE_BASE,
                    per_page,
                    prev_page
                ))
            else:
                prev_page = None

            # add a link to "next" and "last"
            try:
                no_of_objects = 9200  # TODO replace this magic number
                last_page = int(round(no_of_objects / per_page, 0)) + 1  # same as math.ceil()

                # if we've gotten the last page value successfully, we can choke if someone enters a larger value
                if page > last_page:
                    return Response(
                        'You must enter either no value for page or an integer <= {} which is the last page number.'
                            .format(last_page),
                        status=400,
                        mimetype='text/plain'
                    )

                # add a link to "next"
                if page != last_page:
                    next_page = page + 1
                    links.append(
                        '<{}?per_page={}&page={}>; rel="next"'.format(config.URI_DATASET_INSTANCE_BASE, per_page, next_page))
                else:
                    next_page = None

                # add a link to "last"
                links.append(
                    '<{}?per_page={}&page={}>; rel="last"'.format(config.URI_DATASET_INSTANCE_BASE, per_page, last_page))
            except:
                # if there's some error in getting the no of object, add the "next" link but not the "last" link
                next_page = page + 1
                links.append(
                    '<{}?per_page={}&page={}>; rel="next"'.format(config.URI_DATASET_INSTANCE_BASE, per_page, next_page))

            headers = {
                'Link': ', '.join(links)
            }

            class_uri_of_register_items = 'http://reference.data.gov.au/def/ont/dataset#Dataset'
            return register.RegisterRenderer(request, class_uri_of_register_items, None, page, per_page, prev_page, next_page, last_page) \
                .render(view, mime_format, extra_headers=headers)

    except LdapiParameterError as e:
        return client_error_Response(str(e))


@classes.route('/doc/dataset/ga/<string:dataset_id>')
def dataset(dataset_id):
    """
    A single Address

    :param dataset_id:
    :return: LDAPI views of a single Address
    """
    # lists the views and formats available for class type C
    c = config.URI_DATASET_CLASS
    views_formats = LDAPI.get_classes_views_formats().get(c)

    try:
        view, mimetype = LDAPI.get_valid_view_and_format(
            request.args.get('_view'),
            request.args.get('_format'),
            views_formats
        )

        # if alternates model, return this info from file
        if view == 'alternates':
            instance_uri = config.URI_DATASET_INSTANCE_BASE + dataset_id
            del views_formats['renderer']
            return render_alternates_view(
                c,
                uparse.quote_plus(c),
                instance_uri,
                uparse.quote_plus(instance_uri),
                views_formats,
                request.args.get('_format')
            )
        else:
            from model.dataset import DatasetRenderer
            try:
                s = DatasetRenderer(dataset_id)
                return s.render(view, mimetype)
            except ValueError:
                return render_template('dataset_no_record.html')

    except LdapiParameterError as e:
        return client_error_Response(str(e))
