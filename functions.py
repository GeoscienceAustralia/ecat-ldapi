import os
import requests
from lxml import etree
from jinja2 import Environment, FileSystemLoader


def get_metadata_fields_from_gn(uuid):
    # make CSW request
    uri = 'http://ecat.ga.gov.au/geonetwork/srv/eng/xml.metadata.get?uuid={}'.format(uuid)

    proxies = {
        'http': 'http://sun-web-intdev.ga.gov.au:2710',
    }
    r = requests.get(uri, proxies=proxies)
    xml = r.content
    root = etree.fromstring(xml)

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

    type = root.xpath(
        '//mdb:MD_Metadata/mdb:metadataScope/mdb:MD_MetadataScope/mdb:resourceScope/mcc:MD_ScopeCode/@codeListValue',
        namespaces=namespaces)[0]

    description = root.xpath(
        '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:abstract/gco:CharacterString/text()',
        namespaces=namespaces)[0]

    # pointOfContact
    creators = root.xpath(
        '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility/cit:party/cit:CI_Individual/cit:name/gco:CharacterString/text()',
        namespaces=namespaces)

    publisher = 'Geoscience Australia'

    created = root.xpath(
        '//mdb:MD_Metadata/mdb:dateInfo/cit:CI_Date[cit:dateType/cit:CI_DateTypeCode/@codeListValue="creation"]/cit:date/gco:DateTime/text()',
        namespaces=namespaces)[0]

    modified = root.xpath(
        '//mdb:MD_Metadata/mdb:dateInfo/cit:CI_Date[cit:dateType/cit:CI_DateTypeCode/@codeListValue="revision"]/cit:date/gco:DateTime/text()',
        namespaces=namespaces)[0]

    rights_title = root.xpath(
        '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:resourceConstraints/mco:MD_LegalConstraints/mco:reference/cit:CI_Citation/cit:title/gco:CharacterString/text()',
        namespaces=namespaces)[0]

    rights_url = root.xpath(
        '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:resourceConstraints/mco:MD_LegalConstraints/mco:reference/cit:CI_Citation/cit:onlineResource/cit:CI_OnlineResource/cit:linkage/gco:CharacterString/text()',
        namespaces=namespaces)[0]

    rights = rights_title + ' (' + rights_url + ')'

    keywords = root.xpath(
        '//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:descriptiveKeywords/mri:MD_Keywords/mri:keyword/gco:CharacterString/text()',
        namespaces=namespaces)

    return {
        'identifier': 'coming',
        'type': type,
        'title': title,
        'description': description,
        'creator': ', '.join(creators),
        'publisher': publisher,
        'created': created,
        'modified': modified,
        'rights': rights,
        'keywords': ', '.join(keywords)
    }


def make_html(metadata):
    # render a Jinja2 template after telling it where the templates dir is
    template = Environment(
        loader=FileSystemLoader(os.path.dirname(os.path.realpath(__file__)) + '/templates')
    ) \
        .from_string(open(os.path.dirname(os.path.realpath(__file__)) + '/templates/staticmeta.html').read())

    return template.render(metadata=metadata)

