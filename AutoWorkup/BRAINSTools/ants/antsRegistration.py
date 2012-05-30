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
from nipype.interfaces.base import (CommandLine, CommandLineInputSpec,
                                    InputMultiPath, traits, TraitedSpec,
                                    OutputMultiPath, isdefined,
                                    File, Directory)
from nipype.utils.filemanip import split_filename
#from nipype.interfaces.ants.base import ANTSCommand, ANTSCommandInputSpec

#class antsRegistrationInputSpec(ANTSCommandInputSpec):
class antsRegistrationInputSpec(CommandLineInputSpec):
    dimension = traits.Enum(3, 2, argstr='--dimensionality %d', usedefault=False, desc='image dimension (2 or 3)')
    fixed_image = InputMultiPath(File(exists=True), mandatory=True, desc=('image to apply transformation to (generally a coregistered functional)') )
    moving_image = InputMultiPath(File(exists=True), argstr='%s', mandatory=True, desc=('image to apply transformation to (generally a coregistered functional)') )

    metric = traits.Enum("CC", "MeanSquares", "Demons", "GC", "MI", "Mattes", mandatory=True, desc="")
    # TODO: Metric has not yet been implemented in the executable
    metric_weight = traits.Int(1,requires=['metric'], usedefault=True, desc="Note that the metricWeight is currently not used. Rather, it is a temporary place holder until multivariate metrics are available for a single stage.")
    radius = traits.Int(5,requires=['metric'], usedefault=True,desc='')

    sampling_strategy = traits.Enum("Regular", "Random", requires=['metric'], default='Regular', desc='')
    sampling_percentage = traits.Range(low=0.0, high=1.0, require=['metric'], desc='')
    fixed_image_mask = File(mandatory=False, desc=(''), requires=['moving_image_mask'], exists=True)
    moving_image_mask = File(argstr='%s', mandatory=False, desc='', requires=['fixed_image_mask'], exists=True)
    initial_moving_transform = File(argstr='%s', desc='', exists=True)
    invert_initial_moving_transform = traits.Bool(desc='', requires=["initial_moving_transform"])
    transform = traits.Str(argstr='--transform "%s"', mandatory = True)

    use_estimate_learning_rate_once = traits.Bool(argstr="--use-estimate-learning-rate-once")
    use_histogram_matching = traits.Bool(argstr="--use-histogram-matching")
    number_of_iterations = traits.List(traits.Int(), argstr="%s")
    smoothing_sigmas = traits.List(traits.Int(), argstr="--smoothing-sigmas %s", sep='x')
    shrink_factors = traits.List(traits.Int(), argstr="--shrink-factors %s", sep='x')

    convergence_threshold = traits.Float(1e-6,requires=['number_of_iterations'],usedefault=True)
    convergence_window_size = traits.Int(10,requires=['number_of_iterations', 'convergence_threshold'],usedefault=True)
    output_transform_prefix = traits.Str("transform", usedefault=True, argstr="%s", desc="")
    output_warped_image = traits.Either(traits.Bool, File(), hash_files=False, desc="")
    output_inverse_warped_image = traits.Either(traits.Bool, File(), hash_files=False, requires=['output_warped_image'], desc="")

class antsRegistrationOutputSpec(TraitedSpec):
    #affine_transform = File(exists=True, desc='Affine transform file')
    warp_transform = File(exists=True, desc='Warp transform')
    inverse_warp_transform = File(exists=True, desc='Inverse warp transform')
    warped_image = File(exists=True, desc='Warped image')
    inverse_warped_image = File(exists=True, desc='Inverse warped image')

#class antsRegistration(ANTSCommand):
class antsRegistration(CommandLine):
    """
    Examples
    --------
    >>>
    """
    _cmd = 'antsRegistration'
    input_spec = antsRegistrationInputSpec
    output_spec = antsRegistrationOutputSpec

    def _format_arg(self, opt, spec, val):
        if opt == 'moving_image':
            retval = []
            for ii in range(len(self.inputs.moving_image)):
                retval.append('--metric "%s[%s,%s,%d,%d]"' % (self.inputs.metric, self.inputs.fixed_image[ii], self.inputs.moving_image[ii],self.inputs.metric_weight,self.inputs.radius))
            return " ".join(retval)
        elif opt == 'moving_image_mask':
            return '--masks "[%s,%s]"' % (self.inputs.fixed_image_mask, self.inputs.moving_image_mask)
        elif opt == 'initial_moving_transform':
            if isdefined(self.inputs.invert_initial_moving_transform) and self.inputs.invert_initial_moving_transform:
                return '--initial-moving-transform "[%s,1]"' % self.inputs.initial_moving_transform
            else:
                return '--initial-moving-transform "[%s,0]"' % self.inputs.initial_moving_transform
        elif opt == "number_of_iterations":
            convergence_iter = "x".join([str(i) for i in self.inputs.number_of_iterations])
            return '--convergence "[%s,%g,%d]"' % (convergence_iter,
                                                self.inputs.convergence_threshold,
                                                self.inputs.convergence_window_size)
        elif opt == 'output_transform_prefix':
            if isdefined(self.inputs.output_inverse_warped_image) and self.inputs.output_inverse_warped_image:
                return '--output "[%s,%s,%s]"' % (self.inputs.output_transform_prefix, self.inputs.output_warped_image, self.inputs.output_inverse_warped_image )
            elif isdefined(self.inputs.output_warped_image) and self.inputs.output_warped_image:
                return '--output "[%s,%s]"'     % (self.inputs.output_transform_prefix, self.inputs.output_warped_image )
            else:
                return '--output %s' % self.inputs.output_transform_prefix
        return super(antsRegistration, self)._format_arg(opt, spec, val)

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['warp_transform'] = os.path.abspath(self.inputs.output_transform_prefix + '1Warp.nii.gz')
        outputs['inverse_warp_transform'] = os.path.abspath(self.inputs.output_transform_prefix + '1InverseWarp.nii.gz')
        if isdefined(self.inputs.output_warped_image) and self.inputs.output_warped_image:
            outputs['warped_image'] = os.path.abspath(self.inputs.output_warped_image)
        if isdefined(self.inputs.output_inverse_warped_image) and self.inputs.output_inverse_warped_image:
            outputs['inverse_warped_image'] = os.path.abspath(self.inputs.output_inverse_warped_image)
        return outputs
