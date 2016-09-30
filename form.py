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

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_REGISTER_NAME = 'default_register'


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
# [END greeting]


# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):
        register_name = self.request.get('register_name',
                                          DEFAULT_REGISTER_NAME)
        
        trade_query = ClerkshipTrade.query(
            ancestor=register_key(register_name)).order(ClerkshipTrade.student.email)
        trades = trade_query.fetch(10)
        

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'trades': trades,
            'register_name': urllib.quote_plus(register_name),
            'url': url,
            'url_linktext': url_linktext,
            'clerkship_mapping': getClerkshipMapping()
        }

        template = JINJA_ENVIRONMENT.get_template('form.html')
        self.response.write(template.render(template_values))
# [END main_page]


# [START guestbook]
class Register(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        register_name = self.request.get('register_name',
                                          DEFAULT_REGISTER_NAME)
        trade = ClerkshipTrade(parent=register_key(register_name))

        if users.get_current_user():
            trade.student = Student(
                    email=users.get_current_user().email())

        trade.block = int(self.request.get('block'))
        trade.current = self.request.get('current')
        trade.desired = self.request.get('desired')
        
        if trade.is_valid():
            trade.put()

        query_params = {'register_name': register_name}
        self.redirect('/?' + urllib.urlencode(query_params))
# [END guestbook]


# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/register', Register),
], debug=True)
# [END app]
