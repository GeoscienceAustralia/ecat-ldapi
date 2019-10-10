from .renderer import Renderer
from flask import Response, render_template, send_file
from rdflib import Graph, URIRef, RDF, RDFS, XSD, Namespace, Literal
from _ldapi import LDAPI
import _config as config
import requests
import xml.sax as x
import os


class RegisterRenderer(Renderer):
    def __init__(self, request, uri, endpoints, page, per_page, prev_page, next_page, last_page):
        Renderer.__init__(self, uri, endpoints)

        self.request = request
        self.uri = uri
        self.register = []
        self.g = None
        self.per_page = per_page
        self.page = page
        self.prev_page = prev_page
        self.next_page = next_page
        self.last_page = last_page

        self._get_data_from_csw(page, per_page)

    def _get_data_from_csw(self, page, per_page):
        # make a CSW request for 100 items
        request_xml = self._make_csw_request_xml(page, per_page)
        self.register = self._extract_ecat_ids_stream(self._stream_csw_request(config.DATASETS_CSW_ENDPOINT, request_xml))

    def _stream_csw_request(self, csw_endpoint, request_xml):
        r = requests.post(csw_endpoint,
                          data=request_xml,
                          headers={'Content-Type': 'application/xml'},
                          stream=True)
        return r.raw

    def _make_csw_request_xml(self, start_position, max_records):
        xml_template_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            'view',
            'templates',
            'csw_request_records.xml')
        xml = open(xml_template_path, 'r').read()
        xml = xml.replace('{{ start_position }}', str(start_position))
        xml = xml.replace('{{ max_records }}', str(max_records))
        return xml

    def _extract_ecat_ids_stream(self, result_stream):
        n = IdHandler()
        parser = x.make_parser()
        parser.setContentHandler(n)
        parser.setFeature(x.handler.feature_namespaces, True)
        parser.parse(result_stream)

        return sorted(n.ids)

    def render(self, view, mimetype, extra_headers=None):
        if view == 'reg':
            # is an RDF format requested?
            if mimetype in LDAPI.get_rdf_mimetypes_list():
                # it is an RDF format so make the graph for serialization
                self._make_reg_graph(view)
                rdflib_format = LDAPI.get_rdf_parser_for_mimetype(mimetype)
                return Response(
                    self.g.serialize(format=rdflib_format),
                    status=200,
                    mimetype=mimetype,
                    headers=extra_headers
                )
            elif mimetype == 'text/html':
                return Response(
                    render_template(
                        'class_register.html',
                        class_name=self.uri,
                        instance_uri_base=config.URI_DATASET_INSTANCE_BASE,
                        register=self.register,
                        page=self.page,
                        per_page=self.per_page,
                        prev_page=self.prev_page,
                        next_page=self.next_page,
                        last_page=self.last_page
                    ),
                    mimetype='text/html',
                    headers=extra_headers
                )
        elif view == 'staticreg':
            if mimetype in LDAPI.get_rdf_mimetypes_list():
                pass
            elif mimetype == 'text/html':
                return send_file('/var/www/html/datasets.html')
        elif view == 'metatag':
            return send_file('/var/www/html/datasets-metatag.html')
        else:
            return Response('The requested model model is not valid for this class', status=400, mimetype='text/plain')

    def _make_reg_graph(self, model_view):
        self.g = Graph()

        if model_view == 'reg':  # reg is default
            # make the static part of the graph
            REG = Namespace('http://purl.org/linked-data/registry#')
            self.g.bind('reg', REG)

            LDP = Namespace('http://www.w3.org/ns/ldp#')
            self.g.bind('ldp', LDP)

            XHV = Namespace('https://www.w3.org/1999/xhtml/vocab#')
            self.g.bind('xhv', XHV)

            register_uri = URIRef(self.request.base_url)
            self.g.add((register_uri, RDF.type, REG.Register))
            self.g.add((register_uri, RDFS.label, Literal('Address Register', datatype=XSD.string)))

            page_uri_str = self.request.base_url
            if self.per_page is not None:
                page_uri_str += '?per_page=' + str(self.per_page)
            else:
                page_uri_str += '?per_page=100'
            page_uri_str_no_page_no = page_uri_str + '&page='
            if self.page is not None:
                page_uri_str += '&page=' + str(self.page)
            else:
                page_uri_str += '&page=1'
            page_uri = URIRef(page_uri_str)

            # pagination
            # this page
            self.g.add((page_uri, RDF.type, LDP.Page))
            self.g.add((page_uri, LDP.pageOf, register_uri))

            # links to other pages
            self.g.add((page_uri, XHV.first, URIRef(page_uri_str_no_page_no + '1')))
            self.g.add((page_uri, XHV.last, URIRef(page_uri_str_no_page_no + str(self.last_page))))

            if self.page != 1:
                self.g.add((page_uri, XHV.prev, URIRef(page_uri_str_no_page_no + str(self.page - 1))))

            if self.page != self.last_page:
                self.g.add((page_uri, XHV.next, URIRef(page_uri_str_no_page_no + str(self.page + 1))))

            # add all the items
            for item in self.register:
                item_uri = URIRef(self.request.base_url + str(item))
                self.g.add((item_uri, RDF.type, URIRef(self.uri)))
                self.g.add((item_uri, RDFS.label, Literal('Address ID:' + str(item), datatype=XSD.string)))
                self.g.add((item_uri, REG.register, page_uri))


class IdHandler(x.ContentHandler):
    # see http://python.zirael.org/e-sax2.html
    def __init__(self):
        x.ContentHandler.__init__(self)
        self.ids = []
        self.one = False
        self.two = False
        self.three = False
        self.four = False
        self.five = False
        self.six = False
        self.seven = False
        self.parent = []

    # check for a particular sequence of tags:
    # identificationInfo SV_ServiceIdentification citation CI_Citation identifier RS_Identifier code CharacterString
    # this is similar to an XPath query but this function notices every start tag, not just those in the hierarchy
    # above, also anything else in between
    def startElementNS(self, name, qname, attrs):
        uri, localname = name
        # //mdb:MD_Metadata/mdb:alternativeMetadataReference/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/gco:CharacterString/text()
        if localname == 'MD_Metadata':
            self.one = True
        if self.one and localname == 'alternativeMetadataReference':
            self.two = True
        if self.two and localname == 'CI_Citation':
            self.three = True
        if self.three and localname == 'identifier':
            self.four = True
        if self.four and localname == 'MD_Identifier':
            self.five = True
        if self.five and localname == 'code':
            self.six = True
        if self.six and localname == 'CharacterString':
            self.seven = True

    # if the required sequence of start tags is true (all 7 flags are True), record the content
    def characters(self, content):
        if self.one and self.two and self.three and self.four and self.five and self.six and self.seven:
            try:
                self.ids.append(int(content))
            except Exception:
                pass

    # once an eCat ID has been found, reset the stream checker
    def endElementNS(self, name, qname):
        if self.one and self.two and self.three and self.four and self.five and self.six and self.seven:
            self.one = False
            self.two = False
            self.three = False
            self.four = False
            self.five = False
            self.six = False
            self.seven = False