"""Material utility."""
import material.bsdf
import material.glass
import material.glow
import material.light
import material.metal
import material.mirror
import material.plastic
import material.spotlight
import primitive
import radparser

material_mapper = {
    'BSDF': material.bsdf,
    'glass': material.glass,
    'glow': material.glow,
    'light': material.light,
    'metal': material.metal,
    'mirror': material.mirror,
    'plastic': material.plastic,
    'spotlight': material.spotlight
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
