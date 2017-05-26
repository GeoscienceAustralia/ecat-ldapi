import os
import sys
import requests
from lxml import etree
from jinja2 import Environment, FileSystemLoader

# ecat_id = int(sys.argv[1])
#
# query = 'http://ecat.ga.gov.au/geonetwork/srv/eng/csw' \
#         '?service=CSW' \
#         '&request=GetRecords' \
#         '&version=2.0.2' \
#         '&namespace=xmlns(csw=http%3A%2F%2Fwww.opengis.net%2Fcat%2Fcsw%2F2.0.2)' \
#         '&outputSchema=http://www.isotc211.org/2005/gmd' \
#         '&constraintLanguage=CQL_TEXT' \
#         '&constraint_language_version=1.1.0' \
#         '&constraint=ResourceIdentifier%20LIKE%20%27{}%27' \
#         '&typeNames=csw:Record' \
#         '&elementSetName=full' \
#         '&resultType=results'.format(ecat_id)
#
# print query
#
# r = requests.get(query)
# xml = r.content
# root = etree.fromstring(xml)
# p = root.xpath(
#     '//gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString',
#     namespaces={
#         'gmd': 'http://www.isotc211.org/2005/gmd',
#         'gco': 'http://www.isotc211.org/2005/gco'
#     }
# )
# uuid = p[0].text
#
# url = 'http://ecat.ga.gov.au/geonetwork/srv/eng/search#!{}'.format(uuid)
#
# print url


def make_html(metadata):
    # render a Jinja2 template after telling it where the templates dir is
    template = Environment(
        loader=FileSystemLoader(os.path.dirname(os.path.realpath(__file__)) + '/templates')
    ) \
        .from_string(open(os.path.dirname(os.path.realpath(__file__)) + '/templates/staticmeta.html').read())

    return template.render(metadata=metadata)


def test_make_html():
    metadata = {
        'identifier': 'http://pid.geoscience.gov.au/dataset/103620',
        'type': 'software',
        'creator': 'Car, N.J., Ip, A.',
        'publisher': 'Geoscience Australia',
        'title': 'ncskos code repository',
        'description': '''A prototype Python, utility called ncskosdump, which wraps the ncdump netCDF reading tool and adds a series of options for the retrieval and display of Linked Data that the tool is able to extract from a netCDF file, including links to vocabulary terms.
The tool is presented in a code repository using the Git distributed version control system.''',
        'created': '2017-01-15',
        'modified': '2017-02-23',
        'rights': 'http://creativecommons.org/licenses/by/4.0/',
        'keywords': ', '.join(['SKOS', 'Linked Data', 'netCDF', 'vocabulary', 'metadata'])
    }

    open('103620.html', 'w').write(make_html(metadata))


def get_metadata_fields_from_gn(uuid):
    # make CSW request
    uri = 'http://ecat.ga.gov.au/geonetwork/srv/eng/xml.metadata.get?uuid={}'.format(uuid)
    r = requests.get(uri)
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


if __name__ == '__main__':
    #test_make_html()
    metadata = get_metadata_fields_from_gn('05bd5519-6a29-4678-a2d5-b0708c8284e8')
    print make_html(metadata)
