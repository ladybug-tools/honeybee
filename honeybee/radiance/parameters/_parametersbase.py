"""Radiance raytracing Parameters."""
import warnings
from collections import OrderedDict
import re


class RadianceParameters(object):
    """Radiance Parameters Base Class.

    Usage:

        class CustomRP(RadianceParameters):
            ab = RadianceNumber('ab', 'ambient bounces', default_value=3)
            ad = RadianceValue('ad', 'ambient divisions', default_value=None)

            def __init__(self):
                RadianceParameters.__init__(self)
                # add default parameters to class
                self.addParameterToDefaultParameters('ad', 'ad')
                self.addParameterToDefaultParameters('ab', 'ab')

        rp = CustomRP()
        rp.import_parameter_values_from_string('-dj 20 -fo')
        print(rp.to_rad_string())

        > -ab 15 -dj 20 -fo
    """

    # TODO: Automate the process of assigning any default key if available
    def __init__(self):
        """Init parameters."""
        # place holder for default parameter names
        # use radiance.datatype classes to create default parameters
        # self.
        self._default_parameters = {}

        # static parameters are the parameters which are set from a string.
        # static parameters are collected here
        self._additional_parameters = []

        setattr(self, 'is{}'.format(self.__class__.__name__), True)

    @property
    def isRadianceParameters(self):
        """Return True to indicate this object is a RadianceParameters."""
        return True

    @property
    def parameters(self):
        """Return list of current parameters."""
        return set(list(self._default_parameters.keys()) + self._additional_parameters)

    @property
    def default_parameters(self):
        """Return list of default parameters."""
        return set(self._default_parameters.keys())

    @property
    def additional_parameters(self):
        """Return list of default parameters."""
        return set(self._additional_parameters)

    @additional_parameters.setter
    def additional_parameters(self, values):
        self._additional_parameters = values

    @property
    def values(self):
        """Return list of current values."""
        return [getattr(self, key) for key in self.parameters]

    def try_to_unfreeze(self):
        """Try to unfreeze subclass to add a new attribute."""
        try:
            self.unfreeze()
        except AttributeError:
            raise Exception(
                "Sub-classes from RadianceParameters should be @frozen"
            )

    def add_default_parameter_name(self, alias, parameter):
        """Add a single parameter name to the list of default parameters.

        This method is only useful for base class developements and should not be
        used otherwise.

        Args:
            parameter:
                The radiance parameter name(e.g. ab, aa, f, c)
            alias:
                The alias name that will be used to create the attribute
                (e.g. ambient_bounces, ambient_accuracy, freeze, color)
        """
        assert hasattr(self.__class__, alias), \
            "Can't find '%s' in %s attributes." % (alias, self.__class__.__name__)
        self._default_parameters[alias] = parameter

    def remove_parameters(self):
        """Remove all current parameters."""
        for name in self.default_parameters:
            delattr(self.__class__, name)
        for name in self.additional_parameters:
            delattr(self, name)
        self._default_parameters = {}
        self._additional_parameters = []

    def remove_parameter(self, name):
        """Remove a single parameter by name."""
        if name in self.default_parameters:
            delattr(self.__class__, name)
            del self._default_parameters[name]
            print("Removed %s from default parameters." % str(name))
        elif name in self._default_parameters.values():
            for k, v in self._default_parameters.items():
                if v == name:
                    alias_name = k
                    break
            del self._default_parameters[alias_name]
            print("Removed %s from default parameters." % str(alias_name))
        elif name in self.additional_parameters:
            delattr(self, name)
            self._additional_parameters.remove(name)
            print("Removed %s from additional parameters." % str(name))
        else:
            warnings.warn("Couldn't find %s in parameters!" % str(name))

    def add_additional_parameter_by_name_and_value(self, name, value=""):
        """Add a static parameter by name and value.

        To add default parameters with types use CustomRadianceParameters.

        Args:
            name: A string to set name of parameter (e.g ab, i, o).
            value: A string to set thr value of paramter (e.g. 2, "2", "f")
            overwrite: Set to True if you want to overwrite current parameter
                value. If the parameter is default you should use
                RadianceParameters.parameterName = value to set the value
                (e.g. rp.ab = 5)
        """
        # clean name
        try:
            name = name.replace("-", "").strip()
        except TypeError:
            raise ValueError("Invalid name {}. Name should be a string.".format(name))

        # check if the name is in default values change the name to the alias
        if name in self._default_parameters.values():
            for k, v in self._default_parameters.items():
                if v == name:
                    alias_name = k
                    break
            if name != alias_name:
                raise ValueError(
                    "'{0}' is already set as an attribute by the name of {1}. "
                    "Use 'self.{1}' to change the value".format(name, alias_name)
                )

        if name in self.parameters:
            raise Exception(
                "'{0}' is already set as a parameter."
                " Use 'self.{0}' to change the value".format(
                    name)
            )

        try:
            self.try_to_unfreeze()
            setattr(self, name, str(value))
            self._additional_parameters.append(name)
        except TypeError:
            raise ValueError("Value should be a string or convertable to a string.")
        else:
            self.freeze()

    def import_parameter_values_from_string(self, parameters_string):
        """Import Radiance parameters from string.

        This will update the value for the parameter if the parameter already exist.

        Args:
            parameters_string: A standard radiance parameter string
                (e.g. -ab 5 -aa 0.05 -ar 128)
        """
        params = self._parse_rad_parameters(parameters_string)

        for key, value in params.items():
            try:
                self.add_additional_parameter_by_name_and_value(key, value)
            except ValueError:
                # parameter already exists under an alias name
                # find alias name and update the value
                for k, v in self._default_parameters.items():
                    if v == key:
                        alias_name = k
                        break
                setattr(self, alias_name, value)
                print("Updated value for %s to %s" % (alias_name, value))
            except Exception:
                # parameter already exists. just update the value
                setattr(self, key, value)
                print("Updated value for %s to %s" % (key, value))

    def radiance_default_values(self):
        """Use this method to remove all values assigned by Honeybee."""
        for name in self.default_parameters:
            setattr(self, name, None)
        for name in self.additional_parameters:
            setattr(self, name, None)

    def _parse_rad_parameters(self, parameters_string):
        """Parse radiance parameters.

        Args:
            parameters_string: e.g. "-ab 6 -ad 128"
        Returns:
            A dictionary of parameters and values.
        """
        # I'm pretty sure there is a regX method to do this in one line
        # but for now this should also do it

        rad_par = OrderedDict()

        if parameters_string is None:
            return rad_par

        # use re to find the start and end index for each parameter in parameter string
        indices = [(m.start(0), m.end(0)) for m in re.finditer(r'-[a-zA-Z]+',
                                                               parameters_string)]

        indices = [item for sublist in indices for item in sublist]

        indices.append(len(parameters_string))

        for i in range(0, len(indices) - 2, 2):
            key_start = indices[i] + 1
            key_end = indices[i + 1]
            key = parameters_string[key_start:key_end]

            value_start = key_end
            value_end = indices[i + 2]
            value = parameters_string[value_start:value_end]

            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    # case for parameters with no input values -u, -i
                    if key.strip() == "":
                        continue
                    elif value.strip() == "":
                        value = True

            rad_par[key.strip()] = value

        return rad_par

    def to_rad_string(self):
        """Get parameters as a radiance definition."""
        _default_parameters = [
            getattr(self, key).to_rad_string()
            for key in sorted(self.default_parameters)
            if getattr(self, key) is not None and
            getattr(self, key).to_rad_string() != ""
        ]

        _additional_parameters = [
            "-%s %s" % (key, getattr(self, key))
            if str(getattr(self, key)).strip() != ""
            else "-%s" % key
            for key in sorted(self.additional_parameters)
        ]

        return " ".join(_default_parameters + _additional_parameters)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Return radiance string."""
        return self.to_rad_string()
