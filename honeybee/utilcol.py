"""A collection of useful utilities for Honeybee"""
import uuid
import re


def randomName(shorten=True):
    """Generate a random name as a string using uuid.

    Args:
        shorten: If True the name will be the first to segment of uuid.
    """
    if shorten:
        return '-'.join(str(uuid.uuid4()).split('-')[:2])
    else:
        return str(uuid.uuid4())


# TODO(-): Not sure what should happen with non-ascii stuff. for now they are not valid.
def checkName(name):
    """Check if a name is a valid honeybee name.

    A valid name can only have alphabet, digits, - and _.
    """
    if re.match("^[.A-Za-z0-9_-]*$", name):
        return True
    else:
        raise ValueError(
            'Invalid input name: ({}).'
            ' Name can only contain letters, numbers,'
            ' dots, underscores and dashes.'.format(name)
        )


if __name__ == '__main__':
    checkName('should_be_fine')
#     checkName('also-fine')
    checkName('this.is.also.fine.1234')
#     checkName('not good')
