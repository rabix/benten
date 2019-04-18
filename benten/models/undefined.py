"""This typically happens as we type and create transient un-parsable YAML.
We can also get here when we load malformed YAML"""
from .base import Base


class Undefined(Base):
    pass
