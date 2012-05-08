from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSTrimForegroundInDirectionInputSpec(CommandLineInputSpec):
    inputVolume = File(desc="Input image to trim off the neck (and also air-filling noise.)", exists=True, argstr="--inputVolume %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="Output image with neck and air-filling noise trimmed isotropic image with AC at center of image.", argstr="--outputVolume %s")
    directionCode = traits.Int(desc=",                 This flag chooses which dimension to compare.  The sign lets you flip direction.,             ", argstr="--directionCode %d")
    otsuPercentileThreshold = traits.Float(desc=",                 This is a parameter to FindLargestForegroundFilledMask, which is employed to trim off air-filling noise.,             ", argstr="--otsuPercentileThreshold %f")
    closingSize = traits.Int(desc=",                 This is a parameter to FindLargestForegroundFilledMask,             ", argstr="--closingSize %d")
    headSizeLimit = traits.Float(desc=",                 Use this to vary from the command line our search for how much upper tissue is head for the center-of-mass calculation.  Units are CCs, not cubic millimeters.,             ", argstr="--headSizeLimit %f")
    BackgroundFillValue = traits.Str(desc="Fill the background of image with specified short int value. Enter number or use BIGNEG for a large negative number.", argstr="--BackgroundFillValue %s")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class BRAINSTrimForegroundInDirectionOutputSpec(TraitedSpec):
    outputVolume = File(desc="Output image with neck and air-filling noise trimmed isotropic image with AC at center of image.", exists=True)


class BRAINSTrimForegroundInDirection(SlicerCommandLine):
    """title: Trim Foreground In Direction (BRAINS)

category: Utilities.BRAINS

description: This program will trim off the neck and also air-filling noise from the inputImage.

version: 0.1

documentation-url: http://www.nitrc.org/projects/art/

"""

    input_spec = BRAINSTrimForegroundInDirectionInputSpec
    output_spec = BRAINSTrimForegroundInDirectionOutputSpec
    _cmd = " BRAINSTrimForegroundInDirection "
    _outputs_filenames = {'outputVolume':'outputVolume.nii'}
