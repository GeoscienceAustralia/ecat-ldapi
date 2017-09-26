import requests
import re


reg = requests.get('http://pid.geoscience.gov.au/dataset/ga/?_view=metatag')

for m in re.findall(
            '<li><a href="http://pid.geoscience.gov.au/dataset/(\d)\?_view=metatag">http://pid.geoscience.gov.au/dataset/\d4\?_view=metatag</a></li>',
            reg.content
        ):
    print(m)

