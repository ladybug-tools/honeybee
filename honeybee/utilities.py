"""Useful utilities for Honeybee"""
import uuid


def randomName(shorten=True):
    """Generate a random name as a string using uuid.

    Args:
        shorten: If True the name will be the first to segment of uuid.
    """
    if shorten:
        return '-'.join(str(uuid.uuid4()).split('-')[:2])
    else:
        return str(uuid.uuid4())
