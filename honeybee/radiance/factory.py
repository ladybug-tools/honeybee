"""Material utility."""
import material.bsdf
import material.custom
import material.glass
import material.glow
import material.light
import material.metal
import material.mirror
import material.plastic
import primitive
import radparser

material_mapper = {
    'BSDF': material.bsdf,
    'glass': material.glass,
    'glow': material.glow,
    'light': material.light,
    'metal': material.metal,
    # 'mirror': material.mirror,
    'plastic': material.plastic
}


def modifier_from_json(mod_json):
    """
    Args:
        mod_json: A radiance modifier as a dictionary.

    Return:
        A Radiance modifier (currently Material).
    """
    pass
    # parse input json
    # if not mod_json:
    #     return Void()
    #
    # type = mod_json['type']
    # # create a Radiance material based on the input
    # if type in material_mapper:
    #     return material_mapper[type].from_json(mod_json)
    # else:
    #     # create a generic material
    #     return GenericMaterial.from_json(mod_json)


def primitive_from_string(prim_string):
    """Create Honeybee Radiance primitives from string.

    Args:
        prim_string: A radiance modifier string. The input can be a multi-line string.

    Returns:
        A list of Honeybee Radiance primitives. If input includes polygons and
        materials, materials will be added to polygons as modifiers. This method
        will return all the polygons and only the materials that are not used.
    """
    # parse input json
    if not prim_string or prim_string == 'void':
        return primitive.Void()

    # run the initial parsing
    materials = radparser.parse_from_string(prim_string)
    type = materials[-1].split()[1]
    if type in primitive.Primitive.MATERIALTYPES:
        return material_from_string(prim_string)
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
    except KeyError:
        # the class is not part of honeybee yet. Create a custom material
        return material.custom.Custom.from_string(mat_string)
