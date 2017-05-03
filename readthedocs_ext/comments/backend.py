from __future__ import print_function

import json
import requests

from sphinx.websupport.storage import StorageBackend


class WebStorage(StorageBackend):

    """
    A storage class meant to be used by the Sphinx Builder to store nodes.

    This is super inefficient and a hack right now.
    When in prod we'll store all nodes to be added
    and send them all up at once like with sync_versions.

    """

    def __init__(self, builder=None):
        self.builder = builder
        self.url = self.builder.config.websupport2_base_url
        print("Using Websupport URL: %s" % self.url)

    def _add_server_data(self, data):
        if 'current_version' in self.builder.config.html_context:
            data['version'] = self.builder.config.html_context['current_version']
        if 'slug' in self.builder.config.html_context:
            data['project'] = self.builder.config.html_context['slug']
        if self.builder.current_docname:
            data['page'] = self.builder.current_docname
        if 'commit' in self.builder.config.html_context:
            data['commit'] = self.builder.config.html_context['commit']

    def get_comments(self, node):
        url = self.url + "/_get_comments"
        data = {'node': node}
        self._add_server_data(data)
        r = requests.get(url, params=data)
        if r.status_code == 200:
            return r.json()
        return False

    def get_project_metadata(self, project):
        url = self.url.replace('/websupport', '') + "/api/v2/comments/"
        data = {'project': project}
        r = requests.get(url, params=data)
        if r.status_code == 200:
            return r.json()
        return False

    def get_metadata(self, docname, moderator=None):
        url = self.url + "/_get_metadata"
        data = {'page': docname}
        self._add_server_data(data)
        r = requests.get(url, params=data)
        if r.status_code == 200:
            return r.json()
        return False

    def has_node(self, id):
        url = self.url + "/_has_node"
        data = {'node_id': id, }
        self._add_server_data(data)
        r = requests.get(url, params=data)
        if r.status_code == 200:
            return r.json()['exists']
        return False

    def add_node(self, id, document, source):
        url = self.url + "/_add_node"
        data = {
            'id': id,
            'document': document,
            'source': source
        }
        self._add_server_data(data)
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(data), headers=headers)
        print("Adding node %s" % (r.status_code))
        return r

    def update_node(self, old_hash, new_hash, commit):
        url = self.url + "/_update_node"
        data = {
            'old_hash': old_hash,
            'new_hash': new_hash,
            'commit': commit
        }
        self._add_server_data(data)
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(data), headers=headers)
        print("Updating node %s" % (r.status_code))
        return r
