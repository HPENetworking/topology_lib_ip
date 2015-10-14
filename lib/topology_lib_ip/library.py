# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Hewlett Packard Enterprise Development LP <asicapi@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
topology_lib_ip communication library implementation.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division


def configure_interface(enode, portlbl, ipv4, up=None, shell=None):
    """
    Configure a interface.

    This communication library function allows to:

    #. Set address of given interface.
    #. Bring up or down the interface, or leave it as it is.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param str portlbl: Port label to configure. Port label will be mapped to
     real port automatically.
    :param str ipv4: IPv4 address and netmask to assign to the interface in
     the form ``'192.168.20.20/24'``.
    :param up: Bring up or down the interface. If ``None``, take no action.
    :type up: bool or None
    :param shell: Shell name to execute commands. If ``None``, use the Engine
     Node default shell.
    :type shell: str or None
    """
    assert portlbl
    assert ipv4

    port = enode.ports[portlbl]

    addr_cmd = 'ip addr add {addr} dev {port}'.format(addr=ipv4, port=port)
    response = enode(addr_cmd, shell=shell)
    assert not response

    if up is not None:
        up_cmd = 'ip link set dev {port} {state}'.format(
            port=port, state='up' if up else 'down'
        )
        response = enode(up_cmd, shell=shell)
        assert not response


def add_route(enode, route, via, shell=None):
    """
    Add a new static route.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param str route: Route to add, an IP in the form ``'192.168.20.20/24'``
     or ``'default'``.
    :param str via: Via for the route as an IP in the form
     ``'192.168.20.20/24'``.
    :param shell: Shell name to execute commands. If ``None``, use the Engine
     Node default shell.
    :type shell: str or None
    """
    cmd = 'ip route add {route} via {via}'.format(route=route, via=via)
    response = enode(cmd, shell=shell)
    assert not response


PING_RE = (
    r'^(?P<transmitted>\d+) packets transmitted, '
    r'(?P<received>\d+) received,'
    r'( \+(?P<errors>\d+) errors,)? '
    r'(?P<loss>\d+)% packet loss, '
    r'time (?P<time_ms>\d+)ms$'
)


def ping(enode, count, destination):
    """
    Perform a ping and parse the result.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param int count: Number of packets to send.
    :param str destination: The destination host.
    """
    assert count > 0
    assert destination

    import re
    ping_re = re.compile(PING_RE)

    ping_raw = enode('ping -c {} {}'.format(count, destination), shell='bash')
    assert ping_raw

    for line in ping_raw.splitlines():
        m = ping_re.match(line)
        if m:
            return m.groupdict()

    assert False, 'Could not parse ping result'


__all__ = [
    'configure_interface',
    'add_route',
    'ping'
]
