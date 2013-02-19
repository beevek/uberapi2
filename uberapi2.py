#!/usr/bin/env python

from twisted.internet import reactor, defer
from twisted.web.client import HTTPClientFactory, _parse
from twisted.internet.ssl import ClientContextFactory
from urllib import urlencode
import base64
from json import loads


# small refactor of twisted.web.client.getPage so we have access to
# factory after the request


def _get_factory(url, *args, **kwargs):
    return HTTPClientFactory(url, *args, **kwargs)


def _get_page(factory):
    if factory.scheme == 'https':
        reactor.connectSSL(factory.host, factory.port,
                           factory, ClientContextFactory())
    else:
        reactor.connectTCP(factory.host, factory.port, factory)
    return factory.deferred


class UbersmithError(Exception):

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg


class uberapi2:
    '''Ubersmith 2.0 API client built on twisted.web.'''

    def __init__(self, url='', username='', password=''):
        self._url = url
        self._username = username
        self._password = password

    @defer.inlineCallbacks
    def call(self, method, params=None):
        # compute the authorization header
        auth = '%s:%s' % (self._username, self._password)
        auth = base64.encodestring(auth).strip()

        # compute the request body
        body = {'method': method}
        if params:
            body.update(params)
        data = urlencode(body)

        headers = {
            'Authorization': 'Basic ' + auth,
            'Content-Type': 'application/x-www-form-urlencoded',
            }

        # make the request
        factory = _get_factory(
            self._url, method='POST',
            postdata=data, headers=headers,
            agent='Twisted/uberapi2')
        rsp = yield _get_page(factory)

        # handle the response -- usually we expect JSON
        content_type = factory.response_headers.get(
            'content-type', [None])[0]
        if content_type == 'application/json':
            rsp = loads(rsp)
            if 'status' not in rsp or not rsp['status']:
                raise UbersmithError(
                    rsp.get('error_code', 0),
                    rsp.get('error_message', 'Unknown error'))
            yield defer.returnValue(rsp.get('data', {}))

        # XXX: could also decode application/xml

        # non-JSON responses are returned directly
        yield defer.returnValue(rsp)
