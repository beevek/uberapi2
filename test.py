#!/usr/bin/env python

import cyclone.web
from uberapi2 import uberapi2, UbersmithError
from twisted.internet import reactor, defer
from twisted.python import log
import base64
import sys


uberapi_url = 'https://ubersmith.example.com/api/2.0/'
uberapi_user = 'myapiuser'
uberapi_pass = 'myapipass'


class Login(cyclone.web.RequestHandler):
  '''Simple handler that takes in Basic HTTP authentication
  credentials from the Authorization header, and uses Ubersmith as an
  authentication provider to validate that the credentials belong to a
  *client* or *contact* (not admin user).  Returns 401 on auth
  failure, or 200 with a body containing the Ubersmith clientid on
  success.'''

  @defer.inlineCallbacks
  def get(self):
    msg = None

    if 'Authorization' in self.request.headers:
      try:

        # extract credentials
        auth_type, data = self.request.headers['Authorization'].split()
        try:
          assert auth_type == 'Basic'
          user, password = base64.b64decode(data).split(':', 1)

          # set up uberapi client
          uber = uberapi2(url=uberapi_url, username=uberapi_user,
                          password=uberapi_pass)

          # call the uber.check_login method with the credentials we
          # got from basic auth
          user = yield uber.call('uber.check_login',
                                 {'login': user, 'pass': password})

          # verify the user is a client or contact, not an admin
          assert user['type'] in ('client', 'contact')

          # get the client id from the response
          clientid = int(user['client_id'])

        except AssertionError:
          msg = 'Bad authentication type'
        except UbersmithError, e:
          msg = '%d: %s' % (e.code, e.msg)
        except:
          msg = 'Failed checking credentials'

      except Exception, e:
        msg = 'Require valid Authorization header'

    else:
      msg = 'Credentials required'

    if msg:
      # auth failure, respond with a 401
      raise cyclone.web.HTTPAuthenticationRequired(
        auth_type='Basic', realm='Test Realm')
    else:
      # write the clientid to the response body
      self.write(str(clientid) + "\n")


if __name__ == '__main__':

  app = cyclone.web.Application([
      (r'/login', Login),
      ])

  log.startLogging(sys.stdout)
  reactor.listenTCP(8888, app)
  reactor.run()
