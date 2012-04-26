# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""The antsRegistration module provides basic functions for interfacing with ants functions.

  Change directory to provide relative paths for doctests

   >>> import os
   >>> filepath = os.path.dirname( os.path.realpath( __file__ ) )
   >>> datadir = os.path.realpath(os.path.join(filepath, '../../testing/data'))
   >>> os.chdir(datadir)

"""

# Standard library imports
import os
from glob import glob

# Local imports
from nipype.interfaces.base import (TraitedSpec, File, traits, InputMultiPath, OutputMultiPath,
                    isdefined)
from nipype.utils.filemanip import split_filename
from .base import ANTSCommand, ANTSCommandInputSpec

class WarpImageMultiTransformInputSpec(ANTSCommandInputSpec):
    dimension = traits.Enum(3, 2, argstr='%d', usedefault=True,
                            desc='image dimension (2 or 3)', position=1)
    moving_image = File(argstr='%s', mandatory=True, copyfile=True,
                        desc=('image to apply transformation to (generally a '
                              'coregistered functional)') )
    out_postfix = traits.Str('_wimt', argstr='%s', usedefault=True,
                             desc=('Postfix that is prepended to all output '
                                   'files (default = _wimt)'))
    reference_image = File(argstr='-R %s', xor=['tightest_box'],
                       desc='reference image space that you wish to warp INTO')
    tightest_box = traits.Bool(argstr='--tightest-bounding-box',
                          desc=('computes tightest bounding box (overrided by '  \
                                'reference_image if given)'),
                          xor=['reference_image'])
    reslice_by_header = traits.Bool(argstr='--reslice-by-header',
                     desc=('Uses orientation matrix and origin encoded in '
                           'reference image file header. Not typically used '
                           'with additional transforms'))
    use_nearest = traits.Bool(argstr='--use-NN',
                              desc='Use nearest neighbor interpolation')
    use_bspline = traits.Bool(argstr='--use-Bspline',
                              desc='Use 3rd order B-Spline interpolation')
    transformation_series = InputMultiPath(File(exists=True), argstr='%s',
                             desc='transformation file(s) to be applied',
                             mandatory=True, copyfile=False)
    invert_affine = traits.List(traits.Int,
                    desc=('List of Affine transformations to invert. '
                          'E.g.: [1,4,5] inverts the 1st, 4th, and 5th Affines '
                          'found in transformation_series'))

class WarpImageMultiTransformOutputSpec(TraitedSpec):
    output_image = File(exists=True, desc='Warped image')


class WarpImageMultiTransform(ANTSCommand):
    """Warps an image from one space to another

    Examples
    --------

    >>> from nipype.interfaces.ants import WarpImageMultiTransform
    >>> wimt = WarpImageMultiTransform()
    >>> wimt.inputs.moving_image = 'structural.nii'
    >>> wimt.inputs.reference_image = 'ants_deformed.nii.gz'
    >>> wimt.inputs.transformation_series = ['ants_Warp.nii.gz','ants_Affine.txt']
    >>> wimt.cmdline
    'WarpImageMultiTransform 3 structural.nii structural_wimt.nii -R ants_deformed.nii.gz ants_Warp.nii.gz ants_Affine.txt'

    """

    _cmd = 'WarpImageMultiTransform'
    input_spec = WarpImageMultiTransformInputSpec
    output_spec = WarpImageMultiTransformOutputSpec

    def _format_arg(self, opt, spec, val):
        if opt == 'out_postfix':
            _, name, ext = split_filename(os.path.abspath(self.inputs.moving_image))
            return name + val + ext
        if opt == 'transformation_series':
            if isdefined(self.inputs.invert_affine):
                series = []
                affine_counter = 0
                for transformation in val:
                    if affine_counter in self.inputs.invert_affine:
                        series.append( '-i' )
                    series.append(transformation)
                    affine_counter += 1
                return ' '.join(series)
            else:
              return ' '.join(val)

        return super(WarpImageMultiTransform, self)._format_arg(opt, spec, val)

    def _list_outputs(self):
        outputs = self._outputs().get()
        _, name, ext = split_filename(os.path.abspath(self.inputs.moving_image))
        outputs['output_image'] = os.path.join(os.getcwd(),
                                             ''.join((name,
                                                      self.inputs.out_postfix,
                                                      ext)))
        return outputs

"""
  antsRegistration \
        -d 3 \
        -m CC[/IPLlinux/ipldev/scratch/johnsonhj/PREDICT/ExpandedExperiment/B4AUTO.ExpandedExperiment/BAW_20120104_workflow/_uid_PHD_024_0003_42245/11_BABC/t1_average_BRAINSABC.nii.gz,/ipldev/scratch/johnsonhj/src/BRAINSStandAlone-Darwin-clang/ReferenceAtlas-build/Atlas/Atlas_20120104/template_t1.nii.gz,1,5] \
        -m CC[/IPLlinux/ipldev/scratch/johnsonhj/PREDICT/ExpandedExperiment/B4AUTO.ExpandedExperiment/BAW_20120104_workflow/_uid_PHD_024_0003_42245/11_BABC/t2_average_BRAINSABC.nii.gz,/ipldev/scratch/johnsonhj/src/BRAINSStandAlone-Darwin-clang/ReferenceAtlas-build/Atlas/Atlas_20120104/template_t2.nii.gz,1,5] \
        -t SyN[0.25,3.0,0.0] \
        -r [/IPLlinux/ipldev/scratch/johnsonhj/PREDICT/ExpandedExperiment/B4AUTO.ExpandedExperiment/BAW_20120104_workflow/_uid_PHD_024_0003_42245/05_BLI/landmarkInitializer_atlas_to_subject_transform.mat,0] \
        -o ANTS_ \
        -c [70x70x20,1e-6,10] \
        -f 3x2x1 \
        -s 0x0x0 \
        -u 1
