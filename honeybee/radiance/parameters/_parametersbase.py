"""Radiance raytracing Parameters."""
import warnings
from collections import OrderedDict


class RadianceParameters(object):
    """Radiance Parameters Base Class.

    Usage:

        class CustomRP(RadianceParameters):
            ab = RadianceNumber('ab', 'am fddf', defaultValue=15)
            ad = RadianceValue('ad', 'fsfdsfds', defaultValue=None)

            def __init__(self):
                RadianceParameters.__init__(self)
                # add default parameters to class
                self.addParameterToDefaultParameters('ad', 'ad')
                self.addParameterToDefaultParameters('ab', 'ab')

        rp = CustomRP()
        rp.importParameterValuesFromString('-dj 20 -fo')
        print rp.toRadString()

        > -ab 15 -dj 20 -fo
    """

    # TODO: Automate the process of assigning any default key if available
    def __init__(self):
        """Init parameters."""
        # place holder for default parameter names
        # use radiance.datatype classes to create default parameters
        # self.
        self._defaultParameters = {}

        # static parameters are the parameters which are set from a string.
        # static parameters are collected here
        self._additionalParameters = []

        setattr(self, 'is{}'.format(self.__class__.__name__), True)

    @property
    def isRadianceParameters(self):
        """Return True to indicate this object is a RadianceParameters."""
        return True

    @property
    def parameters(self):
        """Return list of current parameters."""
        return set(self._defaultParameters.keys() + self._additionalParameters)

    @property
    def defaultParameters(self):
        """Return list of default parameters."""
        return set(self._defaultParameters.keys())

    @property
    def additionalParameters(self):
        """Return list of default parameters."""
        return set(self._additionalParameters)

    @additionalParameters.setter
    def additionalParameters(self, values):
        self._additionalParameters = values

    @property
    def values(self):
        """Return list of current values."""
        return [getattr(self, key) for key in self.parameters]

    def tryToUnfreeze(self):
        """Try to unfreeze subclass to add a new attribute."""
        try:
            self.unfreeze()
        except AttributeError:
            raise Exception(
                "Sub-classes from RadianceParameters should be @frozen"
            )

    def addDefaultParameterName(self, alias, parameter):
        """Add a single parameter name to the list of default parameters.

        This method is only useful for base class developements and should not be
        used otherwise.

        Args:
            parameter:
                The radiance parameter name(e.g. ab, aa, f, c)
            alias:
                The alias name that will be used to create the attribute
                (e.g. ambientBounces, ambientAccuracy, freeze, color)
        """
        assert hasattr(self.__class__, alias), \
            "Can't find '%s' in %s attributes." % (alias, self.__class__.__name__)
        self._defaultParameters[alias] = parameter

    def removeParameters(self):
        """Remove all t"
        "he current parameters."""
        for name in self.defaultParameters:
            delattr(self.__class__, name)
        for name in self.additionalParameters:
            delattr(self, name)
        self._defaultParameters = {}
        self._additionalParameters = []

    def removeParameter(self, name):
        """Remove a single parameter by name."""
        if name in self.defaultParameters:
            delattr(self.__class__, name)
            del self._defaultParameters[name]
            print "Removed %s from default parameters." % str(name)
        elif name in self._defaultParameters.values():
            _i = self._defaultParameters.values().index(name)
            aliasName = self._defaultParameters.keys()[_i]
            del self._defaultParameters[aliasName]
            print "Removed %s from default parameters." % str(aliasName)
        elif name in self.additionalParameters:
            delattr(self, name)
            self._additionalParameters.remove(name)
            print "Removed %s from additional parameters." % str(name)
        else:
            warnings.warn("Couldn't find %s in parameters!" % str(name))

    def addAdditionalParameterByNameAndValue(self, name, value=""):
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
        if name in self._defaultParameters.values():
            i = self._defaultParameters.values().index(name)
            aliasName = self._defaultParameters.keys()[i]
            if name != aliasName:
                raise ValueError(
                    "'{0}' is already set as an attribute by the name of {1}. "
                    "Use 'self.{1}' to change the value".format(name, aliasName)
                )

        if name in self.parameters:
            raise Exception(
                "'{0}' is already set as a parameter."
                " Use 'self.{0}' to change the value".format(
                    name)
            )

        try:
            self.tryToUnfreeze()
            setattr(self, name, str(value))
            self._additionalParameters.append(name)
        except TypeError:
            raise ValueError("Value should be a string or convertable to a string.")
        else:
            self.freeze()

    def importParameterValuesFromString(self, parametersString):
        """Import Radiance parameters from string.

        This will update the value for the parameter if the parameter already exist.

        Args:
            parametersString: A standard radiance parameter string
                (e.g. -ab 5 -aa 0.05 -ar 128)
        """
        params = self._parseRadParameters(parametersString)

        for key, value in params.items():
            try:
                self.addAdditionalParameterByNameAndValue(key, value)
            except ValueError:
                # paramter already exists under an alias name
                # find alias name and update the value
                _i = self._defaultParameters.values().index(key)
                aliasName = self._defaultParameters.keys()[_i]
                setattr(self, aliasName, value)
                print "Updated value for %s to %s" % (aliasName, value)
            except Exception:
                # paramter already exists. just update the value
                setattr(self, key, value)
                print "Updated value for %s to %s" % (key, value)

    # TODO: Enhance the parser using regX
    def _parseRadParameters(self, parametersString):
        """Parse radiance parameters.

        Args:
            parametersString: e.g. "-ab 6 -ad 128"
        Returns:
            A dictionary of parameters and values.
        """
        # I'm pretty sure there is a regX method to do this in one line
        # but for now this should also do it

        radPar = OrderedDict()

        if parametersString is None:
            return radPar

        # split input string: each part will look like key value (eg ad 1)
        parList = parametersString.split("-")

        for p in parList:
            key, sep, value = p.partition(" ")

            # convert the value to number
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
                        value = ""
                    else:
                        # case for tuples
                        try:
                            value = value.strip().split(" ")
                        except Exception:
                            value = ""

            radPar[key.strip()] = value

        return radPar

    def toRadString(self):
        """Get parameters as a radiance definition."""
        _defaultParameters = [
            getattr(self, key).toRadString()
            for key in self.defaultParameters
            if getattr(self, key).toRadString() != ""
        ]

        _additionalParameters = [
            "-%s %s" % (key, getattr(self, key))
            if str(getattr(self, key)).strip() != ""
            else "-%s" % key
            for key in self.additionalParameters
        ]

        return " ".join(_defaultParameters + _additionalParameters)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Return radiance string."""
        return self.toRadString()
