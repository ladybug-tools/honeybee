# !/usr/bin/env python
# -*- coding: utf-8 -*-

from _advancedparametersbase import AdvancedRadianceParameters


class RcollateParameters(AdvancedRadianceParameters):
    """Radiance parameters for rcollate.

    Note: As on Apr-10-2016, this class has been implemented to facilitate
    it's use for 3-Phase and 5-Phase method calculations. Not all the possible
    options of rcollate have been added at present.

    Read more:
    http://www.radiance-online.org/learning/documentation/manual-pages/
    pdfs/rcollate.pdf

    Attributes:
        removeHeader: [-h[io]] -hi turns input header off, -ho turns ouput
            header off. -h turns both off.
        warningsOff: [-w] turn off non fatal warnings.
        outputFormat: [-f[afdb[N]]. Specify an output format.
        transpose: [-t] Transpose the matrix.
        inputColumns: [-ic col] Size of the columns of the input matrix.
        outputColumns: [-oc col] Size of the columns of the output matrix.
        inputRows: [-ir row] Size of the rows of the input matrix.
        outputRows: [-or row] Size of the rows of output matrix.

        * For the full list of attributes try self.keys
        ** values between []'s indicate Radiance equivalent keys for advanced users

    Usage:

        #Rearrange an input 10x10 matrix to 20x5 matrix.
        rcolparam = RcollateParameters()

        rcolparam.inputColumns = 10
        rcolpara.inputRows = 10

        rcolparam.outputRows = 20
        rcolparam.outputColumns = 5

        #Check the values.
        print rcolparam.toRadString()
        > -ic 10 -ir 10 -oc 5 -or 20
    """

    def __init__(self,removeHeader=None,warningsOff=None,outputFormat=None,
                 transpose=None,inputColumns=None,outputColumns=None,
                 inputRows=None,outputRows=None):
        self.removeHeader = None
        """ removeHeader: [-h[io]] -hi turns input header off, -ho turns ouput
            header off. -h turns both off. """
        
        self.warningsOff =  None
        """warningsOff: [-w] turn off non fatal warnings."""
        
        self.outputFormat = None
        """outputFormat: [-f[afdb[N]]. Specify an output format."""
        
        self.transpose = None
        """transpose: [-t] Transpose the matrix."""
        
        self.inputColumns = None
        """inputColumns: [-ic col] Size of the columns of the input matrix."""
        
        self.outputColumns = None
        """outputColumns: [-oc col] Size of the columns of the output matrix."""
        
        self.inputRows = None
        """inputRows: [-ir row] Size of the rows of the input matrix."""
        
        self.outputRows = None
        """outputRows: [-or row] Size of the rows of output matrix."""

        self.addRadianceValue('h','removeHeader',acceptedInputs=[True,'i','o'],
                              defaultValue=removeHeader,isJoined=True)
        self.addRadianceBoolFlag('w','warningsOff',defaultValue=warningsOff)
        self.addRadianceBoolFlag('t','transpose',defaultValue=transpose)
        self.addRadianceNumber('ic','inputColumns',defaultValue=inputColumns,
                               numType=int)
        self.addRadianceNumber('oc', 'outputColumns', defaultValue=outputColumns,
                               numType=int)
        self.addRadianceNumber('ir', 'inputRows', defaultValue=inputRows,
                               numType=int)
        self.addRadianceNumber('or', 'outputRows', defaultValue=outputRows,
                               numType=int)