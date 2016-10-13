#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import urllib
import json

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

import firebase_helper

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_REGISTER_NAME = '1'


# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def register_key(register_name=DEFAULT_REGISTER_NAME):
    """Constructs a Datastore key for a Register entity.

    We use register_name as the key.
    """
    return ndb.Key('Register', register_name)

def getClerkshipMapping():
    return {
        'pcpsych': 'Primary Care / Psych',
        'imneuro': 'Medicine / Neurology',
        'surgem': 'Surgery / Emergency',
        'pedobgyn': 'Pediatrics / ObGyn'
    }


# [START greeting]
class Student(ndb.Model):
    """Sub model for representing an student."""
    email = ndb.StringProperty()


class ClerkshipTrade(ndb.Model):
    """A main model for representing an individual clerkship trade entry."""
    student = ndb.StructuredProperty(Student)
    block = ndb.IntegerProperty(choices = [1, 2, 3, 4])
    current = ndb.StringProperty(choices = getClerkshipMapping().keys())
    desired = ndb.StringProperty(choices = getClerkshipMapping().keys())

    def is_valid(self):
        return self.current != self.desired
        # TODO: add check for update that submitter is same as original

    def get_json(self):
        return {'block': self.block,
                'current': self.current,
                'desired': self.desired,
                'key': self.key.urlsafe(),
                'student': {'email': self.student.email}
                }


# [END greeting]

class List(webapp2.RequestHandler):
    def get(self):
        trades = ClerkshipTrade.query(ancestor=register_key(DEFAULT_REGISTER_NAME)
                                      ).order(ClerkshipTrade.student.email).fetch()

        template = JINJA_ENVIRONMENT.get_template('list.html')
        self.response.write(template.render({'records': trades}))

# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):

        register_name = self.request.get('register_name',
                                          DEFAULT_REGISTER_NAME)
        
        template_values = {
            'register_name': urllib.quote_plus(register_name),
            'clerkship_mapping': getClerkshipMapping()
        }

        template = JINJA_ENVIRONMENT.get_template('form.html')
        print 'writing response with template values'
        self.response.write(template.render(template_values))
# [END main_page]

class Load(webapp2.RequestHandler):
    def get(self):
        # Verify Firebase auth.
        print self.request
        claims = firebase_helper.verify_auth_token(self.request)

        register_name = self.request.get('register_name',
                                          DEFAULT_REGISTER_NAME)
        if claims:
            print 'claims found'
            trade_query = ClerkshipTrade.query(
                ClerkshipTrade.student.email == claims.get('email'),
                ancestor=register_key(register_name))
            trades = trade_query.fetch()
        else:
            trades = []

        data = {}
        for trade in trades:
            data[trade.block] = trade.get_json()
        
        response_obj = {'data': data}

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response_obj))


# [START guestbook]
class Register(webapp2.RequestHandler):

    def post(self):
        # Verify Firebase auth.
        claims = firebase_helper.verify_auth_token(self.request)
        if not claims:
            self.abort(401, detail='Unauthorized access attempted')

        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        register_name = self.request.get('register_name',
                                         DEFAULT_REGISTER_NAME)

        key = self.request.get('key')
        print 'block is ' + self.request.get('block')
        block = int(self.request.get('block'))
        current = self.request.get('current')
        desired = self.request.get('desired')

        if key:
            trade = ndb.Key(urlsafe=key).get()
            trade.current = current
            trade.desired = desired

        else:
            trade = ClerkshipTrade(parent=register_key(register_name))

            trade.student = Student(email=claims.get('email'))
            print trade.student.email
            trade.block = block
            trade.current = current
            trade.desired = desired
        
        if trade.is_valid():
            trade.put()
            print 'trade was put'
            self.response.headers['Content-Type'] = 'application/json'
            response_obj = {'data': trade.get_json()}
            self.response.out.write(json.dumps(response_obj))
        else:
            self.abort(500, detail='Unable to save record')
# [END guestbook]


# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/load', Load),
    ('/register', Register),
    ('/list', List)
], debug=True)
# [END app]
