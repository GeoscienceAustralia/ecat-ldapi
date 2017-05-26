APP_DIR = 'c:/work/surveys-api/'
LOGFILE = APP_DIR + 'surveys-api.log'
DEBUG = True

XML_API_URL_SURVEY_REGISTER = 'http://www.ga.gov.au/www/argus.argus_api.SearchSurveys' \
                              '?pOrder=SURVEYID&pPageno={0}&pNoOfRecordsPerPage={1}'
XML_API_URL_SURVEY = 'http://www.ga.gov.au/www/argus.argus_api.survey?pSurveyNo={}'

BASE_URI_SAMPLE = 'http://pid.geoscience.gov.au/survey/'

ADMIN_EMAIL = 'dataman@ga.gov.au'