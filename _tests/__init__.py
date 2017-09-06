import functions


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

    open('103620.html', 'w').write(functions.render_metatag_html(metadata))
