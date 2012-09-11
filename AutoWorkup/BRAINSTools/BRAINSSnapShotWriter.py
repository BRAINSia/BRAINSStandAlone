#! /usr/bin/env python
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""

Program:       PINC/nipype/Writers/BRAINSSnapShotWriter.py
Date:          Thu Jan  5 17:29:38 2012
Author:        David Welch, dmwelch@NOSPAM.uiowa.edu
Purpose:       Wrap BRAINSSnapShotWriter.sh to interact with Nipype

Requirements:  see BRAINSSnapShotWriter --help

"""
import os
from nipype.interfaces.base import (File, TraitedSpec, Interface, isdefined,
                                    CommandLineInputSpec, CommandLine,
                                    traits, InputMultiPath, OutputMultiPath)
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSSnapShotWriterInputSpec(CommandLineInputSpec):
    inputVolumes = InputMultiPath(File(exists = True),
                                  sep = ', ',
                                  argstr='%s',
                                  desc = 'Input image volume list to be extracted as 2D image. \
                                  Multiple input is possible. At least one input is required.')
    inputBinaryVolumes = InputMultiPath(File(exists = True),
                                        sep = ', ',
                                        argstr='%s',
                                        desc = 'Input mask (binary) volume list to be extracted \
                                        as 2D image. Multiple input is possible.' )
    # inputPlaneDirection = traits.Either(traits.List(traits.Int(),
    #                                                 minlen=1),
    #                                     traits.List(traits.Enum('saggital', 'coronal', 'axial'),
    #                                                 minlen=1),
    inputPlaneDirection = traits.List(traits.Int(),
                                      argstr='%s',
                                      mandatory=True,
                                      default=[0,1,2],
                                      usedefault=True,
                                      desc = 'List of plane(s) to display. Values are a vector of \
                                      integers OR strings.  0=saggital, 1=coronal, and 2=axial \
                                      plane.')
    inputSliceToExtractInPhysicalPoint = traits.List(traits.Float(),
                                                     requires=['inputPlaneDirection'],
                                                     desc = '2D slice number of input images. \
                                                     For autoWorkUp output with AC-PC aligned, \
                                                     [0.0, 0.0, 0.0] will be the center.' )
    inputSliceToExtractInIndex = traits.List(traits.Int(),
                                             requires=['inputPlaneDirection'],
                                             desc = '2D slice number of input images. For size of \
                                             256*256*256 image, 128 is usually used.')
    inputSliceToExtractInPercent = traits.List(traits.Range(low=0.0, high=1.0),
                                               requires=['inputPlaneDirection'],
                                               desc = '2D slice number of input images. Percentage \
                                               input from [0.0 - 1.0] (ex. [0.50, 0.50, 0.50]')
    outputFilename = traits.Str(argstr='--outputFilename %s', required=True, desc='')

class BRAINSSnapShotWriterOutputSpec(TraitedSpec):
    outputFilename = File(desc = '2D file name of input images. Required.')

class BRAINSSnapShotWriter(CommandLine):
    """
    Example
    -------

    >>> import BRAINSSnapShotWriter
    >>> bssw = BRAINSSnapShotWriter.BRAINSSnapShotWriter()
    >>> bssw.inputs.inputVolumes = ['file1.nii.gz', 'file2.nii.gz', 'file3.nii.gz']
    >>> bssw.inputs.inputBinaryVolumes = ['mask.nii.gz']
    >>> bssw.inputs.inputSliceToExtractInPercent = [0.3, 0.3, 0.6]
    >>> bssw.inputs.inputPlaneDirection = [2, 1, 3]
    >>> bssw.inputs.outputFilename = 'result'
    >>> print bssw.cmdline
    BRAINSSnapShotWriter --inputBinaryVolumes mask.nii.gz --inputPlaneDirection 2, 1, 3 --inputSliceToExtractInPercent 0.3, 0.3, 0.6 --inputVolumes file1.nii.gz, file2.nii.gz, file3.nii.gz --outputFilename result

    """
    _cmd = 'BRAINSSnapShotWriter'
    input_spec = BRAINSSnapShotWriterInputSpec
    output_spec = BRAINSSnapShotWriterOutputSpec

    def _formatSliceExtent(self):
        retval = []
        values = []
        if isdefined(self.inputs.inputSliceToExtractInPercent):
            retval.append('--inputSliceToExtractInPercent')
            for jj in range(self.numberOfSnapShots):
                values.append('%g' % self.inputs.inputSliceToExtractInPercent[jj])
        elif isdefined(self.inputs.inputSliceToExtractInIndex):
            retval.append('--inputSliceToExtractInIndex')
            for jj in range(self.numberOfSnapShots):
                values.append('%d' % self.inputs.inputSliceToExtractInIndex[jj])
        elif isdefined(self.inputs.inputSliceToExtractInPhysicalPoint):
            retval.append('--inputSliceToExtractInPhysicalPoint')
            for jj in range(self.numberOfSnapShots):
                values.append('%g' % self.inputs.inputSliceToExtractInPhysicalPoint[jj])
        retval.append(', '.join(values))
        return ' '.join(retval)

    def _format_arg(self, opt, spec, val):
        if not isdefined(self.inputs.inputVolumes) or \
            not isdefined(self.inputs.inputBinaryVolumes):
            raise Exception('Must define at least one input file')
        if opt == 'inputPlaneDirection':
            self.numberOfSnapShots = len(self.inputs.inputPlaneDirection)
            retval = ['--inputPlaneDirection']
            values = []
            for ii in range(self.numberOfSnapShots):
                values.append('%d' % self.inputs.inputPlaneDirection[ii])
            retval.append(', '.join(values))
            retval.append(self._formatSliceExtent())
            return " ".join(retval)
        elif opt == 'inputBinaryVolumes':
            retval = ['--inputBinaryVolumes']
            for ii in range(len(self.inputs.inputBinaryVolumes)):
                retval.append('%s,' % self.inputs.inputBinaryVolumes[ii])
            return " ".join(retval)[:-1]
        elif opt == 'inputVolumes':
            retval = ['--inputVolumes']
            for ii in range(len(self.inputs.inputVolumes)):
                retval.append('%s,' % self.inputs.inputVolumes[ii])
            return " ".join(retval)[:-1]
        return super(BRAINSSnapShotWriter, self)._format_arg(opt, spec, val)

    def _list_outputs(self):
        """
        The BRAINSSnapShot script
        """
        from os.path import abspath
        outputs = self.output_spec().get()
        outputs['outputFilename'] = abspath( self.inputs.outputFilename )
        return outputs

if __name__ == '__main__':
    import doctest
    doctest.testmod()

