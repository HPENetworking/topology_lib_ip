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

from ipaddress import ip_address


def interface(enode, portlbl, addr=None, up=None, shell=None):
    """
    Configure a interface.

    All parameters left as ``None`` are ignored and thus no configuration
    action is taken for that parameter (left "as-is").

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param str portlbl: Port label to configure. Port label will be mapped to
     real port automatically.
    :param str addr: IPv4 or IPv6 address to add to the interface:
     - IPv4 address and netmask to assign to the interface in the form
     ``'192.168.20.20/24'``.
     - IPv6 address and subnets to assign to the interface in the form
     ``'2001::1/120'``.
    :param bool up: Bring up or down the interface.
    :param str shell: Shell name to execute commands.
     If ``None``, use the Engine Node default shell.
    """
    assert portlbl
    port = enode.ports[portlbl]

    if addr is not None:
        cmd = 'ip addr add {addr} dev {port}'.format(addr=addr, port=port)
        response = enode(cmd, shell=shell)
        assert not response

    if up is not None:
        cmd = 'ip link set dev {port} {state}'.format(
            port=port, state='up' if up else 'down'
        )
        response = enode(cmd, shell=shell)
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


def add_6_route(enode, route, via, shell=None):
    """
    Add a new static route for IPv6.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param str route: Route to add, an IP in the form ``'2001::0/24'``
     or ``'default'``.
    :param str via: Via for the route as an IP in the form
     ``'2000::2'``.
    :param shell: Shell name to execute commands. If ``None``, use the Engine
     Node default shell.
    :type shell: str or None
    """
    cmd = 'ip -6 route add {route} via {via}'.format(route=route, via=via)
    response = enode(cmd, shell=shell)
    assert not response


PING_RE = (
    r'^(?P<transmitted>\d+) packets transmitted, '
    r'(?P<received>\d+) received,'
    r'( \+(?P<errors>\d+) errors,)? '
    r'(?P<loss_pc>\d+)% packet loss, '
    r'time (?P<time_ms>\d+)ms$'
)


def ping(enode, count, destination):
    """
    Perform a ping and parse the result.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param int count: Number of packets to send.
    :param str destination: The destination host.
    :rtype: dict
    :return: The parsed result of the ping command in a dictionary of the form:

     ::

        {
            'transmitted': 0,
            'received': 0,
            'errors': 0,
            'loss_pc': 0,
            'time_ms': 0
        }
    """
    assert count > 0
    assert destination

    addr = ip_address(destination)
    cmd = 'ping'
    if addr.version == 6:
        cmd = 'ping6'

    import re
    ping_re = re.compile(PING_RE)

    ping_raw = enode(
        '{} -c {} {}'.format(cmd, count, destination),
        shell='bash'
    )
    assert ping_raw

    for line in ping_raw.splitlines():
        m = ping_re.match(line)
        if m:
            return {
                k: (int(v) if v is not None else 0)
                for k, v in m.groupdict().items()
            }

    raise Exception('Could not parse ping result')


__all__ = [
    'interface',
    'add_route',
    'add_6_route',
    'ping'
]
