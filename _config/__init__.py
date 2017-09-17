from os.path import dirname, realpath, join, abspath

APP_DIR = dirname(dirname(realpath(__file__)))
TEMPLATES_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'templates')
STATIC_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'static')
LOGFILE = APP_DIR + '/flask.log'
DEBUG = True


PROXIES = {}

DATASETS_CSW_ENDPOINT = 'https://ecat.ga.gov.au/geonetwork/srv/eng/csw'

URI_DATASET_CLASS = 'http://reference.data.gov.au/def/ont/dataset#Dataset'
URI_DATASET_INSTANCE_BASE = 'http://pid.geoscience.gov.au/dataset/ga/'
