import os
import sys
path = os.path.join(request.folder,'modules')
if not path in sys.path: sys.path.append(path)
from oauth2client import client
from apiclient import errors
from oauth2client.client import OAuth2Credentials
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
import gdata.spreadsheets.client
import gdata.gauth
import gspread

import httplib2
try:
    import json
except ImportError:
    from gluon.contrib import simplejson as json

from unicodedata import normalize

def remover_acentos(txt, codif='utf-8'):
    return normalize('NFKD', txt.decode(codif)).encode('ASCII','ignore')

def conversorListaPlanilhasNumeros(row):
    row = [float(ri.replace('.','').replace(',','.').replace('R$ ',''))
            for ri in row if ri != '']
    return row

def get_service(api_name, api_version):
    """
    Get a service that communicates to a Google API.
    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
    Returns:
        A service that is connected to the specified API.
  """


    if(session.credentials is not None):
        credentials = OAuth2Credentials.from_json(session.credentials)
        if(credentials.access_token_expired):
            session.credentials = None
            session.token_expired = True
        else:
            http_auth = credentials.authorize(httplib2.Http())
            service = build(api_name, api_version, http=http_auth)
            session.token_expired = False
            return service
    return None

def get_sheets(keySheet):
    if(session.credentials is not None):
        credentials = OAuth2Credentials.from_json(session.credentials)
        if(credentials.access_token_expired):
            session.credentials = None
            session.token_expired = True
        else:
            http_auth = credentials.authorize(httplib2.Http())
            gc = gspread.authorize(credentials)
            sh = gc.open_by_key(keySheet)
            worksheet = sh.get_worksheet(0)
            list_of_lists = worksheet.get_all_records(empty2zero=False, head=1)
            return list_of_lists

    return None


def batch_callback(request_id, response, exception):
    print "Response for request_id (%s)" % request_id
    print response
    if(exception):
        raise exception
