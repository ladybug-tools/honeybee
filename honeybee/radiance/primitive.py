"""Base class for Radiance Primitives.

Unless you are a developer you most likely want to use one of the subclasses of
Primitive instead of using this class directly. Look under honeybee.radiance.material
and honeybee.radiance.geometry

http://radsite.lbl.gov/radiance/refer/ray.html
"""
from ..utilcol import check_name
from .radparser import parse_from_string
try:
    from .factory import primitive_from_string
except ImportError:
    # circular import
    pass
try:
    from .factory import primitive_from_json
except ImportError:
    # circular import
    pass


class Void(object):
    """Void modifier."""

    @property
    def name(self):
        return 'void'

    @property
    def can_be_modifier(self):
        return True

    def to_rad_string(self):
        """Return full radiance definition."""
        return 'void'

    def to_json(self):
        """Return void."""
        return self.to_rad_string()

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.to_rad_string()

    def __repr__(self):
        return self.to_rad_string()


class Primitive(object):
    """Base class for Radiance Primitives.

    Attributes:
        name: Primitive name as a string. Do not use white space and special character.
        type: One of Radiance standard Material types (e.g. glass, plastic).
        modifier: Modifier. It can be material, mixture, texture or pattern. Honeybee
            currently only supports materials. For other types use Generic primitive
            class (Default: "void").
    """

    # list of Radiance material types
    MATERIALTYPES = \
        set(('plastic', 'glass', 'trans', 'metal', 'mirror', 'illum',
             'mixedfunc', 'dielectric', 'transdata', 'light', 'glow', 'BSDF',
             'void', 'spotlight', 'prism1', 'prism2', 'mist', 'plastic2',
             'metal2', 'trans2', 'ashik2', 'dielectric', 'interface',
             'plasfunc', 'metfunc', 'transfunc', 'BRTDfunc',
             'plasdata', 'metdata', 'transdata', 'antimatter'))

    TEXTURETYPES = set(('texfunc', 'texdata'))

    # list of Radiance geometry types
    GEOMETRYTYPES = set(('source', 'sphere', 'bubble', 'polygon', 'cone', 'cup',
                         'cylinder', 'tube', 'ring', 'instance', 'mesh'))

    PATTERNTYPES = set(('colorfunc', 'brightfunc', 'colordata', 'brightdata',
                        'colorpict', 'colortext', 'brighttext'))

    MIXTURETYPES = set(('mixfunc', 'mixdata', 'mixpict', 'mixtext'))

    TYPES = set().union(MATERIALTYPES, TEXTURETYPES, GEOMETRYTYPES, PATTERNTYPES,
                        MIXTURETYPES)

    # Materials, mixtures, textures or patterns
    MODIFIERTYPES = set().union(MATERIALTYPES, MIXTURETYPES, TEXTURETYPES, PATTERNTYPES)

    def __init__(self, name, type, modifier=None):
        """Create material base."""
        self.name = name
        self.type = type
        self.modifier = modifier

    @property
    def isPrimitive(self):
        """Indicate that this object is a Radiance primitive."""
        return True

    @property
    def isGeometry(self):
        """Indicate if this object is a Radiance geometry."""
        return False

    @property
    def isRadianceMaterial(self):
        """Indicate if this object is a Radiance material."""
        return False

    @property
    def can_be_modifier(self):
        """Indicate if this object can be a modifier.

        Materials, mixtures, textures or patterns can be modifiers.
        """
        if self.type in self.MODIFIERTYPES:
            return True

        return False

    @property
    def name(self):
        """Get/set material name."""
        return self._name

    @name.setter
    def name(self, name):
        if self.isRadianceMaterial:
            assert name not in self.MATERIALTYPES, \
                '%s is a radiance primitive type and' \
                ' should not be used as a material name.' % name

        if self.isGeometry:
            assert name not in self.GEOMETRYTYPES, \
                '%s is a radiance geometry type and' \
                ' should not be used as a geometry name.' % name

        self._name = name.rstrip()
        check_name(self._name)

    @property
    def modifier(self):
        """Get/set material modifier."""
        return self._modifier

    @modifier.setter
    def modifier(self, modifier):
        if not modifier or modifier == 'void':
            self._modifier = Void()
        else:
            assert modifier.can_be_modifier, \
                'A {} cannot be a modifier. Modifiers can be Materials, mixtures, ' \
                'textures or patterns'.format(type(modifier))
            self._modifier = modifier

    @property
    def type(self):
        """Get/set material type."""
        return self._type

    @type.setter
    def type(self, type):
        assert type in self.TYPES, \
            "%s is not a supported material type." % type + \
            "Try one of these materials:\n%s" % str(self.TYPES)

        self._type = type

    @staticmethod
    def _get_string_type(input_string):
        """This is a helper function for from_string classmethod.

        Args:
            input_string: Radiance input string
        Returns:
            primitive type.
        """
        input_objects = parse_from_string(input_string)

        if not input_objects:
            raise ValueError(
                '{} includes no radiance materials.'.format(input_string)
            )

        bm = input_objects[-1]
        bm_data = bm.split()
        bm_type = bm_data[1]
        return bm_type

    @staticmethod
    def _analyze_string_input(desired_type, input_string, modifier):
        """This is a helper function for from_string classmethod.

        Args:
            desired_type: Desired type of base modifier as a string (e.g. plastic).
            input_string: Radiance input string
            modifier: A radiance modifier for base input string.
        Returns:
            modifier, name, modifier data as a list
        """
        input_objects = parse_from_string(input_string)

        if not input_objects:
            raise ValueError(
                '{} includes no radiance materials.'.format(input_string)
            )

        bm = input_objects[-1]
        bm_data = bm.split()
        bm_modifier = bm_data[0]
        bm_type = bm_data[1]
        bm_name = bm_data[2]

        if desired_type:
            # custom materials won't have desired_type
            assert bm_type == desired_type, \
                '{} is a {} not a {}.'.format(bm, bm_type, desired_type)

        if len(input_objects) == 1:
            # There is only one material ensure that modifier is void

            if bm_modifier != 'void':
                assert modifier, \
                    '{} has a modifier: "{}" which is not provided.'.format(
                        bm_data[2], bm_modifier
                    )
                assert modifier.can_be_modifier, \
                    '{} cannot be a modifier!'.format(modifier)

                assert modifier.name == bm_modifier, \
                    'Illegal modifier. Expected {} got {}'.format(bm_modifier,
                                                                  modifier.name)
            else:
                modifier == bm_modifier

        if modifier != 'void' and len(input_objects) > 1:
            # create modifier if any
            modifier_materials = '\n'.join(input_objects[:-1])
            try:
                modifier = primitive_from_string(modifier_materials)
            except UnboundLocalError:
                # circular import
                from .factory import primitive_from_string
                modifier = primitive_from_string(modifier_materials)

        return modifier, bm_name, bm_data[3:]

    @staticmethod
    def _analyze_json_input(desired_type, input_json):
        """This is a helper function for from_json classmethod.

        Args:
            desired_type: Desired type of base modifier as a string (e.g. plastic).
            input_json: Radiance input as a dictionary.
        Returns:
            modifier as a Honeybee Radiance primitive.
        """
        if not input_json:
            raise ValueError('{} includes no radiance materials.'.format(input_json))

        bm_data = input_json
        bm_modifier = bm_data['modifier']
        bm_type = bm_data['type']

        if desired_type:
            # custom materials won't have desired_type
            assert bm_type == desired_type, \
                '{} is a {} not a {}.'.format(bm_data, bm_type, desired_type)

        if bm_modifier != 'void':
            # create modifier if any
            try:
                modifier = primitive_from_json(bm_modifier)
            except UnboundLocalError:
                # circular import
                from .factory import primitive_from_json
                modifier = primitive_from_json(bm_modifier)
        else:
            modifier = Void()

        return modifier

    def head_line(self, minimal=False):
        """Return first line of Material definition.

        If material has a modifier it returns the modifier definition as well.
        """
        if self.modifier.name == 'void':
            return "void %s %s\n" % (self.type, self.name)

        # include modifier material in definition
        modifier = self.modifier.to_rad_string(minimal)

        return "%s\n\n%s %s %s\n" % (modifier, self.modifier.name, self.type, self.name)

    def to_rad_string(self, minimal=False):
        """Return full radiance definition.

        Args:
            minimal: Set to True to get the definition in as single line.
        """
        raise NotImplementedError()

    def to_json(self):
        """Return material definition as a dictionary.

        Implement in subclasses.
        """
        raise NotImplementedError()

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __repr__(self):
        """Return material definition."""
        return self.to_rad_string()


