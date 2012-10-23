"""ComposeMultiTransform ImageDimension output_field [-R reference_image] {[deformation_field | [-i] affine_transform_txt ]}
  Usage has the same form as WarpImageMultiTransform
 For Example:

ComposeMultiTransform Dimension  outwarp.nii   -R template.nii   ExistingWarp.nii  ExistingAffine.nii
 or for an inverse mapping :
ComposeMultiTransform Dimension  outwarp.nii   -R template.nii   -i ExistingAffine.nii ExistingInverseWarp.nii
 recalling that the -i option takes the inverse of the affine mapping

Or: to compose multiple affine text file into one:
ComposeMultiTransform ImageDimension output_affine_txt [-R reference_affine_txt] {[-i] affine_transform_txt}
This will be evoked if a text file is given as the second parameter. In this case reference_affine_txt is used
to define the center of the output affine.  The default reference is the first given affine text file.
This ignores all non-txt files among the following parameters."""

# Standard library imports
import os
import nipype

# Local imports
from nipype.interfaces.base import (TraitedSpec, File, traits, InputMultiPath, OutputMultiPath, isdefined)
from nipype.utils.filemanip import split_filename
from nipype.interfaces.ants.base import ANTSCommand, ANTSCommandInputSpec


class ComposeMultiTransformInputSpec(ANTSCommandInputSpec):
    dimension = traits.Enum(3, 2, argstr='%d', usedefault=True,
                            desc='image dimension (2 or 3)', position=1)
    out_postfix = traits.Str('_cmt', argstr='%s', usedefault=True, position=2,
                             desc=('Postfix that is prepended to all output '
                                   'files (default = _cmt)'))
    #output_affine_txt = File(argstr='%s', position=2,
    #                            desc='output affine')
    reference_affine_txt = File(argstr='-R %s', position=3,
                                desc='reference image space that you wish to warp INTO')
    transformation_series = InputMultiPath(File(copyfile=False), argstr='%s', #exists=True,
                             desc='transformation file(s) to be applied',
                             mandatory=True, copyfile=False)
    invert_affine = traits.List(traits.Int,
                    desc=('List of Affine transformations to invert. '
                          'E.g.: [1,4,5] inverts the 1st, 4th, and 5th Affines '
                          'found in transformation_series'))

class ComposeMultiTransformOutputSpec(TraitedSpec):
    output_image = File(exists=True, desc='Warped image')

class ComposeMultiTransform(ANTSCommand):
    _cmd = 'ComposeMultiTransform'
    input_spec = ComposeMultiTransformInputSpec
    output_spec = ComposeMultiTransformOutputSpec

    def _format_arg(self, opt, spec, val):
        if opt == 'out_postfix':
            _, name, ext = split_filename(os.path.abspath(self.inputs.reference_affine_txt))
            return name + val + ext
        if opt == 'transformation_series':
            series = []
            affine_counter = 0
            for transformation in val:
                if 'Affine' in transformation and \
                    isdefined(self.inputs.invert_affine):
                    affine_counter += 1
                    if affine_counter in self.inputs.invert_affine:
                        series += '-i',
                series += [transformation]
            return ' '.join(series)
        return super(ComposeMultiTransform, self)._format_arg(opt, spec, val)

    def _list_outputs(self):
        outputs = self._outputs().get()
        _, name, ext = split_filename(os.path.abspath(self.inputs.reference_affine_txt))
        outputs['output_image'] = os.path.join(os.getcwd(),
                                             ''.join((name,
                                                      self.inputs.out_postfix,
                                                      ext)))
        return outputs
