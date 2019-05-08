import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.conf import settings


class SingletonAmi(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
            class_._instance.cookies = []
            class_._instance.expire = False
            class_._instance.session = requests.Session()
            class_._instance.auth = dict(Action='Login', Username=settings.ASTERISK_AMI_USER, Secret=settings.ASTERISK_AMI_PASS)
            class_._instance.url = settings.ASTERISK_AMI_URL
        return class_._instance


class AsteriskAmi(SingletonAmi):

    def get_auth(self):
        authreq = requests.Request('Get', self.url, params=self.auth).prepare()
        self.cookies = self.session.send(authreq).cookies
        for cookie in self.cookies:
            self.expire = cookie.expires

    def get_response(self, request):
        # type: (object) -> object

        if not hasattr(self, 'expire'):
            self.get_auth()
        if datetime.fromtimestamp(int(self.expire)) > datetime.now() and self.cookies:
            statusreq = requests.Request('Get', self.url, params=request, cookies=self.cookies).prepare()
            response = self.session.send(statusreq).content
            response = BeautifulSoup(response, 'lxml')
            validate = response.findAll('generic')[0].get('response')
            if validate == 'Success':
                return response
            else:
                raise ValueError(message=response.findAll('generic')[0].get('message'))
        else:
            self.get_auth()
            return self.get_response(request)

    def get_db(self, family, key):
        return self.get_response(dict(Action='DBGet', Family=family, Key=key))

    def put_db(self, family, key, value):
        return self.get_response(dict(Action='DBPut', Family=family, Key=key, Val=value))

    def del_db(self, family, key):
        return self.get_response(dict(Action='DBDel', Family=family, Key=key))






