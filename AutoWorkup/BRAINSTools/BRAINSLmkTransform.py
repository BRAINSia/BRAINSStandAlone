from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSLmkTransformInputSpec(CommandLineInputSpec):
    inputMovingLandmarks = File(desc="Input Moving Landmark list file in fcsv,             ", exists=True, argstr="--inputMovingLandmarks %s")
    inputFixedLandmarks = File(desc="Input Fixed Landmark list file in fcsv,             ", exists=True, argstr="--inputFixedLandmarks %s")
    outputAffineTransform = traits.Either(traits.Bool, File(), hash_files=False, desc="The filename for the estimated affine transform,             ", argstr="--outputAffineTransform %s")
    inputMovingVolume = File(desc="The filename of input moving volume", exists=True, argstr="--inputMovingVolume %s")
    inputReferenceVolume = File(desc="The filename of the reference volume", exists=True, argstr="--inputReferenceVolume %s")
    outputResampledVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="The filename of the output resampled volume", argstr="--outputResampledVolume %s")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class BRAINSLmkTransformOutputSpec(TraitedSpec):
    outputAffineTransform = File(desc="The filename for the estimated affine transform,             ", exists=True)
    outputResampledVolume = File(desc="The filename of the output resampled volume", exists=True)


class BRAINSLmkTransform(SlicerCommandLine):
    """title: Landmark Transform (BRAINS)

category: Utilities.BRAINS

description: 
      This utility program estimates the affine transform to align the fixed landmarks to the moving landmarks, and then generate the resampled moving image to the same physical space as that of the reference image.
    

version: 1.0

documentation-url: http://www.nitrc.org/projects/brainscdetector/

"""

    input_spec = BRAINSLmkTransformInputSpec
    output_spec = BRAINSLmkTransformOutputSpec
    _cmd = " BRAINSLmkTransform "
    _outputs_filenames = {'outputResampledVolume':'outputResampledVolume.nii','outputAffineTransform':'outputAffineTransform.mat'}
