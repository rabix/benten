#  Copyright (c) 2019-2020 Seven Bridges. See LICENSE

__version__ = "2020.12.18"

import sys
import platform

binary_package_name = "benten_%s_%s_%s" % (__version__, sys.platform, platform.machine())
