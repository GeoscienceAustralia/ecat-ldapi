from .renderer import Renderer
from flask import Response, render_template
from rdflib import Graph, URIRef, RDF, RDFS, XSD, OWL, Namespace, Literal, BNode
import _config as config
from _ldapi import LDAPI
import psycopg2
from psycopg2 import sql


class DatasetRenderer(Renderer):

    def __init__(self, id):
        pass

    def render(self, view, format):
        if format == 'text/html':
            return self.export_html(view=view)
        elif format in LDAPI.get_rdf_mimetypes_list():
            return Response(self.export_rdf(view, format), mimetype=format)
        else:
            return Response('The requested model model is not valid for this class', status=400, mimetype='text/plain')

    def export_html(self, view='ISO19115-2014'):  # defaults to GeoNetworks HTML
        if view == 'dataset':
            # renders a table of basic Dataset-O properties in HTML
            pass
        elif view == 'dct':
            # renders a table of basic DCT properties in HTML
            pass
        elif view == 'ISO19115-2014':
            # redirects to GeoNetwork HTML of ISO19115-2014
            pass
        elif view == 'metatag':
            # renders GeoNetwork-delivered CSW XML as custom HTML
            pass

    def export_xml(self, view='ISO19115-2014', format='text/turtle'):  # defaults to GeoNetworks' ISO XML
        if view == 'agls':
            # renders AGLS in XML
            pass
        elif view == 'agrkms':
            # renders AGRkMS in XML
            pass
        if view == 'dct':
            # renders DCT in XML
            pass
        elif view == 'ISO19115-2014':
            # redirects to GeoNetwork CSW XML
            pass

    def export_rdf(self, view='dataset', format='text/turtle'):
        if view == 'agls':
            # renders an RDF file according to AGLS
            pass
        elif view == 'dataset':
            # renders an RDF file according to Dataset-O
            pass
        elif view == 'dct':
            # renders an RDF file according to DCT
            pass
