from controller import functions
import _config as config

def test_make_html():
    metadata = {
        'identifier': 'http://pid.geoscience.gov.au/dataset/103620.xml',
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

    open('103620.xml.html', 'w').write(functions.render_metatag_html(metadata))


if __name__ == '__main__':
    import requests

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
        '''.format(str(111821))

    headers = {
        'Content-Type': 'application/xml'
    }

    r = requests.post(
        config.DATASETS_CSW_ENDPOINT,
        data=csw_request_xml,
        headers=headers,
        verify=True
    )

    print(r.content.decode('utf-8'))
