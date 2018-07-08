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
        """Void."""
        return 'void'

    @property
    def can_be_modifier(self):
        """True."""
        return True

    @property
    def is_opaque(self):
        """False for a void."""
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
        type: One of Radiance standard Primitive types (e.g. glass, plastic, etc)
        modifier: Modifier. It can be primitive, mixture, texture or pattern.
            (Default: "void").
        values: A dictionary of primitive data. key is line number and item is the list
            of values {0: [], 1: [], 2: ['0.500', '0.500', '0.500', '0.000', '0.050']}
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
    # Materials that are not usually opaque. This will be used to set is_opaque property
    # is it's not provided by user and can be overwritten by setting the value for
    # is_opaque
    NONEOPAQUETYPES = set(('glass', 'trans', 'trans2', 'transdata', 'transfunc',
                           'dielectric', 'BSDF', 'mixfunc', 'BRTDfunc', 'mist',
                           'prism1', 'prism2'))

    def __init__(self, name, type, modifier=None, values=None, is_opaque=None):
        """Create primitive base."""
        self.name = name
        self.type = type
        self.modifier = modifier
        self.values = values or {0: [], 1: [], 2: []}
        self._is_opaque = is_opaque

    @classmethod
    def from_string(cls, primitive_string, modifier=None):
        """Create a Radiance primitive from a string.

        If the primitive has a modifier the modifier primitive should also be part of the
        string or should be provided using modifier argument.
        """
        primitive_type = cls._get_string_type(primitive_string)

        modifier, name, base_data = cls._analyze_string_input(
            None, primitive_string, modifier)

        count_1 = int(base_data[0])
        count_2 = int(base_data[count_1 + 1])
        count_3 = int(base_data[count_1 + count_2 + 2])

        l1 = [] if count_1 == 0 else base_data[1: count_1 + 1]
        l2 = [] if count_2 == 0 \
            else base_data[count_1 + 2: count_1 + count_2 + 2]
        l3 = [] if count_3 == 0 \
            else base_data[count_1 + count_2 + 3: count_1 + count_2 + count_3 + 3]

        values = {0: l1, 1: l2, 2: l3}
        if cls.__class__.__name__ == 'Primitive':
            return cls(name, primitive_type, modifier, values)
        else:
            # subclass - type will be assigned based on name
            return cls(name, modifier, values)

    @classmethod
    def from_json(cls, mat_json):
        """Make radiance primitive from json
        {
            "modifier": "", // primitive modifier (Default: "void")
            "type": "custom", // primitive type
            "base_type": "type", // primitive type
            "name": "", // primitive Name
            "values": {} // values
        }
        """
        modifier = cls._analyze_json_input(cls.__name__.lower(), mat_json)
        if cls.__class__.__name__ == 'Primitive':
            return cls(name=mat_json["name"],
                       type=mat_json["type"],
                       modifier=modifier,
                       values=mat_json["values"])
        else:
            # subclass - type will be assigned based on name
            return cls(name=mat_json["name"],
                       modifier=modifier,
                       values=mat_json["values"])

    @property
    def values(self):
        self._update_values()
        return self._values

    @values.setter
    def values(self, new_values):
        """Modify values for the current primitive.

        Args:
           new_values: New values as a dictionary. The keys should be between 0 and 2.

         Usage:
            # This line will assign 9 values to line 0 of the primitive
            primitive.values = {0: ["0.5", "0.5", "0.5",
                "/usr/local/lib/ray/oakfloor.pic", ".", "frac(U)",
                "frac(V)", "-s", "1.1667"]}
        """
        self._values = {}
        for line_count, value in new_values.iteritems():
            assert 0 <= line_count <= 2, ValueError(
                'Illegal input: {}. Key values must be between 0-2.'.format(line_count)
            )
            self._values[line_count] = value

    @property
    def isRadiancePrimitive(self):
        """Indicate that this object is a Radiance primitive."""
        return True

    @property
    def isRadianceGeometry(self):
        """Indicate if this object is a Radiance geometry."""
        return False

    @property
    def isRadianceTexture(self):
        """Indicate if this object is a Radiance geometry."""
        return False

    @property
    def isRadiancePattern(self):
        """Indicate if this object is a Radiance geometry."""
        return False

    @property
    def isRadianceMixture(self):
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
        """Get/set primitive name."""
        return self._name

    @name.setter
    def name(self, name):
        if self.isRadianceMaterial:
            assert name not in self.MATERIALTYPES, \
                '%s is a radiance primitive type and' \
                ' should not be used as a material name.' % name

        elif self.isRadianceGeometry:
            assert name not in self.GEOMETRYTYPES, \
                '%s is a radiance geometry type and' \
                ' should not be used as a geometry name.' % name

        self._name = name.rstrip()
        check_name(self._name)

    @property
    def modifier(self):
        """Get/set primitive modifier."""
        return self._modifier

    @modifier.setter
    def modifier(self, modifier):
        if not modifier or modifier == 'void':
            self._modifier = Void()
        else:
            if not hasattr(modifier, 'can_be_modifier'):
                raise TypeError('Invalid modifier: %s' % modifier)
            assert modifier.can_be_modifier, \
                'A {} cannot be a modifier. Modifiers can be Materials, mixtures, ' \
                'textures or patterns'.format(type(modifier))
            self._modifier = modifier

    @property
    def type(self):
        """Get/set primitive type."""
        return self._type

    @type.setter
    def type(self, type):
        _mapper = {'bsdf': 'BSDF', 'brtdfunc': 'BRTDfunc'}

        if type not in self.TYPES:
            # try base classes for subclasses
            for base in self.__class__.__mro__:
                if base.__name__.lower() in _mapper:
                    type = _mapper[base.__name__.lower()]
                    break
                if base.__name__.lower() in self.TYPES:
                    type = base.__name__.lower()
                    break

        assert type in self.TYPES, \
            "%s is not a supported primitive type." % type + \
            "Try one of these primitives:\n%s" % str(self.TYPES)

        self._type = type

    @property
    def is_opaque(self):
        """Indicate if the primitive is opaque.

        This property is used to separate opaque and non-opaque surfaces.
        """
        if self._is_opaque:
            return self._is_opaque
        elif self.type in self.NONEOPAQUETYPES:
            # none opaque material
            self._is_opaque = False
            return self._is_opaque
        else:
            # check modifier for surfaces
            return self.modifier.is_opaque

    @is_opaque.setter
    def is_opaque(self, is_opaque):
        self._is_opaque = bool(is_opaque)

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
                '{} includes no radiance primitives.'.format(input_string)
            )

        bm = input_objects[-1]
        bm_data = bm.split()
        bm_type = bm_data[0]
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
                '{} includes no radiance primitives.'.format(input_string)
            )

        bm = input_objects[-1]
        bm_data = bm.split()
        bm_modifier = bm_data[0]
        bm_type = bm_data[1]
        bm_name = bm_data[2]

        if desired_type:
            # custom primitives won't have desired_type
            assert bm_type == desired_type, \
                '{} is a {} not a {}.'.format(bm, bm_type, desired_type)

        if len(input_objects) == 1:
            # There is only one primitive ensure that modifier is void

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
            modifier_primitives = '\n'.join(input_objects[:-1])
            try:
                modifier = primitive_from_string(modifier_primitives)
            except UnboundLocalError:
                # circular import
                from .factory import primitive_from_string
                modifier = primitive_from_string(modifier_primitives)

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
            raise ValueError('{} includes no radiance primitives.'.format(input_json))

        bm_data = input_json
        bm_modifier = bm_data['modifier']
        bm_type = bm_data['type']

        if desired_type:
            # custom primitives won't have desired_type
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

    def _update_values(self):
        """update value dictionaries.

        _update_values must be implemented under subclasses.
        """
        pass

    def head_line(self, minimal=False, include_modifier=True):
        """Return first line of primitive definition.

        If primitive has a modifier it returns the modifier definition as well.
        """
        if self.modifier.name == 'void':
            return "void %s %s\n" % (self.type, self.name)

        if include_modifier:
            # include modifier primitive in definition
            modifier = self.modifier.to_rad_string(minimal)
            return "%s\n%s %s %s\n" % (modifier, self.modifier.name, self.type,
                                       self.name)
        else:
            return "%s %s %s\n" % (self.modifier.name, self.type, self.name)

    # add string format for float values
    def to_rad_string(self, minimal=False, include_modifier=True):
        """Return full radiance definition."""
        output = [self.head_line(minimal, include_modifier).strip()]
        for line_count in xrange(3):
            try:
                values = (str(v) for v in self.values[line_count])
            except BaseException:
                values = []  # line will be printed as 0
            else:
                count = len(self.values[line_count])
                line = '%d %s' % (count, " ".join(values).rstrip())
                output.append(' '.join(line.split()))

        return " ".join(output) if minimal else "\n".join(output)

    def to_json(self):
        """Translate radiance primitive to json
        {
            "modifier": "", // primitive modifier (Default: "void")
            "type": "custom", // primitive type
            "base_type": "type", // primitive type
            "name": "", // primitive Name
            "values": {} // values
        }
        """
        return {
            "modifier": self.modifier.to_json(),
            "type": self.type,
            "name": self.name,
            "values": self.values
        }

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __repr__(self):
        """Return primitive definition."""
        return self.to_rad_string()
