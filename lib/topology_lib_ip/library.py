# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Hewlett Packard Enterprise Development LP
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

from ipaddress import ip_address, ip_network, ip_interface


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
        assert ip_interface(addr)
        cmd = 'ip addr add {addr} dev {port}'.format(addr=addr, port=port)
        response = enode(cmd, shell=shell)
        assert not response

    if up is not None:
        cmd = 'ip link set dev {port} {state}'.format(
            port=port, state='up' if up else 'down'
        )
        response = enode(cmd, shell=shell)
        assert not response


def sub_interface(enode, portlbl, subint, addr=None, up=None, shell=None):
    """
    Configure a subinterface.

    All parameters left as ``None`` are ignored and thus no configuration
    action is taken for that parameter (left "as-is").
    Sub interfaces can only be configured if the device exists.
    If you want to enable the sub interface, it will enable the interface
    as well.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param str portlbl: Port label to configure. Port label will be mapped to
     real port automatically.
    :param str subint: The suffix of the interface.
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
    assert subint
    port = enode.ports[portlbl]

    if addr is not None:
        assert ip_interface(addr)
        cmd = 'ip addr add {addr} dev {port}.{subint}'.format(addr=addr,
                                                              port=port,
                                                              subint=subint)
        response = enode(cmd, shell=shell)
        assert not response

    if up is not None:
        if up:
            interface(enode, portlbl, up=up)

        cmd = 'ip link set dev {port}.{subint} {state}'.format(
            port=port, subint=subint, state='up' if up else 'down'
        )
        response = enode(cmd, shell=shell)
        assert not response


def remove_ip(enode, portlbl, addr, shell=None):
    """
    Remove an IP address from an interface.

    All parameters left as ``None`` are ignored and thus no configuration
    action is taken for that parameter (left "as-is").

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param str portlbl: Port label to configure. Port label will be mapped to
     real port automatically.
    :param str addr: IPv4 or IPv6 address to remove from the interface:
     - IPv4 address to remove from the interface in the form
     ``'192.168.20.20'`` or ``'192.168.20.20/24'``.
     - IPv6 address to remove from the interface in the form
     ``'2001::1'`` or ``'2001::1/120'``.
    :param str shell: Shell name to execute commands.
     If ``None``, use the Engine Node default shell.
    """
    assert portlbl
    assert ip_interface(addr)
    port = enode.ports[portlbl]

    cmd = 'ip addr del {addr} dev {port}'.format(addr=addr, port=port)
    response = enode(cmd, shell=shell)
    assert not response


def add_route(enode, route, via, shell=None):
    """
    Add a new static route.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param str route: Route to add, an IP in the form ``'192.168.20.20/24'``
     or ``'2001::0/24'`` or ``'default'``.
    :param str via: Via for the route as an IP in the form
     ``'192.168.20.20/24'`` or ``'2001::0/24'``.
    :param shell: Shell name to execute commands. If ``None``, use the Engine
     Node default shell.
    :type shell: str or None
    """
    via = ip_address(via)

    version = '-4'
    if (via.version == 6) or \
            (route != 'default' and ip_network(route).version == 6):
        version = '-6'

    cmd = 'ip {version} route add {route} via {via}'.format(
        version=version, route=route, via=via
    )

    response = enode(cmd, shell=shell)
    assert not response


def add_link_type_vlan(enode, portlbl, name, vlan_id, shell=None):
    """
    Add a new virtual link with the type set to VLAN.

    Creates a new vlan device {name} on device {port}.
    Will raise an exception if value is already assigned.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param str portlbl: Port label to configure. Port label will be mapped
     automatically.
    :param str name: specifies the name of the new virtual device.
    :param str vlan_id: specifies the VLAN identifier.
    :param str shell: Shell name to execute commands. If ``None``, use the
     Engine Node default shell.
    """
    assert name
    if name in enode.ports:
        raise ValueError('Port {name} already exists'.format(name=name))

    assert portlbl
    assert vlan_id
    port = enode.ports[portlbl]

    cmd = 'ip link add link {dev} name {name} type vlan id {vlan_id}'.format(
        dev=port, name=name, vlan_id=vlan_id)

    response = enode(cmd, shell=shell)
    assert not response, 'Cannot add virtual link {name}'.format(name=name)

    enode.ports[name] = name


def remove_link_type_vlan(enode, name, shell=None):
    """
    Delete a virtual link.

    Deletes a vlan device with the name {name}.
    Will raise an expection if the port is not already present.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param str name: specifies the name of the new
     virtual device.
    :param str shell: Shell name to execute commands. If ``None``, use the
     Engine Node default shell.
    """
    assert name
    if name not in enode.ports:
        raise ValueError('Port {name} doesn\'t exists'.format(name=name))

    cmd = 'ip link del link dev {name}'.format(name=name)

    response = enode(cmd, shell=shell)
    assert not response, 'Cannot remove virtual link {name}'.format(name=name)

    del enode.ports[name]


__all__ = [
    'interface',
    'remove_ip',
    'add_route',
    'add_link_type_vlan',
    'remove_link_type_vlan',
    'sub_interface'
]
