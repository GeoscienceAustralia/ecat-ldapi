import requests
import re
from lxml import etree
from io import BytesIO
import itertools


# # reg = requests.get('http://pid.geoscience.gov.au/dataset/ga/?_view=metatag')
# # parser = etree.HTMLParser()
# # tree = etree.parse(BytesIO(reg.content))
#
# # get cached HTML index
tree = etree.parse('index.html')
dataset_uris = tree.xpath("//li/a/text()")

ecat_ids = []
for uri in dataset_uris:
    r = requests.get(uri)
    l = '{}, {}'.format(uri[40:][:-14], r.status_code)
    print(l)
    ecat_ids.append(l)

with open('results.csv', 'w') as f:
    f.writelines(ecat_ids)



#
# # for the first 1,000 datasets, test the metatag view of each for a 200 response
# cnt = 0
# for dataset_uri in dataset_uris[:1000]:
#     r = requests.get(dataset_uri, allow_redirects=True)
#     print(dataset_uri)
#     if r.status_code != 200:
#         print('FAILED')
#     cnt += 1
#
#
#
#
# # print(reg.content.decode('utf-8'))
# #
# # for m in re.findall(
# #             '<li><a href="http://pid.geoscience.gov.au/dataset/(\d)\?_view=metatag">http://pid.geoscience.gov.au/dataset/\d4\?_view=metatag</a></li>',
# #             reg.content.decode('utf-8')
# #         ):
# #     print(m)

# i = 23
# while i < 34:
#     r = requests.get('http://pid.geoscience.gov.au/dataset/ga/{}?_view=metatag'.format(i))
#     print('{}: {}'.format(i, r.status_code))
#     i += 1

# i = 4296
# r = requests.get('http://pid.geoscience.gov.au/dataset/ga/{}?_view=metatag'.format(i))
# print('{}: {}'.format(i, r.status_code))
