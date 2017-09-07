import os
import datetime
import requests
from lxml import etree
from jinja2 import Environment, FileSystemLoader
import _config


if __name__ == '__main__':
    print(get_view_metatag_dict_from_csw(103620))
