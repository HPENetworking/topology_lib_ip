=====================================
ip Communication Library for Topology
=====================================

Linux ip command Communication Library for Topology


Documentation
=============

    https://github.com/HPENetworking/topology_lib_ip/tree/master/doc


Changelog
=========

0.2.0
-----

**Changes**

- Updated developer guide to reflect Python 3 development and to not use pip
  from system repositories (as it is too old).

**New**

- Added function ``remove_link_type_vlan`` that allows to remove vlan
  virtual links created with ``add_link_type_vlan``.

**Fixes**

- Fixed issue in ``add_link_type_vlan`` that ignored the ports mapping of the
  node.
- Fixed issue in ``add_link_type_vlan`` that registered the port mapping before
  creating it, causing potential issue if the creation failed.


0.1.0
-----

**New**

- Initial release.


License
=======

::

   Copyright (C) 2015-2016 Hewlett Packard Enterprise Development LP

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing,
   software distributed under the License is distributed on an
   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
   KIND, either express or implied.  See the License for the
   specific language governing permissions and limitations
   under the License.
