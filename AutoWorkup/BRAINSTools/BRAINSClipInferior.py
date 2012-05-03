from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSClipInferiorInputSpec(CommandLineInputSpec):
    inputVolume = File(desc="Input image to make a clipped short int copy from.", exists=True, argstr="--inputVolume %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="Output image, a short int copy of the upper portion of the input image, filled with BackgroundFillValue.", argstr="--outputVolume %s")
    acLowerBound = traits.Float(desc=",                 When the input image to the output image, replace the image with the BackgroundFillValue everywhere below the plane This Far in physical units (millimeters) below (inferior to) the AC point (assumed to be the voxel field middle.)  The oversize default was chosen to have no effect.  Based on visualizing a thousand masks in the IPIG study, we recommend a limit no smaller than 80.0 mm.,             ", argstr="--acLowerBound %f")
    BackgroundFillValue = traits.Str(desc="Fill the background of image with specified short int value. Enter number or use BIGNEG for a large negative number.", argstr="--BackgroundFillValue %s")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class BRAINSClipInferiorOutputSpec(TraitedSpec):
    outputVolume = File(desc="Output image, a short int copy of the upper portion of the input image, filled with BackgroundFillValue.", exists=True)


class BRAINSClipInferior(SlicerCommandLine):
    """title: Clip Inferior of Center of Brain (BRAINS)

category: Utilities.BRAINS

description: This program will read the inputVolume as a short int image, write the BackgroundFillValue everywhere inferior to the lower bound, and write the resulting clipped short int image in the outputVolume.
    

version: 1.0

"""

    input_spec = BRAINSClipInferiorInputSpec
    output_spec = BRAINSClipInferiorOutputSpec
    _cmd = " BRAINSClipInferior "
    _outputs_filenames = {'outputVolume':'outputVolume.nii'}