"""

class antsRegistrationInputSpec(ANTSCommandInputSpec):
    dimension = traits.Enum(3, 2, argstr='-d %d', usedefault=True,
                             desc='image dimension (2 or 3)', position=1)
    reference_image = File(exists=True,
                           argstr='-r %s', desc='template file to warp to',
                           mandatory=True, copyfile=True)
    input_image = File(exists=True,
                       argstr='-i %s', desc='input image to warp to template',
                       mandatory=True, copyfile=False)
    force_proceed = traits.Bool(argstr='-f 1',
                             desc=('force script to proceed even if headers '
                                   'may be incompatible'))
    inverse_warp_template_labels = traits.Bool(argstr='-l',
                       desc=('Applies inverse warp to the template labels '
                             'to estimate label positions in target space (use '
                             'for template-based segmentation)'))
    max_iterations = traits.List(traits.Int, argstr='-m %s', sep='x',
                             desc=('maximum number of iterations (must be '
                                   'list of integers in the form [J,K,L...]: '
                                   'J = coarsest resolution iterations, K = '
                                   'middle resolution interations, L = fine '
                                   'resolution iterations'))
    bias_field_correction = traits.Bool(argstr='-n 1',
                                desc=('Applies bias field correction to moving '
                                      'image'))
    similarity_metric = traits.Enum('PR', 'CC', 'MI', 'MSQ', argstr='-s %s',
            desc=('Type of similartiy metric used for registration '
                  '(CC = cross correlation, MI = mutual information, '
                  'PR = probability mapping, MSQ = mean square difference)'))
    transformation_model = traits.Enum('GR', 'EL', 'SY', 'S2', 'EX', 'DD', 'RI',
                                       'RA', argstr='-t %s', usedefault=True,
               desc=('Type of transofmration model used for registration '
                     '(EL = elastic transformation model, SY = SyN with time, '
                     'arbitrary number of time points, S2 =  SyN with time '
                     'optimized for 2 time points, GR = greedy SyN, EX = '
                     'exponential, DD = diffeomorphic demons style exponential '
                     'mapping, RI = purely rigid, RA = affine rigid'))
    out_prefix = traits.Str('ants_', argstr='-o %s', usedefault=True,
                             desc=('Prefix that is prepended to all output '
                                   'files (default = ants_)'))
    quality_check = traits.Bool(argstr='-q 1',
                             desc='Perform a quality check of the result')


class antsRegistrationOutputSpec(TraitedSpec):
    affine_transformation = File(exists=True, desc='affine (prefix_Affine.txt)')
    warp_field = File(exists=True, desc='warp field (prefix_Warp.nii)')
    inverse_warp_field = File(exists=True,
                            desc='inverse warp field (prefix_InverseWarp.nii)')
    input_file = File(exists=True, desc='input image (prefix_repaired.nii)')
    output_file = File(exists=True, desc='output image (prefix_deformed.nii)')

