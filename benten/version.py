#  Copyright (c) 2019-2020 Seven Bridges. See LICENSE

__version__ = "2020.12.21"

import sys
import platform

arch_dict = {"x86_64": "x64",
             "AMD64": "x64"}

binary_package_name = "benten_%s_%s_%s" % (__version__, sys.platform, arch_dict[platform.machine()])
