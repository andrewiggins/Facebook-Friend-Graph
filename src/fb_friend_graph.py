#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        fb_friend_graph.py
# Purpose:     Writes a graphml file
#
# Author:      Andre Wiggins
#
# Created:     21/12/2010
# Copyright:   (c) Andre Wiggins 2010
# Licence:
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

"""Facebook Friend Graph

All methods and terminology refers to the facebook friends of the user whose
access token is passed into the method graph_mutual_friends.

This module is designed to create a graph of the facebook friends of
a user and the connections between each of the friends. This graph can then be
written to a GraphML file so further analysis and processing may be preformed.
"""

from urllib import quote
from xml.sax.saxutils import escape

import sys
import json
import time
import codecs
import pickle
import os.path
import urllib2
import facebook
import traceback


class MutualFriendGraphMLFile(object):
    """This class writes a GraphML file of the mutual friends of the user the
    class in initialized with.

    GraphML specification: (http://graphml.graphdrawing.org/)
    """

    def __init__(self, user_id, user_name, filename, mode='r'):
        """Initializes the file"""
        self.user = {'id': user_id, 'name': user_name}
        self.filename = filename
        self.names = {}
        self.gfile = codecs.open(filename, mode=mode, encoding='utf-8', errors='replace')

        self.gfile.write('<?xml version="1.0" encoding="UTF-8"?> \n' +
                        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns" \n' +
                        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \n' +
                        'xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns \n' +
                        'http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"> \n' +
                        '\n' +
                        '<key id="name" for="node" attr.name="name" attr.type="string" /> \n' +
                        '\n' +
                        '<graph edgedefault="directed"> \n')

        self.addFriendNode(self.user['id'], self.user['name'])


    def addFriendNode(self, friend_id, friend_name):
        """Writes a node to the file"""
        self.names[friend_id] = friend_name
        return self.gfile.write('<node id="friend%s"><data key="name">%s</data></node>\n' % (friend_id, escape(friend_name)))


    def addFriendNodes(self, friends):
        """Writes a list of friend noes to the file"""
        for friend in friends:
            self.addFriendNode(friend['id'], friend['name'])


    def addFriendEdge(self, source_id, target_id):
        """Writes a connection (edge) between to friends"""
        edge_id = str(source_id) + '->' + str(target_id)
        return self.gfile.write(u'<edge id="edge%s" source="friend%s" target="friend%s" />\n' % (edge_id, source_id, target_id))


    def addFriendEdges(self, friends):
        """Writes a list of friends and their connections to the user and
        other nodes"""
        for friend1_id in friends:
            self.writeComment(u"%s" % escape(self.names[friend1_id]))
            self.addFriendEdge(self.user['id'], friend1_id)

            for friend2_id in friends[friend1_id]:
                self.addFriendEdge(friend1_id, friend2_id)


    def write(self, s):
        """Writes a generic string to the file"""
        self.gfile.write(s)


    def writeComment(self, s):
        """Writes a comment to the file"""
        return self.write("<!-- %s -->\n" % s)

    def close(self):
        """Closes the graph and closes the file"""
        self.write("</graph></graphml>")
        self.gfile.close()


def get_mutual_friends(source_uid, target_uid, access_token):
    """Gets the mutual friends of the tow user ids using the passed
    in access_token
    """
    url = 'https://api.facebook.com/method/friends.getMutualFriends?source_uid=%s&target_uid=%s&access_token=%s&format=json'
    t = (quote(s) for s in [source_uid, target_uid, access_token])
    url = url % tuple(t)

    req = urllib2.Request(url)

    return json.loads(urllib2.urlopen(req).read())


def load_mutual_friends(directory, user):
    """Reads a dictionary of mutual friends from a pickled file"""
    obj = {}
    filename = directory + "%s(%s).mutualfriends.pickle" % (user['name'].strip().replace(' ','').lower(), user['id'])
    if os.path.exists(filename):
        pfile = open(filename, 'r')
        obj = pickle.load(pfile)
        pfile.close()
    return obj


def pickle_mutual_friends(directory, user, mutual_friends):
    """Pickles a dictionary of mutual friends to the file"""
    filename = directory + "%s(%s).mutualfriends.pickle" % (user['name'].strip().replace(' ','').lower(), user['id'])
    pfile = open(filename, 'w')
    pickle.dump(mutual_friends, pfile)
    pfile.close()


def load_write_directory(name):
    """Returns the directory the files are to be created in and creates it if
    necessary.
    """
    directory = "FacebookData/%s/" % name
    if (not os.path.exists(directory)):
        os.mkdir(directory)

    return directory


def write_mutual_friends(filename, me, my_friends, my_mutual_friends):
    """Writes the nodes (my friends) and edges (mutual friends) to a
    GraphML file.
    """
    gfile = MutualFriendGraphMLFile(me['id'], me['name'], filename, 'w')
    gfile.addFriendNodes(my_friends)
    gfile.addFriendEdges(my_mutual_friends)
    gfile.close()


def remove_old_friends(my_friends, my_mutual_friends):
    """Removes friends from the my_mutual_friends that are no longer friends of
    the user (those not in my_friends)
    """
    if len(my_friends) < len(my_mutual_friends):
        for oldfriend in set(my_mutual_friends.keys()) - set([u['id'] for u in my_friends]):
            my_mutual_friends.pop(oldfriend)

    return my_mutual_friends


def graph_mutual_friends(access_token):
    """Takes the friends of the user whose access_token is passed in to a
    GraphML file and the connections between each of those friends and writes
    them to a GraphML file.
    """
    print 'Access Token: %s' % access_token
    graph = facebook.GraphAPI(access_token)

    me = graph.get_object('me')
    print 'Retrieving my (%s(%s)) friends...' % (me['name'], me['id'])
    my_friends = graph.get_connections(me['id'], 'friends')["data"]

    directory = load_write_directory(me['name'])

    my_mutual_friends = remove_old_friends(my_friends, load_mutual_friends(directory, me))

    try:
        print
        for my_friend, count in zip(my_friends, xrange(len(my_friends))):
            if not my_mutual_friends.has_key(my_friend['id']):
                try:
                    print '%s/%s: Retrieving mutual friends of %s(%s)...' % (count + 1, len(my_friends), my_friend['name'], my_friend['id'])
                except:
                    print str(my_friend['id']) + ' will not print! :('

                my_mutual_friends[my_friend['id']] = get_mutual_friends(me['id'], my_friend['id'], access_token)
            else:
                try:
                    print '%s/%s: %s(%s) mutual friends have already been loaded' % (count + 1,len(my_friends), my_friend['name'], my_friend['id'])
                except:
                    print str(my_friend['id']) + ' will not print! :(' #1087500527
    except Exception as e:
        traceback.print_exc()
    finally:
        print 'Have mutual friends for %s out of %s friends' %(len(my_mutual_friends), len(my_friends))
        print
        print "Creating files in  %s" % os.path.join(os.path.abspath(os.curdir), directory)
        print 'Writing mutual friends to file...'
        pickle_mutual_friends(directory, me, my_mutual_friends)

        filename = directory + "%s(%s).graphml" % (me['name'], me['id'])
        print 'Writing %s...' % filename
        write_mutual_friends(filename, me, my_friends, my_mutual_friends)
        print 'Done!'


def main():
    """runs graph_mutual_friends() on the access_token passed in as a command
    line agrument
    """
    if len(sys.argv) > 1:
        access_token = sys.argv[1]
        graph_mutual_friends(access_token)
    else:
        print 'Please pass in the access_token of the user to use.'


if __name__ == '__main__':
    main()
