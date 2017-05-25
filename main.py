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


if __name__ == '__main__':
    test_make_html()
