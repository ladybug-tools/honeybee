"""Material utility."""
import honeybee_plus.radiance.material.bsdf
import honeybee_plus.radiance.material.glass
import honeybee_plus.radiance.material.glow
import honeybee_plus.radiance.material.light
import honeybee_plus.radiance.material.metal
import honeybee_plus.radiance.material.mirror
import honeybee_plus.radiance.material.plastic
import honeybee_plus.radiance.material.spotlight
import honeybee_plus.radiance.primitive as primitive
import honeybee_plus.radiance.radparser as radparser

material_mapper = {
    'BSDF': honeybee_plus.radiance.material.bsdf,
    'glass': honeybee_plus.radiance.material.glass,
    'glow': honeybee_plus.radiance.material.glow,
    'light': honeybee_plus.radiance.material.light,
    'metal': honeybee_plus.radiance.material.metal,
    'mirror': honeybee_plus.radiance.material.mirror,
    'plastic': honeybee_plus.radiance.material.plastic,
    'spotlight': honeybee_plus.radiance.material.spotlight
}


def primitive_from_json(prm_json):
    """
    Args:
        prm_json: A radiance modifier as a dictionary.

    Returns:
        A list of Honeybee Radiance primitives. If input includes polygons and
        materials, materials will be added to polygons as modifiers. This method
        will return all the polygons and only the materials that are not used.
    """
    # parse input json
    if not prm_json or prm_json == 'void':
        return primitive.Void()

    type = prm_json['type']

    if type in primitive.Primitive.MATERIALTYPES:
        return material_from_json(prm_json)
    else:
        raise NotImplementedError(
            'Pasring for {} primitives is not implemented!'.format(type)
        )


def material_from_json(mat_json):
    """Create Honeybee Radiance material from string.

    Args:
        mat_json: A radiance modifier string. The input can be a multi-line string.

    Returns:
        A list of Honeybee Radiance materials.
    """
    # parse input json
    if not mat_json or mat_json == 'void':
        return primitive.Void()

    type = mat_json['type']

    assert type in primitive.Primitive.MATERIALTYPES, \
        '{} is not a Radiance material:\n{}'.format(
            type, '\n'.join(primitive.Primitive.MATERIALTYPES)
        )

    # create a Radiance material based on the input
    try:
        matcls = getattr(material_mapper[type], type.capitalize())
        return matcls.from_json(mat_json)
    except AttributeError:
        # BSDF
        matcls = getattr(material_mapper[type], type)
        return matcls.from_json(mat_json)


def primitive_from_string(prm_string):
    """Create Honeybee Radiance primitives from string.

    Args:
        prim_string: A radiance modifier string. The input can be a multi-line string.

    Returns:
        A list of Honeybee Radiance primitives. If input includes polygons and
        materials, materials will be added to polygons as modifiers. This method
        will return all the polygons and only the materials that are not used.
    """
    # parse input json
    if not prm_string or prm_string == 'void':
        return primitive.Void()

    # run the initial parsing
    materials = radparser.parse_from_string(prm_string)
    type = materials[-1].split()[1]
    if type in primitive.Primitive.MATERIALTYPES:
        return material_from_string(prm_string)
    else:
        raise NotImplementedError(
            'Pasring for {} primitives is not implemented!'.format(type)
        )


def material_from_string(mat_string):
    """Create Honeybee Radiance material from string.

    Args:
        mat_string: A radiance modifier string. The input can be a multi-line string.

    Returns:
        A list of Honeybee Radiance materials.
    """
    # parse input json
    if not mat_string or mat_string == 'void':
        return primitive.Void()

    # run the initial parsing
    materials = radparser.parse_from_string(mat_string)
    type = materials[-1].split()[1]

    assert type in primitive.Primitive.MATERIALTYPES, \
        '{} is not a Radiance material:\n{}'.format(
            type, '\n'.join(primitive.Primitive.MATERIALTYPES)
        )
    # create a Radiance material based on the input
    try:
        matcls = getattr(material_mapper[type], type.capitalize())
        return matcls.from_string(mat_string)
    except AttributeError:
        # BSDF
        matcls = getattr(material_mapper[type], type)
        return matcls.from_string(mat_string)
