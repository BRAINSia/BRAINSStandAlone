# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""The antsRegistration module provides basic functions for interfacing with ants functions.

COMMAND:
     antsRegistration
          This program is a user-level registration application meant to utilize
          ITKv4-only classes. The user can specify any number of "stages" where a stage
          consists of a transform; an image metric; and iterations, shrink factors, and
          smoothing sigmas for each level.

OPTIONS:
     -d, --dimensionality 2/3
          This option forces the image to be treated as a specified-dimensional image. If
          not specified, N4 tries to infer the dimensionality from the input image.

     -o, --output outputTransformPrefix
                  [outputTransformPrefix,<outputWarpedImage>,<outputInverseWarpedImage>]
          Specify the output transform prefix (output format is .nii.gz ). Optionally, one
          can choose to warp the moving image to the fixed space and, if the inverse
          transform exists, one can also output the warped fixed image.

     -q, --initial-fixed-transform initialTransform
                                   [initialTransform,<useInverse>]
          Specify the initial fixed transform(s) which get immediately incorporated into
          the composite transform. The order of the transforms is stack-esque in that the
          last transform specified on the command line is the first to be applied. See
          antsApplyTransforms for additional information.

     -a, --composite-transform-file compositeFile
          Specify name of a composite transform file to write out after registration

     -r, --initial-moving-transform initialTransform
                                    [initialTransform,<useInverse>]
          Specify the initial moving transform(s) which get immediately incorporated into
          the composite transform. The order of the transforms is stack-esque in that the
          last transform specified on the command line is the first to be applied. See
          antsApplyTransforms for additional information.

     -m, --metric          CC[fixedImage,movingImage,metricWeight,radius,      <samplingStrategy={Regular,Random}>,<samplingPercentage=[0,1]>]
                  MeanSquares[fixedImage,movingImage,metricWeight,radius,      <samplingStrategy={Regular,Random}>,<samplingPercentage=[0,1]>]
                       Demons[fixedImage,movingImage,metricWeight,radius,      <samplingStrategy={Regular,Random}>,<samplingPercentage=[0,1]>]
                           GC[fixedImage,movingImage,metricWeight,radius,      <samplingStrategy={Regular,Random}>,<samplingPercentage=[0,1]>]
                           MI[fixedImage,movingImage,metricWeight,numberOfBins,<samplingStrategy={Regular,Random}>,<samplingPercentage=[0,1]>]
                       Mattes[fixedImage,movingImage,metricWeight,numberOfBins,<samplingStrategy={Regular,Random}>,<samplingPercentage=[0,1]>]
          These image metrics are available--- CC: ANTS neighborhood cross correlation,
          MI: Mutual information, Demons: (Thirion), MeanSquares, and GC: Global
          Correlation. Note that the metricWeight is currently not used. Rather, it is a
          temporary place holder until multivariate metrics are available for a single
          stage. The metrics can also employ a sampling strategy defined by a sampling
          percentage. The sampling strategy defaults to dense, otherwise it defines a
          point set over which to optimize the metric. The point set can be on a regular
          lattice or a random lattice of points slightly perturbed to minimize aliasing
          artifacts. samplingPercentage defines the fraction of points to select from the
          domain.

     -t, --transform Rigid[gradientStep]
                     Affine[gradientStep]
                     CompositeAffine[gradientStep]
                     Similarity[gradientStep]
                     Translation[gradientStep]
                     BSpline[gradientStep,meshSizeAtBaseLevel]
                     GaussianDisplacementField[gradientStep,updateFieldVarianceInVoxelSpace,totalFieldVarianceInVoxelSpace]
                     BSplineDisplacementField[gradientStep,updateFieldMeshSizeAtBaseLevel,totalFieldMeshSizeAtBaseLevel,<splineOrder=3>]
                     TimeVaryingVelocityField[gradientStep,numberOfTimeIndices,updateFieldVarianceInVoxelSpace,updateFieldTimeVariance,totalFieldVarianceInVoxelSpace,totalFieldTimeVariance]
                     TimeVaryingBSplineVelocityField[gradientStep,velocityFieldMeshSize,<numberOfTimePointSamples=4>,<splineOrder=3>]
                     SyN[gradientStep,updateFieldVarianceInVoxelSpace,totalFieldVarianceInVoxelSpace]
                     BSplineSyN[gradientStep,updateFieldMeshSizeAtBaseLevel,totalFieldMeshSizeAtBaseLevel,<splineOrder=3>]
          Several transform options are available. The gradientStep or learningRate
          characterizes the gradient descent optimization and is scaled appropriately for
          each transform using the shift scales estimator. Subsequent parameters are
          transform-specific and can be determined from the usage.

     -c, --convergence MxNxO
                       [MxNxO,<convergenceThreshold=1e-6>,<convergenceWindowSize=10>]
          Convergence is determined from the number of iterations per leveland is
          determined by fitting a line to the normalized energy profile of the last N
          iterations (where N is specified by the window size) and determining the slope
          which is then compared with the convergence threshold.

     -s, --smoothing-sigmas MxNxO...
          Specify the amount of smoothing at each level.

     -f, --shrink-factors MxNxO...
          Specify the shrink factor for the virtual domain (typically the fixed image) at
          each level.

     -u, --use-histogram-matching
          Histogram match the images before registration.

     -l, --use-estimate-learning-rate-once
          turn on the option that lets you estimate the learning rate step size only at
          the beginning of each level. * useful as a second stage of fine-scale
          registration.

     -w, --winsorize-image-intensities [lowerQuantile,upperQuantile]
          Winsorize data based on specified quantiles.

     -x, --masks [fixedImageMask,movingImageMask]
          Image masks to limit voxels considered by the metric.

     -h
          Print the help menu (short version).
          <VALUES>: 0

     --help
          Print the help menu.
          <VALUES>: 0