class Generic(Primitive):
    """Custom Radiance material.

    Attributes:
        name: Primitive name as a string. Do not use white space and special character.
        type: One of Radiance standard Primitive types (e.g. glass, plastic, etc)
        values: A dictionary of primitive data. key is line number and item is the list
            of values {0: [], 1: [], 2: ['0.500', '0.500', '0.500', '0.000', '0.050']}
        modifier: Modifier. It can be material, mixture, texture or pattern. Honeybee
            currently only supports materials. For other types use Generic primitive
            class (Default: "void").
    """

    def __init__(self, name, type, values, modifier=None):
        """Create custom radiance material."""
        Primitive.__init__(self, name, type, modifier=modifier)
        self.values = values
        """ A dictionary of material data. key is line number and item is the list of
            values {0: [], 1: [], 2: ['0.500', '0.500', '0.500', '0.000', '0.050']}
        """

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, new_values):
        """Modify values for the current material.

        Args:
           new_values: New values as a dictionary. The keys should be between 0 and 2.

         Usage:
            # This line will assign 9 values to line 0 of the material
            material.values = {0: ["0.5", "0.5", "0.5",
                "/usr/local/lib/ray/oakfloor.pic", ".", "frac(U)",
                "frac(V)", "-s", "1.1667"]}
        """
        for line_count, value in new_values.iteritems():
            assert 0 <= line_count <= 2, ValueError(
                'Illegal input: {}. Key values must be between 0-2.'.format(line_count)
            )
            self._values[line_count] = value

    def to_rad_string(self, minimal=False):
        """Return full radiance definition."""
        output = [self.head_line(minimal)]

        for line_count in xrange(3):
            try:
                values = self.values[line_count]
            except BaseException:
                values = []  # line will be printed as 0
            else:
                count = [str(len(values))]
                line = " ".join(count + values).rstrip()
                output.append(line)

        return " ".join(output) if minimal else "\n".join(output)
