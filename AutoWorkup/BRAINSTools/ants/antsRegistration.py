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
    antsRegistration.inputs.fixedMask=SUBJ_A_small_T2_mask.nii.gz
    antsRegistration.inputs.movingMask=SUBJ_B_small_T2_mask.nii.gz
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
    # TODO: Metric has not yet been implemented in the executable
    metric_weight = traits.Int(requires=['metric'], default=1, desc="Note that the metricWeight is currently not used. Rather, it is a temporary place holder until multivariate metrics are available for a single stage.")
    radius = traits.Int(requires=['metric'], desc='')
    sampling_strategy = traits.Enum("Regular", "Random", requires=['metric'], default='Regular', desc='')
    sampling_percentage = traits.Range(low=0.0, high=1.0, require=['metric'], desc='')
    fixed_image_mask = File(mandatory=True, desc=(''), exists=True)
    moving_image_mask = File(argstr='%s', mandatory=True, desc='', exists=True)
    initial_fixed_transform = File(argstr='%s', desc='', exists=True)
    invert_initial_fixed_transform = traits.Bool(desc='', requires=["initial_fixed_transform"])
    transform = traits.Str(argstr='--transform %s', mandatory = True)
    n_iterations = traits.List(traits.Int(), argstr="%s")
    convergence_threshold = traits.Float(requires=['n_iterations'])
    convergence_window_size = traits.Int(requires=['n_iterations', 'convergence_threshold'])
    shrink_factors = traits.List(traits.Int(), argstr="--shrink-factors %s", sep='x')
    smoothing_sigmas = traits.List(traits.Int(), argstr="--smoothing-sigmas %s", sep='x')
    use_histogram_matching = traits.Bool(argstr="--use-histogram-matching")
    output_warped_image = traits.Either(traits.Bool, File(), hash_files=False, desc="")
    output_inverted_warped_image = traits.Either(traits.Bool, File(), hash_files=False, requires=['output_warped_image'], desc="")
    output_transform_prefix = traits.Str("transform", usedefault=True, argstr="%s", desc="")

class AntsRegistrationOutputSpec(TraitedSpec):
    warped_image = File(exists=True, desc='Warped image')
    inverted_warped_image = File(exists=True, desc='Inverted warped image')
    warped_transform = File(exists=True, desc='Warp transform')
    inverted_warped_transform = File(exists=True, desc='Inverted warp transform')

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
                retval.append("--metric '%s[%s,%s,1,5]'" % (self.inputs.metric, self.inputs.fixed_image[ii], self.inputs.moving_image[ii]))
            return " ".join(retval)
        elif opt == 'moving_image_mask':
            return "--masks [%s,%s]"%(self.inputs.fixed_image_mask, self.inputs.moving_image_mask)
        elif opt == 'initial_fixed_transform':
            if isdefined(self.inputs.invert_initial_fixed_transform) and self.inputs.invert_initial_fixed_transform:
                return "--initial-moving-transform [%s, 1]"%self.inputs.initial_fixed_transform
            else:
                return "--initial-moving-transform %s"%self.inputs.initial_fixed_transform
        elif opt == "n_iterations":
            convergence_iter = "x".join([str(i) for i in self.inputs.n_iterations])
            if isdefined(self.inputs.convergence_window_size):
                return "--convergence [%s,%g,%d]"%(convergence_iter,
                                                   self.inputs.convergence_threshold,
                                                   self.inputs.convergence_window_size)
            elif isdefined(self.inputs.convergence_threshold):
                return "--convergence [%s,%g]"%(convergence_iter,
                                                   self.inputs.convergence_threshold)
            else:
                return "--convergence %s"%(convergence_iter)
        elif opt == 'output_transform_prefix':
            if isdefined(self.inputs.output_inverted_warped_image) and self.inputs.output_inverted_warped_image:
                return '--output [%s, %s, %s]' %(self.inputs.output_transform_prefix, self._getOutputWarpedImageFileName(), self._getOutputWarpedImageFileName(inverted=True))
            elif isdefined(self.inputs.output_warped_image) and self.inputs.output_warped_image:
                return '--output [%s, %s]' %(self.inputs.output_transform_prefix, self._getOutputWarpedImageFileName())
            else:
                return '--output %s' % self.inputs.output_transform_prefix

        return super(AntsRegistration, self)._format_arg(opt, spec, val)

    def _getOutputWarpedImageFileName(self, inverted=False):
        value = self.inputs.output_warped_image
        _, fixedName, ext = split_filename(self.inputs.fixed_image[0])
        _, movingName, __ = split_filename(self.inputs.moving_image[0])
        if inverted:
            defaultName = '%s_to_%s%s' % (fixedName, movingName, ext)
        else:
            defaultName = '%s_to_%s%s' % (movingName, fixedName, ext)
        if isinstance(value, bool):
            if value == True:
                return defaultName
        else:
            return value

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['warped_transform'] = os.path.abspath(self.inputs.output_transform_prefix + '1Warp.nii.gz')
        outputs['inverted_warped_transform'] = os.path.abspath(self.inputs.output_transform_prefix + '1InverseWarp.nii.gz')
        if isdefined(self.inputs.output_warped_image) and self.inputs.output_warped_image:
            outputs['warped_image'] = os.path.abspath(self._getOutputWarpedImageFileName())
        if isdefined(self.inputs.output_inverted_warped_image) and self.inputs.output_inverted_warped_image:
            outputs['inverted_warped_image'] = os.path.abspath(self._getOutputWarpedImageFileName(inverted=True))
        return outputs
