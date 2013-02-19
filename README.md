uberapi_2_client
======================================================================

This is a simple [Ubersmith](http://www.ubersmith.com/) APIv2 client
for use with the [Twisted](http://twistedmatrix.com/trac/) Python
framework.

Use it from code running in the Twisted reactor:

    from twisted.internet import defer
    from uberapi2 import uberapi2, UbersmithError

    @defer.inlineCallbacks
    def get_device(device_id):
      uber = uberapi2(url='https://ubersmith.example.com/api/2.0/',
                      username='myapiuser',
                      password='myapipassword')
      dev = yield uber.call('device.get', {'device_id': device_id})
      yield defer.returnValue(dev)

There is an example, built using [Cyclone](http://cyclone.io/), that
implements a very simple web app that accepts credentials via HTTP
Basic Authentication, and verifies against an Ubersmith backend that
the credentials belong to an Ubersmith client or contact.  With all
dependencies installed, set the `uberapi_*` parameters at the top of
the file, and then run it like:

    python test.py

and in another terminal, do:

    curl --basic --user user:pass http://localhost:8888/login

where `user` and `pass` are credentials for a valid Ubersmith client
or contact in your Ubersmith.

Note that your `uberapi_user` must be granted API Access in
Ubersmith's Setup & Admin page.
