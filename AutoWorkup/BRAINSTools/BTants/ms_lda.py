# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""The freesurfer module provides basic functions for interfacing with freesurfer tools.

   Change directory to provide relative paths for doctests
   >>> import os
   >>> filepath = os.path.dirname( os.path.realpath( __file__ ) )
   >>> datadir = os.path.realpath(os.path.join(filepath, '../../testing/data'))
   >>> os.chdir(datadir)

"""
__docformat__ = 'restructuredtext'

import os

from nipype.utils.filemanip import fname_presuffix, split_filename
from nipype.interfaces.freesurfer.base import FSCommand, FSTraitedSpec
from nipype.interfaces.base import (TraitedSpec, File, traits, InputMultiPath,
                                    OutputMultiPath, Directory, isdefined)

class MS_LDAInputSpec(FSTraitedSpec):
    lda_labels = traits.List(traits.Int(), argstr='-lda %s', mandatory=True, minlen=2, maxlen=2, sep=' ', position=1,
                             desc='pair of class labels to optimize')
    weight_file = traits.File(exists=False, argstr='-weight %s', mandatory=True, position=2, desc='filename for the LDA weights (input or output)')
    output_synth = traits.File(exists=False, argstr='-synth %s', mandatory=True, position=3, desc='filename for the synthesized output volume')
    label_file = traits.File(exists=True, argstr='-label %s', mandatory=True,    position=4, desc='filename of the label volume')
    mask_file = traits.File(exists=True, argstr='-mask %s', position=5, desc='filename of the brain mask volume')
    shift = traits.Int(argstr='-shift %d', position=6, desc='shift all values equal to the given value to zero')
    conform = traits.Bool(argstr='-conform', position=7, desc='Conform the input volumes (brain mask typically already conformed)')
    use_weights = traits.Bool(argstr='-W', position=8, desc='Use the weights from a previously generated weight file')
    images = InputMultiPath(File(exists=True), argstr='%s', mandatory=True, copyfile=False, desc='list of input FLASH images' )

class MS_LDAOutputSpec(TraitedSpec):
    weight_file = File(exists=True, desc='')
    output_synth = File(exists=True, desc='')

class MS_LDA(FSCommand):
    """Perform LDA reduction on the intensity space of an arbitrary # of FLASH images

    Examples
    --------

    >>> grey_label = 2
    >>> white_label = 3
    >>> zero_value = 1
    >>> optimalWeights = MS_LDA(lda_labels=[grey_label, white_label], label_file='label.mgz', weight_file='weights.txt',
                               shift=zero_value, synth='synth_out.mgz', conform=True, use_weights=True, images=['FLASH1.mgz',
                               'FLASH2.mgz', 'FLASH3.mgz'])
    >>> optimalWeights.cmdline
    'mri_ms_LDA -lda 2 3 -label label.mgz -weight weights.txt -shift 0 -synth synth_out.mgz -conform -W FLASH1.mgz FLASH2.mgz
    FLASH3.mgz'
    """

    _cmd = 'mri_ms_LDA'
    input_spec = MS_LDAInputSpec
    output_spec = MS_LDAOutputSpec

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['output_synth'] = os.path.abspath(self.inputs.output_synth)
        if not isdefined(self.inputs.use_weights) or self.inputs.use_weights is False:
            outputs['weight_file'] = os.path.abspath(self.inputs.weight_file)
        return outputs

    def _verify_weights_file_exists(self):
        if not os.path.exists(os.path.abspath(self.inputs.weight_file)):
            raise traits.TraitError("MS_LDA: use_weights must accompany an existing weights file")

    def _format_arg(self, name, spec, value):
        if name is 'use_weights':
            if self.inputs.use_weights is True:
                self._verify_weights_file_exists()
            else: return ''
                # TODO: Fix bug when boolean values are set explicitly to false
        return super(MS_LDA, self)._format_arg(name, spec, value)
