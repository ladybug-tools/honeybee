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
                # add dynamic keys to class
                self.dynamicKeys = ['ab', 'ad']

        rp = CustomRP()
        rp.importParameterValuesFromString('-dj 20 -fo')
        print rp.toRadString()

        > -ab 15 -dj 20 -fo
    """

    # TODO: Automate the process of assigning any dynamic key if available
    def __init__(self):
        """Init parameters."""
        # place holder for dynamic parameter names
        # use radiance.datatype classes to create dynamic parameters
        # self.
        self.__dynamicParameters = []

        # static parameters are the parameters which are set from a string.
        # static parameters are collected here
        self.__staticParameters = []

    @property
    def isRadianceParameters(self):
        """Return True to indicate this object is a RadianceParameters."""
        return True

    @property
    def keys(self):
        """Return list of current parameters."""
        return set(self.__dynamicParameters + self.__staticParameters)

    @property
    def dynamicKeys(self):
        """Return list of dynamic parameters."""
        return set(self.__dynamicParameters)

    @property
    def staticKeys(self):
        """Return list of dynamic parameters."""
        return set(self.__staticParameters)

    @staticKeys.setter
    def staticKeys(self, values):
        self.__staticParameters = values

    @property
    def values(self):
        """Return list of current values."""
        return [getattr(self, key) for key in self.keys]

    def appendParametersToDynamicKeys(self, values):
        """Append a list of  parameter names to list of dynamic keys.

        This method is only useful for base class developements and should not be
        used otherwise.
        """
        for v in values:
            self.appendParameterToDynamicKeys(v)

    def appendParameterToDynamicKeys(self, v):
        """Append a single parameter names to list of dynamic keys.

        This method is only useful for base class developements and should not be
        used otherwise.
        """
        assert hasattr(self.__class__, v), \
            "Can't find '%s' in %s attributes." % (v, self.__class__.__name__)
        self.__dynamicParameters.append(v)

    def removeParameters(self):
        """Remove all the current parameters."""
        for name in self.dynamicKeys:
            delattr(self.__class__, name)
        for name in self.staticKeys:
            delattr(self, name)
        self.__dynamicParameters = []
        self.__staticParameters = []

    def removeParameter(self, name):
        """Remove a single parameter by name."""
        if name in self.dynamicKeys:
            delattr(self.__class__, name)
            self.__dynamicParameters.remove(name)
            print "Removed %s from dynamic parameters." % str(name)
        elif name in self.staticKeys:
            delattr(self, name)
            self.__staticParameters.remove(name)
            print "Removed %s from static parameters." % str(name)
        else:
            warnings.warn("Couldn't find %s in parameters!" % str(name))

    def addParamterByNameAndValue(self, name, value=""):
        """Add a static parameter by name and value.

        To add dynamic parameters with types use CustomRadianceParameters.

        Args:
            name: A string to set name of parameter (e.g ab, i, o).
            value: A string to set thr value of paramter (e.g. 2, "2", "f")
            overwrite: Set to True if you want to overwrite current parameter
                value. If the parameter is dynamic you should use
                RadianceParameters.parameterName = value to set the value
                (e.g. rp.ab = 5)
        """
        # clean name
        try:
            name = name.replace("-", "").strip()
        except TypeError:
            raise ValueError("Invalid name {}. Name should be a string.".format(name))

        if name in self.keys:
            raise Exception(
                "'{0}' is already set as a parameter. Use 'self.{0}' to change the value".format(name)
            )

        try:
            setattr(self, name, str(value))
            self.__staticParameters.append(name)
        except TypeError:
            raise ValueError("Value should be a string or convertable to a string.")

    def importParameterValuesFromString(self, parametersString):
        """Import Radiance parameters from string.

        This will update the value for the parameter if the parameter already exist.

        Args:
            parametersString: A standard radiance parameter string (e.g. -ab 5 -aa 0.05 -ar 128)
        """
        __params = self.__parseRadParameters(parametersString)

        for key, value in __params.items():
            try:
                self.addParamterByNameAndValue(key, value)
            except Exception:
                # paramter already exist just update the value
                setattr(self, key, value)

    # TODO: Enhance the parser using regX
    def __parseRadParameters(self, parametersString):
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
            except:
                try:
                    value = float(value)
                except:
                    # case for parameters with no input values -u, -i
                    if key.strip() == "":
                        continue
                    value = ""

            radPar[key.strip()] = value

        return radPar

    def toRadString(self):
        """Get parameters as a radiance definition."""
        _dynamicParameters = [
            getattr(self, key).toRadString()
            for key in self.dynamicKeys
            if getattr(self, key).toRadString() != ""
        ]

        _staticParameters = [
            "-%s %s" % (key, getattr(self, key))
            if getattr(self, key).strip() != ""
            else "-%s" % key
            for key in self.staticKeys
        ]

        return " ".join(_dynamicParameters + _staticParameters)

    def __repr__(self):
        """Return radiance string."""
        return self.toRadString()
