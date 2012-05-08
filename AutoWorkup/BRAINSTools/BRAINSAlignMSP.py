from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSAlignMSPInputSpec(CommandLineInputSpec):
    inputVolume = File(desc=",         The Image to be resampled,       ", exists=True, argstr="--inputVolume %s")
    OutputresampleMSP = traits.Either(traits.Bool, File(), hash_files=False, desc=",         The image to be output.,       ", argstr="--OutputresampleMSP %s")
    verbose = traits.Bool(desc=",         Show more verbose output,       ", argstr="--verbose ")
    resultsDir = traits.Either(traits.Bool, Directory(), hash_files=False, desc=",         The directory for the results to be written.,       ", argstr="--resultsDir %s")
    writedebuggingImagesLevel = traits.Int(desc=",           This flag controls if debugging images are produced.  By default value of 0 is no images.  Anything greater than zero will be increasing level of debugging images.,       ", argstr="--writedebuggingImagesLevel %d")
    mspQualityLevel = traits.Int(desc=",           Flag cotrols how agressive the MSP is estimated.  0=quick estimate (9 seconds), 1=normal estimate (11 seconds), 2=great estimate (22 seconds), 3=best estimate (58 seconds).,       ", argstr="--mspQualityLevel %d")
    rescaleIntensities = traits.Bool(desc=",           Flag to turn on rescaling image intensities on input.,       ", argstr="--rescaleIntensities ")
    trimRescaledIntensities = traits.Float(desc=",           Turn on clipping the rescaled image one-tailed on input.  Units of standard deviations above the mean.  Very large values are very permissive.  Non-positive value turns clipping off.  Defaults to removing 0.00001 of a normal tail above the mean.,       ", argstr="--trimRescaledIntensities %f")
    rescaleIntensitiesOutputRange = InputMultiPath(traits.Int, desc=",           This pair of integers gives the lower and upper bounds on the signal portion of the output image.  Out-of-field voxels are taken from BackgroundFillValue.,       ", sep=",", argstr="--rescaleIntensitiesOutputRange %s")
    BackgroundFillValue = traits.Str(desc="Fill the background of image with specified short int value. Enter number or use BIGNEG for a large negative number.", argstr="--BackgroundFillValue %s")
    interpolationMode = traits.Enum("NearestNeighbor", "Linear", "ResampleInPlace", "BSpline", "WindowedSinc", "Hamming", "Cosine", "Welch", "Lanczos", "Blackman", desc="Type of interpolation to be used when applying transform to moving volume.  Options are Linear, ResampleInPlace, NearestNeighbor, BSpline, or WindowedSinc", argstr="--interpolationMode %s")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class BRAINSAlignMSPOutputSpec(TraitedSpec):
    OutputresampleMSP = File(desc=",         The image to be output.,       ", exists=True)
    resultsDir = Directory(desc=",         The directory for the results to be written.,       ", exists=True)


class BRAINSAlignMSP(SlicerCommandLine):
    """title: Align Mid Saggital Brain (BRAINS)

category: Utilities.BRAINS

description: Resample an image into ACPC alignement ACPCDetect

"""

    input_spec = BRAINSAlignMSPInputSpec
    output_spec = BRAINSAlignMSPOutputSpec
    _cmd = " BRAINSAlignMSP "
    _outputs_filenames = {'OutputresampleMSP':'OutputresampleMSP.nii','resultsDir':'resultsDir'}