=======================================================================

How to run the test case:

cd /hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST
/ipldev/scratch/johnsonhj/src/ANTS-Darwin-clang/bin/antsRegistration \
    -d 3 \
    --mask '[SUBJ_A_small_T2_mask.nii.gz,SUBJ_B_small_T2_mask.nii.gz]' \
    -r '[20120430_1348_txfmv2fv_affine.mat,0]' \
    -o '[20120430_1348_ANTS6_,BtoA.nii.gz,AtoB.nii.gz]' \
    -m 'CC[SUBJ_A_T1_resampled.nii.gz,SUBJ_B_T1_resampled.nii.gz,1,5]' \
    -t 'SyN[0.25,3.0,0.0]' \
    -c '[100x70x20,1e-6,10]' \
    -f 3x2x1 \
    -s 0x0x0 \
    -u 1

//OPTIONAL INTERFACE FOR MULTI_MODAL_REGISTRATION:
#    -m 'CC[SUBJ_A_T2.nii.gz,SUBJ_B_T2.nii.gz,1,5]' \

    Nipype interface proposal:

    antsRegistration.inputs.dimension=3
    antsRegistration.inputs.mask=[SUBJ_A_small_T2_mask.nii.gz,SUBJ_B_small_T2_mask.nii.gz]
    antsRegistration.inputs.intialAffineTransform=20120430_1348_txfmv2fv_affine.mat
    antsRegistration.inputs.invertInitialAffineTransform=False
    antsRegistration.inputs.warpPrefix=20120430_1348_ANTS6_
    antsRegistration.inputs.movingResampledImage=BtoA.nii.gz ## Optional
    antsRegistration.inputs.fixedResampledImage=AtoB.nii.gz  ## Optional
    antsRegistration.inputs.metricName='CC'                  ## This is a family of interfaces, CC,MeanSquares,Demons,GC,MI,Mattes
    antsRegistration.inputs.fixedVolumesList=[SUBJ_A_T1_resampled.nii.gz,SUBJ_A_T2.nii.gz]
    antsRegistration.inputs.movingVolumesList=[SUBJ_B_T1_resampled.nii.gz,SUBJ_B_T2.nii.gz]
    antsRegistration.inputs.metricWeight=1
    antsRegistration.inputs.radiusOrBins=1                   ## for CC,MeanSquares,Demons,GC this is the radius and defaults to 1, for MI and Mattes, it is the number of Bins and defaults to 64
    antsRegistration.inputs.transformType='SyN'
    antsRegistration.inputs.transformGradientStep=0.25
    antsRegistration.inputs.transformUpdateFieldVariance=3.0
    antsRegistration.inputs.transformTotalFieldVariance=0.0
    antsRegistration.inputs.convergenceIterations=[100, 70, 20]
    antsRegistration.inputs.convergenceThreshold=1e-6
    antsRegistration.inputs.convergenceWindowSize=10
    antsRegistration.inputs.smoothing=[0,0,0]
    antsRegistration.inputs.useHistogramMatching=True

