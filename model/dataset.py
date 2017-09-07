from .renderer import Renderer
from flask import Response, render_template, redirect
from rdflib import Graph, URIRef, RDF, RDFS, XSD, OWL, Namespace, Literal, BNode
import _config as config
from _ldapi import LDAPI
from jinja2 import Environment, FileSystemLoader
import os
import _config
import requests
from lxml import etree
import datetime


class DatasetRenderer(Renderer):

    def __init__(self, id):
        self.id = id

    def render(self, view, format):
        if format == 'text/html':
            return Response(self.export_html(view), mimetype=format)
        elif format == 'text/xml' or format == 'application/xml':
            if view == 'ISO19115-2014':
                # if it's the ISO view, just redirect to GeoNetwork's CSW
                return redirect(_config.URI_DATASET_INSTANCE_BASE + str(self.id) + '?_format=application/xml')
            else:
                return Response(self.export_xml(view), mimetype=format)
        elif format in LDAPI.get_rdf_mimetypes_list():
            return Response(self.export_rdf(view, format), mimetype=format)
        else:
            return Response('The requested model model is not valid for this class', status=400, mimetype='text/plain')

    def export_html(self, view='ISO19115-2014'):  # defaults to GeoNetworks HTML
        if view == 'dct':
            # renders a table of basic DCT properties in HTML
            metadata = self._get_dct_dict_from_csw_xml()
            metadata['ecat_id'] = str(self.id)
            return render_template(
                'class_dct.html',
                **metadata
            )
        elif view == 'metatag':
            # renders GeoNetwork-delivered CSW XML as custom HTML
            metatag_dict = self._get_metatag_dict_from_csw_xml()
            return self._render_metatag_html(metatag_dict)
        else:  # view == 'ISO19115-2014':
            return render_template(
                'class_ISO19115-2014.html',
                dataset_uri=config.URI_DATASET_INSTANCE_BASE + str(self.id)
            )

    def export_xml(self, view='ISO19115-2014'):  # defaults to GeoNetworks' ISO XML
        if view == 'agls':
            # renders AGLS in XML
            agls_metadata_dict = self._get_agls_dict_from_csw_xml()
            return self._render_agls_xml(agls_metadata_dict)
        elif view == 'agrkms':
            # renders AGRkMS in XML
            pass
        if view == 'dct':
            # renders DCT in XML
            dct_metadata_dict = self._get_dct_dict_from_csw_xml()
            return self._render_dct_xml(dct_metadata_dict)
        elif view == 'ISO19115-2014':
            # redirects to GeoNetwork CSW XML
            # handled by render function
            pass

    def export_rdf(self, view='dataset', format='text/turtle'):
        if view == 'agls':
            # renders an RDF file according to AGLS
            pass
        elif view == 'agrif':
            # renders an RDF file according to AGLS
            agrif_metata_dict = self._get_agrif_dict_from_csw_xml()
            return self._render_agrif_rdf(agrif_metata_dict, format)
        elif view == 'dataset':
            # renders an RDF file according to Dataset-O
            pass
        elif view == 'dct':
            # renders an RDF file according to DCT
            dct_metata_dict = self._get_dct_dict_from_csw_xml()
            return self._render_dct_rdf(dct_metata_dict, format)

    def _get_xml_from_csw(self):
        csw_uri = 'https://public.ecat.ga.gov.au/geonetwork/srv/eng/csw'
        csw_request_xml = '''
            <csw:GetRecords
                service="CSW"
                version="2.0.2"
                resultType="results"
                outputSchema="own"
                xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
                xmlns:ogc="http://www.opengis.net/ogc" 
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2
                http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd">
                <csw:Query typeNames="csw:Record">
                    <csw:ElementSetName>full</csw:ElementSetName>
                    <csw:Constraint version="1.1.0">
                        <ogc:Filter>
                            <ogc:PropertyIsEqualTo>
                                <ogc:PropertyName>AlternateIdentifier</ogc:PropertyName>
                                <ogc:Literal>{}</ogc:Literal>
                            </ogc:PropertyIsEqualTo>
                        </ogc:Filter>
                    </csw:Constraint>
                </csw:Query>
            </csw:GetRecords>
            '''.format(str(self.id))

        headers = {
            'Content-Type': 'application/xml'
        }

        r = requests.post(
            csw_uri,
            data=csw_request_xml,
            headers=headers,
            proxies=_config.PROXIES,
            verify=True
        )
        return etree.fromstring(r.content)

    def _get_xml_from_file(self, file_name):
        return etree.parse(file_name)

    def _get_agls_dict_from_csw_xml(self):
        #root = self._get_xml_from_csw()
        root = self._get_xml_from_file('/Users/car587/work/ecat-ldapi/103620.xml')

        # XPath to all the vars we want
        namespaces = {
            'mdb': 'http://standards.iso.org/iso/19115/-3/mdb/1.0',
            'cit': 'http://standards.iso.org/iso/19115/-3/cit/1.0',
            'gco': 'http://standards.iso.org/iso/19115/-3/gco/1.0',
            'gcx': 'http://standards.iso.org/iso/19115/-3/gcx/1.0',
            'gex': 'http://standards.iso.org/iso/19115/-3/gex/1.0',
            'gml': 'http://www.opengis.net/gml/3.2',
            'lan': 'http://standards.iso.org/iso/19115/-3/lan/1.0',
            'mcc': 'http://standards.iso.org/iso/19115/-3/mcc/1.0',
            'mco': 'http://standards.iso.org/iso/19115/-3/mco/1.0',
            'mmi': 'http://standards.iso.org/iso/19115/-3/mmi/1.0',
            'mrd': 'http://standards.iso.org/iso/19115/-3/mrd/1.0',
            'mri': 'http://standards.iso.org/iso/19115/-3/mri/1.0',
            'mrl': 'http://standards.iso.org/iso/19115/-3/mrl/1.0',
            'xlink': 'http://www.w3.org/1999/xlink',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'geonet': 'http://www.fao.org/geonetwork'
        }

        '''
        mapping from http://www.anzlic.gov.au/sites/default/files/files/Mapping-ANZLIC-metadata-and-AGLS-v2010.pdf
        creator
        date
        available
        created
        dateCopyrighted
        dateLicensed
        issued
        modified
        valid
        description
        title
        alternative
        type
        aggregationLevel
        category
        documentType
        serviceType
        function
        subject
        availability
        identifier
        bibliographicCitation
        publisher
        audience
        coverage
        jurisdiction
        temporal
        spatial
        language
        contributor
        format
        extent
        medium
        mandate
        act
        case
        regulation
        relation
        conformsTo
        hasFormat
        hasPart
        hasVersion
        isBasedOn
        isBasisFor
        isFormatOf
        isPartOf
        isReferencedBy
        isReplacedBy
        isRequiredBy
        isVersionOf
        replaces
        references
        requires
        rights
        accessRights
        license
        protectiveMarking
        rightsHolder
        source
        '''

        '''
        test term set

        title
        modified
        creator
        publisher
        subject
        description
        category
        serviceType
        function
        audience
        availability
        '''

        title = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:title/gco:CharacterString/text()',
            namespaces=namespaces)[0]

        modified = root.xpath(
            '//mdb:MD_Metadata/mdb:dateInfo/cit:CI_Date[cit:dateType/cit:CI_DateTypeCode/@codeListValue="revision"]/cit:date/gco:DateTime/text()',
            namespaces=namespaces)[0]

        # pointOfContact
        creators = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility/cit:party/cit:CI_Individual/cit:name/gco:CharacterString/text()',
            namespaces=namespaces)

        publisher = 'Geoscience Australia'

        subjects = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:descriptiveKeywords/mri:MD_Keywords/mri:keyword/gco:CharacterString/text()',
            namespaces=namespaces)

        description = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:abstract/gco:CharacterString/text()',
            namespaces=namespaces)[0]

        category = 'category x'

        serviceType = 'service type x'

        function = 'function x'

        audience = 'audience x'

        availability = 'availability x'

        return {
            'identifier': str(self.id),
            'title': title,
            'modified': modified,
            'creator': '; '.join(creators),
            'publisher': publisher,
            'subject': '; '.join(subjects),
            'description': description,
            'category': category,
            'serviceType': serviceType,
            'function': function,
            'audience': audience,
            'availability': availability
        }

    def _render_agls_xml(self, metadata_dict):
        # render a Jinja2 template after telling it where the templates dir is
        template_file = open(
            os.path.join(
                _config.TEMPLATES_DIR,
                'class_agls.xml'
            )
        ).read()
        template = Environment(loader=FileSystemLoader(_config.TEMPLATES_DIR)).from_string(template_file)

        return template.render(**metadata_dict)

    def _get_agrif_dict_from_csw_xml(self):
        root = self._get_xml_from_csw()

        # XPath to all the vars we want
        namespaces = {
            'mdb': 'http://standards.iso.org/iso/19115/-3/mdb/1.0',
            'cit': 'http://standards.iso.org/iso/19115/-3/cit/1.0',
            'gco': 'http://standards.iso.org/iso/19115/-3/gco/1.0',
            'gcx': 'http://standards.iso.org/iso/19115/-3/gcx/1.0',
            'gex': 'http://standards.iso.org/iso/19115/-3/gex/1.0',
            'gml': 'http://www.opengis.net/gml/3.2',
            'lan': 'http://standards.iso.org/iso/19115/-3/lan/1.0',
            'mcc': 'http://standards.iso.org/iso/19115/-3/mcc/1.0',
            'mco': 'http://standards.iso.org/iso/19115/-3/mco/1.0',
            'mmi': 'http://standards.iso.org/iso/19115/-3/mmi/1.0',
            'mrd': 'http://standards.iso.org/iso/19115/-3/mrd/1.0',
            'mri': 'http://standards.iso.org/iso/19115/-3/mri/1.0',
            'mrl': 'http://standards.iso.org/iso/19115/-3/mrl/1.0',
            'xlink': 'http://www.w3.org/1999/xlink',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'geonet': 'http://www.fao.org/geonetwork'
        }

        title = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:title/gco:CharacterString/text()',
            namespaces=namespaces)[0]

        created = root.xpath(
            '//mdb:MD_Metadata/mdb:dateInfo/cit:CI_Date[cit:dateType/cit:CI_DateTypeCode/@codeListValue="creation"]/cit:date/gco:DateTime/text()',
            namespaces=namespaces)[0]

        modified = root.xpath(
            '//mdb:MD_Metadata/mdb:dateInfo/cit:CI_Date[cit:dateType/cit:CI_DateTypeCode/@codeListValue="revision"]/cit:date/gco:DateTime/text()',
            namespaces=namespaces)[0]

        # pointOfContact
        creators = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility/cit:party/cit:CI_Individual/cit:name/gco:CharacterString/text()',
            namespaces=namespaces)

        publisher = 'Geoscience Australia'

        subjects = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:descriptiveKeywords/mri:MD_Keywords/mri:keyword/gco:CharacterString/text()',
            namespaces=namespaces)

        description = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:abstract/gco:CharacterString/text()',
            namespaces=namespaces)[0]

        audience = 'audience x'

        '''
        # Digital Artefact
        <mdb:MD_Metadata>
            <mdb:distributionInfo>
                <mrd:MD_Distribution>
                    <mrd:MD_Format>
                        <mrd:formatDistributor>
                            <mrd:MD_Distributor>
                                <mrd:distributorTransferOptions>
                                    <mrd:MD_DigitalTransferOptions>
                                        <mrd:onLine>
                                            <cit:CI_OnlineResource>
                                                <cit:linkage>
                                                    <gco:CharacterString>https://github.com/GeoscienceAustralia/ncskos

        '''
        digital_artefacts = root.xpath(
            '//mdb:MD_Metadata/mdb:distributionInfo/mrd:MD_Distribution/mrd:distributionFormat/mrd:MD_Format/mrd:formatDistributor/mrd:MD_Distributor/mrd:distributorTransferOptions/mrd:MD_DigitalTransferOptions/mrd:onLine/cit:CI_OnlineResource/cit:linkage/gco:CharacterString/text()',
            namespaces=namespaces)

        if len(digital_artefacts) > 0:
            digital_artefact = digital_artefacts[0]
        else:
            digital_artefact = None



        return {
            'identifier': _config.URI_DATASET_INSTANCE_BASE + str(self.id),
            'title': title,
            'created': created,
            'modified': modified,
            'creator': '; '.join(creators),
            'publisher': publisher,
            'subjects': subjects,
            'description': description,
            'audience': audience,
            'digital_artefact': digital_artefact
        }

    def _render_agrif_rdf(self, metadata_dict, format):
        g = Graph()

        AGRIF = Namespace('http://reference.data.gov.au/def/ont/agrif#')
        g.bind('agrif', AGRIF)

        AUROLE = Namespace('http://communications.data.gov.au/def/role/')
        g.bind('aurole', AUROLE)

        PROV = Namespace('http://www.w3.org/ns/prov#')
        g.bind('prov', PROV)

        GEO = Namespace('http://www.opengis.net/ont/geosparql#')
        g.bind('geo', GEO)

        # Record basics
        this_record = URIRef(config.URI_DATASET_INSTANCE_BASE + str(self.id))
        g.add((this_record, RDF.type, AGRIF.Record))
        g.add((this_record, RDFS.label, Literal('Dataset ' + str(self.id), datatype=XSD.string)))

        # DisposalClass -- GA science datasets in eCat all have the same DisposalClass
        RetainAsNationalArchives = URIRef('http://reference.data.gov.au/def/voc/agrif-disposalclass/RetainAsNationalArchive')
        g.add((this_record, AGRIF.hasDisposalClass, RetainAsNationalArchives))

        # creation
        creation = BNode()
        g.add((creation, RDF.type, AGRIF.CreationEvent))
        g.add((creation, PROV.atTime, Literal(metadata_dict['created'], datatype=XSD.datetime)))
        g.add((this_record, AGRIF.isChangedBy, creation))

        # owner attribution
        owner = BNode()
        owner_agent = BNode()
        g.add((owner_agent, RDF.type, PROV.Agent))
        g.add((owner, RDF.type, PROV.Attribution))
        g.add((owner, PROV.agent, owner_agent))
        g.add((owner, PROV.hadRole, AUROLE.Publisher))
        g.add((owner_agent, RDFS.label, Literal('Geoscience Australia', datatype=XSD.string)))
        g.add((this_record, PROV.qualifiedAttribution, owner))

        # coverage
        geometry = BNode()
        g.add((geometry, RDF.type, GEO.Geometry))
        g.add((
            geometry,
            GEO.asWKT,
            Literal(
                'SRID=8311;POLYGON((140 -32.57, 141 -32.57, 141 -33.08, 141 -33.08, 140 -32.57))',
            datatype=GEO.wktLiteral)
        ))
        coverage = BNode()
        g.add((coverage, RDF.type, AGRIF.SpatialCoverage))
        g.add((coverage, GEO.hasGeometry, geometry))
        g.add((this_record, AGRIF.hasCoverage, coverage))

        # Digital Artefact
        if metadata_dict.get('digital_artefact') is not None:
            g.add((this_record, AGRIF.recordOf, URIRef(metadata_dict['digital_artefact'])))



        return g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(format))

    def _get_dct_dict_from_csw_xml(self):
        root = self._get_xml_from_csw()

        # XPath to all the vars we want
        namespaces = {
            'mdb': 'http://standards.iso.org/iso/19115/-3/mdb/1.0',
            'cit': 'http://standards.iso.org/iso/19115/-3/cit/1.0',
            'gco': 'http://standards.iso.org/iso/19115/-3/gco/1.0',
            'gcx': 'http://standards.iso.org/iso/19115/-3/gcx/1.0',
            'gex': 'http://standards.iso.org/iso/19115/-3/gex/1.0',
            'gml': 'http://www.opengis.net/gml/3.2',
            'lan': 'http://standards.iso.org/iso/19115/-3/lan/1.0',
            'mcc': 'http://standards.iso.org/iso/19115/-3/mcc/1.0',
            'mco': 'http://standards.iso.org/iso/19115/-3/mco/1.0',
            'mmi': 'http://standards.iso.org/iso/19115/-3/mmi/1.0',
            'mrd': 'http://standards.iso.org/iso/19115/-3/mrd/1.0',
            'mri': 'http://standards.iso.org/iso/19115/-3/mri/1.0',
            'mrl': 'http://standards.iso.org/iso/19115/-3/mrl/1.0',
            'xlink': 'http://www.w3.org/1999/xlink',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'geonet': 'http://www.fao.org/geonetwork'
        }

        title = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:title/gco:CharacterString/text()',
            namespaces=namespaces)[0]

        created = root.xpath(
            '//mdb:MD_Metadata/mdb:dateInfo/cit:CI_Date[cit:dateType/cit:CI_DateTypeCode/@codeListValue="creation"]/cit:date/gco:DateTime/text()',
            namespaces=namespaces)[0]

        modified = root.xpath(
            '//mdb:MD_Metadata/mdb:dateInfo/cit:CI_Date[cit:dateType/cit:CI_DateTypeCode/@codeListValue="revision"]/cit:date/gco:DateTime/text()',
            namespaces=namespaces)[0]

        # pointOfContact
        creators = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility/cit:party/cit:CI_Individual/cit:name/gco:CharacterString/text()',
            namespaces=namespaces)

        publisher = 'Geoscience Australia'

        subjects = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:descriptiveKeywords/mri:MD_Keywords/mri:keyword/gco:CharacterString/text()',
            namespaces=namespaces)

        description = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:abstract/gco:CharacterString/text()',
            namespaces=namespaces)[0]

        audience = 'audience x'

        return {
            'identifier': _config.URI_DATASET_INSTANCE_BASE + str(self.id),
            'title': title,
            'created': created,
            'modified': modified,
            'creator': '; '.join(creators),
            'publisher': publisher,
            'subjects': subjects,
            'description': description,
            'audience': audience
        }

    def _render_dct_xml(self, metadata_dict):
        # render a Jinja2 template after telling it where the templates dir is
        template_file = open(
            os.path.join(
                _config.TEMPLATES_DIR,
                'class_dct.xml'
            )
        ).read()
        template = Environment(loader=FileSystemLoader(_config.TEMPLATES_DIR)).from_string(template_file)

        return template.render(**metadata_dict)

    def _render_dct_rdf(self, metadata_dict, format):
        g = Graph()
        DCT = Namespace('http://reference.data.gov.au/def/ont/agrif#')
        g.bind('dct', DCT)

        DTYPES = Namespace('http://www.w3.org/ns/dcat-vocabulary#')
        g.bind('dcmitype', DTYPES)

        this_uri = URIRef(config.URI_DATASET_INSTANCE_BASE + str(self.id))
        g.add((this_uri, RDF.type, DTYPES.Dataset))

        g.add((this_uri, DCT.title, Literal(metadata_dict['title'], datatype=XSD.string)))
        g.add((this_uri, DCT.created, Literal(metadata_dict['created'], datatype=XSD.date)))
        g.add((this_uri, DCT.modified, Literal(metadata_dict['modified'], datatype=XSD.date)))
        g.add((this_uri, DCT.creator, Literal(metadata_dict['creator'], datatype=XSD.string)))
        g.add((this_uri, DCT.publisher, Literal(metadata_dict['publisher'], datatype=XSD.string)))
        for subject in metadata_dict['subjects']:
            g.add((this_uri, DCT.subject, Literal(subject, datatype=XSD.string)))
        g.add((this_uri, DCT.description, Literal(metadata_dict['description'], datatype=XSD.string)))
        g.add((this_uri, DCT.audience, Literal('audience x', datatype=XSD.string)))

        return g.serialize(format=format)

    def _get_metatag_dict_from_csw_xml(self):
        root = self._get_xml_from_csw()

        # XPath to all the vars we want
        namespaces = {
            'mdb': 'http://standards.iso.org/iso/19115/-3/mdb/1.0',
            'cit': 'http://standards.iso.org/iso/19115/-3/cit/1.0',
            'gco': 'http://standards.iso.org/iso/19115/-3/gco/1.0',
            'gcx': 'http://standards.iso.org/iso/19115/-3/gcx/1.0',
            'gex': 'http://standards.iso.org/iso/19115/-3/gex/1.0',
            'gml': 'http://www.opengis.net/gml/3.2',
            'lan': 'http://standards.iso.org/iso/19115/-3/lan/1.0',
            'mcc': 'http://standards.iso.org/iso/19115/-3/mcc/1.0',
            'mco': 'http://standards.iso.org/iso/19115/-3/mco/1.0',
            'mmi': 'http://standards.iso.org/iso/19115/-3/mmi/1.0',
            'mrd': 'http://standards.iso.org/iso/19115/-3/mrd/1.0',
            'mri': 'http://standards.iso.org/iso/19115/-3/mri/1.0',
            'mrl': 'http://standards.iso.org/iso/19115/-3/mrl/1.0',
            'xlink': 'http://www.w3.org/1999/xlink',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'geonet': 'http://www.fao.org/geonetwork',
            'srv': 'http://standards.iso.org/iso/19115/-3/srv/2.0'
        }

        uuid = root.xpath(
            '//mdb:MD_Metadata/mdb:metadataIdentifier/mcc:MD_Identifier/mcc:code/gco:CharacterString/text()',
            namespaces=namespaces)[0]

        title = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:title/gco:CharacterString/text()|'
            '//mdb:MD_Metadata/mdb:identificationInfo/srv:SV_ServiceIdentification/mri:citation/cit:CI_Citation/cit:title/gco:CharacterString/text()',
            namespaces=namespaces)[0]

        type = root.xpath(
            '//mdb:MD_Metadata/mdb:metadataScope/mdb:MD_MetadataScope/mdb:resourceScope/mcc:MD_ScopeCode/@codeListValue',
            namespaces=namespaces)[0]

        description = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:abstract/gco:CharacterString/text()|'
            '//mdb:MD_Metadata/mdb:identificationInfo/srv:SV_ServiceIdentification/mri:abstract/gco:CharacterString/text()',
            namespaces=namespaces)[0]

        # pointOfContact
        creators = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility/cit:party/cit:CI_Individual/cit:name/gco:CharacterString/text()|'
            '//mdb:MD_Metadata/mdb:identificationInfo/srv:SV_ServiceIdentification/mri:pointOfContact/cit:CI_Responsibility/cit:party/cit:CI_Organisation/cit:name/gco:CharacterString/text()',
            namespaces=namespaces)

        if len(creators) > 1:
            if creators[0] == creators[1]:
                creator = creators[0]
            else:
                creator = ', '.join(creators)
        else:
            creator = creators[0]

        publisher = 'Geoscience Australia'

        created = root.xpath(
            '//mdb:MD_Metadata/mdb:dateInfo/cit:CI_Date[cit:dateType/cit:CI_DateTypeCode/@codeListValue="creation"]/cit:date/gco:DateTime/text()',
            namespaces=namespaces)[0]

        created = datetime.datetime.strptime(created, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')

        modified = root.xpath(
            '//mdb:MD_Metadata/mdb:dateInfo/cit:CI_Date[cit:dateType/cit:CI_DateTypeCode/@codeListValue="revision"]/cit:date/gco:DateTime/text()',
            namespaces=namespaces)

        if len(modified) < 1:
            modified = ''
        else:
            modified = datetime.datetime.strptime(modified[0], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')

        rights_title = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:resourceConstraints/mco:MD_LegalConstraints/mco:reference/cit:CI_Citation/cit:title/gco:CharacterString/text()|'
            '//mdb:MD_Metadata/mdb:identificationInfo/srv:SV_ServiceIdentification/mri:resourceConstraints/mco:MD_LegalConstraints/mco:reference/cit:CI_Citation/cit:title/gco:CharacterString/text()',
            namespaces=namespaces)

        if len(rights_title) < 1:
            rights_title = ''
        else:
            rights_title = rights_title[0]

        rights_url = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:resourceConstraints/mco:MD_LegalConstraints/mco:reference/cit:CI_Citation/cit:onlineResource/cit:CI_OnlineResource/cit:linkage/gco:CharacterString/text()|'
            '//mdb:MD_Metadata/mdb:identificationInfo/srv:SV_ServiceIdentification/mri:resourceConstraints/mco:MD_LegalConstraints/mco:reference/cit:CI_Citation/cit:onlineResource/cit:CI_OnlineResource/cit:linkage/gco:CharacterString/text()',
            namespaces=namespaces)

        if len(rights_url) < 1:
            rights_url = ''
        else:
            rights_url = rights_url[0]

        if rights_title != '':
            rights = rights_title + ' (' + rights_url + ')'
        else:
            rights = ''

        keywords = root.xpath(
            '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:descriptiveKeywords/mri:MD_Keywords/mri:keyword/gco:CharacterString/text()|'
            '//mdb:MD_Metadata/mdb:identificationInfo/srv:SV_ServiceIdentification/mri:descriptiveKeywords/mri:MD_Keywords/mri:keyword/gco:CharacterString/text()',
            namespaces=namespaces)

        return {
            'uuid': uuid,
            'identifier': str(self.id),
            'uri': _config.URI_DATASET_INSTANCE_BASE + str(self.id),
            'type': type,
            'title': title,
            'description': description,
            'creator': creator,
            'publisher': publisher,
            'created': created,
            'modified': modified,
            'rights': rights,
            'keywords': ', '.join(keywords)
        }

    def _render_metatag_html(self, metadata_dict):
        # render a Jinja2 template after telling it where the templates dir is
        template_file = open(
            os.path.join(
                _config.TEMPLATES_DIR,
                'class_metatag.html'
            )
        ).read()
        template = Environment(loader=FileSystemLoader(_config.TEMPLATES_DIR)).from_string(template_file)

        return template.render(**metadata_dict)
