"""Recipe ids.

This file is reference for recipe ids. Every id must be unique to that recipe.

The first two digits identifies if the recipe is for point_in_time [10] or multiple
hours [20]. The follwing next digits identifies if recipe is grid-based [0] or
view-based [1]. The following 3 digits is a counter starting from 000.

"""
from __future__ import division

IDS = {
    'daylight_factor': 100000,
    'point_in_time': 100001,
    'cumulative_radiation': 100002,
    'vertical_sky_component': 100003,
    'solar_access': 200000,
    'direct_sun': 200001,
    'two_phase': 200002,
    'three_phase': 200003,
    'annual_radiation': 200004,
    'five_phase': 200005,
    'direct_reflection': 200006,
}

NAMES = {value: key for key, value in IDS.items()}

"""Combined recipes are recipes that combine direct sunlight and sky calculations.

These ids are used by honeybee.radiance.resultcollection.database.Database class to
add extra tables for results.
"""
COMBINEDRECIPEIDS = (200002, 200005)

"""Recipes with values for direct sunlight."""
DIRECTRECIPEIDS = (200001, 200002, 200005)

"""Recipes which the result should be saved as float and not integer."""
FLOATRECIPEIDS = (100000, 100003)

def get_id(name, recipe_type=0):
    """Get Honeybee ID from recipe name.

    Args:
        name: Recipe name (e.g. daylight_factor).
        recipe_type: 0 for grid-based and 1 for view-based recipes.

    Returns:
        A 6 digits number. The first two digits identifies if the recipe is for
        point_in_time [10] or multiple hours [20]. The follwing next digits identifies
        if recipe is grid-based [0] or view-based [1]. The following 3 digits is a
        counter starting from 000.
    """
    recipe_type = recipe_type or 0
    assert recipe_type in (0, 1), 'Recipe type can only be 0 or 1.'

    try:
        return IDS[name] + recipe_type * 1000
    except KeyError:
        raise KeyError('{} is not a valid input. Try one of the recipes below:\n{}'
                         .format(name, '\n'.join(IDS.keys())))


def get_name(recipe_id):
    """Get recipe name from ID."""
    try:
        return NAMES[recipe_id]
    except KeyError:
        raise KeyError(
            '{} is not a valid ID.\n{}'.format(
                recipe_id,
                '\n'.join('{}:{}'.format(k, v) for k, v in IDS.items())
            ))


def is_point_in_time(recipe_id):
    """Check if a recipe id is point in time."""
    return int(recipe_id / 100000) == 1


if __name__ == '__main__':
    print(is_point_in_time(200006))
    print(is_point_in_time(100002))
