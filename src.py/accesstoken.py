#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        accesstoken.py
# Purpose:     User logs into Facebook to get their access token
#
# Author:      Andre Wiggins
#
# Created:     04/01/2011
# Copyright:   (c) Andre Wiggins 2011
# License:
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#-------------------------------------------------------------------------------

"""Facebook Access Token

This module is used to determine a user's Facebook Access Token given a Facebook
App ID (or Client ID).

Usage:
Top-Level:
    $python accesstoken.py app_id
        where app_id is the Facebook Application ID that authorizes you to
        request information from Facebook Users. The access_token is printed.

On Import:
    get_access_token(app_id):
        This is the meat of this module. It opens a web browser with the
        Facebook login screen. Once the user logs in, the function extracts the
        access_token from the URL and returns it
"""


import sys
import urllib.parse
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler


javascript_redirect = '''<script type="text/javascript">
var url = window.location.href.toString()
window.location = url.replace("#", "?")
</script>
'''


html = '''<html>
<head>
<title>{}</title>
</head>

<body>
{}
</body>

</html>
'''


class AccessTokenRequestHandler(BaseHTTPRequestHandler):
    """This class handles the request that the Facebook OAuth API will send once
    the user logs in or cancels the Facebook Authentication
    """


    def do_GET(self):
        """This method extracts the access_token or error from the Facebook
        request after the user logs in or cancels the Facebook Authentication
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.server.access_token = ""
        self.server.error = ""
        output = ""

        if '?' in self.path:
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path)[4])
            if 'access_token' in query:
                self.server.access_token = query['access_token'][0]
                #self.wfile.write(html % ('Thank You!', 'You may now close your browser.'))
                output = html.format('Thank You!', 'You may now close your browser.')
            else:
                self.server.error = query.get('error_reason', ['unknown error: %s' % str(query)])[0]
                if self.server.error == 'user_denied':
                    #self.wfile.write(html % ('Error', 'You must login to Facebook for the software to work.<br/>' +
                    #    'This software does not store any user names or passwords.'))
                    output = html.format('Error', 'You must login to Facebook for the software to work.<br/>' +
                        'This software does not store any user names or passwords.')
                else:
                    #self.wfile.write(html % ('Error', 'Sorry! An error has occurred. Please try again.'))
                    output = html.format('Error', 'Sorry! An error has occurred. Please try again.')
        else:
            #self.wfile.write(html.format('Redirect', javascript_redirect))
            output = html.format('Redirect', javascript_redirect)

        self.wfile.write(bytes(output, 'utf8'))
        #self.wfile.close()


def get_access_token(app_id):
    """Returns the access token of a Facebook user. The app_id is the App ID of
    a Facebook Application that is requesting the users access_token
    """
    login_url = "https://graph.facebook.com/oauth/authorize?client_id=%s&redirect_uri=http://localhost:8008/&type=user_agent&display=popup" % app_id

    server_address = ('', 8008)
    httpd = HTTPServer(server_address, AccessTokenRequestHandler)

    webbrowser.open_new(login_url)
    httpd.handle_request()
    while not httpd.access_token and not httpd.error:
        httpd.handle_request()

    if httpd.error:
        raise Exception(httpd.error)
    else:
        return httpd.access_token


def main():
    """Prints the access_token of the user using the App ID passed in as the
    first command line argument
    """
    if len(sys.argv) > 1:
        app_id = sys.argv[1]
        try:
            access_token = get_access_token(app_id)
        except:
            sys.exit(1)
        print(access_token)
    else:
        print('Please pass in the access_token of the user to use.')


if __name__ == '__main__':
    main()
