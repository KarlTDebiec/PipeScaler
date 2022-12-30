#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""pipescaler package.

Code is separated between that which is not specific to any particular object type and
that which is. Code that is specific to a particular object type is isolated within a
subpackage, whose organization mirrors that of the non-specific code. At each level,
code is organized into the following sub-packages:
* analytics
* cli: Command line interfaces
* common: Common code not specific to pipescaler; this is a subrepo shared with other
  packages
* core: Core code including abstract base classes and miscellaneous functions
* data: Miscellaneous raw files needed for other functionality
* models: Machine learning models
* operators: Code that performs operations on objects
* pipelines: pipelines
* runners: Code related to running external tools
* testing: Code related to testing
* utilities: Tools that perform miscellaneous tasks

Note that the above sub-packages are not necessarily present at each level. The
following sub-packages isolate code related to objects of that type:
* image
* video
"""
