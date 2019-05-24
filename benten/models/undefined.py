"""This typically happens as we type and create transient un-parsable YAML.
We can also get here when we load malformed YAML"""
#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .base import Base


class Undefined(Base):
    pass
