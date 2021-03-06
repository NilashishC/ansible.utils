# -*- coding: utf-8 -*-
# Copyright 2020 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""
The to_paths lookup plugin
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
    lookup: to_paths
    author: Bradley Thornton (@cidrblock)
    version_added: "1.0"
    short_description: Flatten a complex object into a dictionary of paths and values
    description:
        - Flatten a complex object into a dictionary of paths and values.
        - Paths are dot delimited whenever possible
        - Brakets are used for list indicies and keys that contain special characters
        - C(to_paths) is also available as a filter plugin
    options:
      _terms:
        description: The values below provided in the order C(var), C(prepend=), C(wantlist=).
        required: True
      var:
        description: The value of C(var) will be will be used.
        type: raw
        required: True
      prepend:
        description: Prepend each path entry. Useful to add the initial C(var) name.
        type: str
        required: False
      wantlist:
        description: >
            If set to C(True), the return value will always be a list.
            This can also be accomplished using C(query) or C(q) instead of C(lookup).
            U(https://docs.ansible.com/ansible/latest/plugins/lookup.html)
        type: bool

    notes:
"""

EXAMPLES = r"""

#### Simple examples

- ansible.builtin.set_fact:
    a:
      b:
        c:
          d:
          - 0
          - 1
          e:
          - True
          - False

- ansible.builtin.set_fact:
    as_lookup: "{{ lookup('ansible.utils.to_paths', a) }}"
    as_filter: "{{ a|ansible.utils.to_paths }}"

# TASK [set_fact] *****************************************************
# task path: /home/brad/github/dotbracket/site.yaml:17
# ok: [localhost] => changed=false
#   ansible_facts:
#     as_filter:
#       b.c.d[0]: 0
#       b.c.d[1]: 1
#       b.c.e[0]: true
#       b.c.e[1]: false
#     as_lookup:
#       b.c.d[0]: 0
#       b.c.d[1]: 1
#       b.c.e[0]: true
#       b.c.e[1]: false

- name: Use prepend to add the initial variable name
  ansible.builtin.set_fact:
    as_lookup: "{{ lookup('ansible.utils.to_paths', a, prepend=('a')) }}"
    as_filter: "{{ a|ansible.utils.to_paths(prepend='a') }}"

# TASK [Use prepend to add the initial variable name] *****************
# ok: [nxos101] => changed=false
#   ansible_facts:
#     as_filter:
#       a.b.c.d[0]: 0
#       a.b.c.d[1]: 1
#       a.b.c.e[0]: true
#       a.b.c.e[1]: false
#     as_lookup:
#       a.b.c.d[0]: 0
#       a.b.c.d[1]: 1
#       a.b.c.e[0]: true
#       a.b.c.e[1]: false


#### Using a complex object

- name: Make an API call
  uri:
    url: "https://nxos101/restconf/data/openconfig-interfaces:interfaces"
    headers:
      accept: "application/yang.data+json"
    url_password: password
    url_username: admin
    validate_certs: False
  register: result
  delegate_to: localhost

- name: Flatten the complex object
  set_fact:
    flattened: "{{ result.json|ansible.utils.to_paths }}"

# TASK [Flatten the complex object] ********************
# ok: [nxos101] => changed=false
#   ansible_facts:
#     flattened:
#       interfaces.interface[0].config.enabled: 'true'
#       interfaces.interface[0].config.mtu: '1500'
#       interfaces.interface[0].config.name: eth1/71
#       interfaces.interface[0].config.type: ethernetCsmacd
#       interfaces.interface[0].ethernet.config['auto-negotiate']: 'true'
#       interfaces.interface[0].ethernet.state.counters['in-crc-errors']: '0'
#       interfaces.interface[0].ethernet.state.counters['in-fragment-frames']: '0'
#       interfaces.interface[0].ethernet.state.counters['in-jabber-frames']: '0'


"""

RETURN = """
  _raw:
    description:
      - A dictionary of key value pairs
      - The key is the path
      - The value is the value
"""

from ansible.plugins.lookup import LookupBase
from ansible_collections.ansible.utils.plugins.module_utils.common.path import (
    to_paths,
)


class LookupModule(LookupBase):
    def run(self, terms, variables, **kwargs):
        if isinstance(terms, dict):
            terms.update(kwargs)
            res = to_paths(**terms)
        else:
            res = to_paths(*terms, **kwargs)
        if not isinstance(res, list):
            return [res]
        return res