=======================================================================

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
from nipype.interfaces.base import (TraitedSpec, File, traits, InputMultiPath, OutputMultiPath, isdefined)
from nipype.utils.filemanip import split_filename
from nipype.interfaces.ants.base import ANTSCommand, ANTSCommandInputSpec

class AntsRegistrationInputSpec(ANTSCommandInputSpec):
    dimension = traits.Enum(3, 2, argstr='--dimensionality %d', usedefault=True, desc='image dimension (2 or 3)')
    fixed_image = InputMultiPath(File(exists=True), mandatory=True, desc=('image to apply transformation to (generally a coregistered functional)') )
    moving_image = InputMultiPath(File(exists=True), argstr='%s', mandatory=True, desc=('image to apply transformation to (generally a coregistered functional)') )
    metric = traits.Enum("CC", "MeanSquares", "Demons", "GC", "MI", "Mattes", mandatory=True, desc="")

    # fixed_image_masks = InputMultiPath(argstr='%s', mandatory=True, copyfile=True, desc=(''))
    # moving_image_masks = InputMultiPath(argstr='%s', mandatory=True, copyfile=True, desc=(''))
    # masks = ???
    # out_postfix = traits.Str('_wimt', argstr='%s', usedefault=True,
    #                          desc=('Postfix that is prepended to all output '
    #                                'files (default = _wimt)'))
    # reference_image = File(argstr='-R %s', xor=['tightest_box'],
    #                    desc='reference image space that you wish to warp INTO')
    # tightest_box = traits.Bool(argstr='--tightest-bounding-box',
    #                       desc=('computes tightest bounding box (overrided by '  \
    #                             'reference_image if given)'),
    #                       xor=['reference_image'])
    # reslice_by_header = traits.Bool(argstr='--reslice-by-header',
    #                  desc=('Uses orientation matrix and origin encoded in '
    #                        'reference image file header. Not typically used '
    #                        'with additional transforms'))
    # use_nearest = traits.Bool(argstr='--use-NN',
    #                           desc='Use nearest neighbor interpolation')
    # use_bspline = traits.Bool(argstr='--use-Bspline',
    #                           desc='Use 3rd order B-Spline interpolation')
    # transformation_series = InputMultiPath(File(exists=True), argstr='%s',
    #                          desc='transformation file(s) to be applied',
    #                          mandatory=True, copyfile=False)
    # invert_affine = traits.List(traits.Int,
    #                 desc=('List of Affine transformations to invert. '
    #                       'E.g.: [1,4,5] inverts the 1st, 4th, and 5th Affines '
    #                       'found in transformation_series'))

class AntsRegistrationOutputSpec(TraitedSpec):
    output_image = File(exists=True, desc='Warped image')

class AntsRegistration(ANTSCommand):
    """
    Examples
    --------

    >>>
    >>>
    >>>
    >>>
    >>>
    >>>
    """
    _cmd = 'antsRegistration'
    input_spec = AntsRegistrationInputSpec
    output_spec = AntsRegistrationOutputSpec

    def _format_arg(self, opt, spec, val):
        if opt == 'moving_image':
            retval = []
            for ii in range(len(self.inputs.moving_image)):
                retval.append("--metric '%s[%s,%s,1,5]' " % (self.inputs.metric, self.inputs.fixed_image[ii], self.inputs.moving_image[ii]))
            return " ".join(retval)
        return super(AntsRegistration, self)._format_arg(opt, spec, val)

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

