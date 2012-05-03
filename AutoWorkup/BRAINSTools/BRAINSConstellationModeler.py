from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSConstellationModelerInputSpec(CommandLineInputSpec):
    verbose = traits.Bool(desc=",               Show more verbose output,             ", argstr="--verbose ")
    inputTrainingList = File(desc=",               Setup file, giving all parameters for training up a template model for each landmark.,             ", exists=True, argstr="--inputTrainingList %s")
    outputModel = traits.Either(traits.Bool, File(), hash_files=False, desc=",               The full filename of the output model file.,             ", argstr="--outputModel %s")
    saveOptimizedLandmarks = traits.Bool(desc=",               Flag to make a new subject-specific landmark definition file in the same format produced by Slicer3 with the optimized landmark (the detected RP, AC, and PC) in it.  Useful to tighten the variances in the ConstellationModeler.,             ", argstr="--saveOptimizedLandmarks ")
    optimizedLandmarksFilenameExtender = traits.Str(desc=",                If the trainingList is (indexFullPathName) and contains landmark data filenames [path]/[filename].fcsv ,  make the optimized landmarks filenames out of [path]/[filename](thisExtender) and the optimized version of the input trainingList out of (indexFullPathName)(thisExtender) , when you rewrite all the landmarks according to the saveOptimizedLandmarks flag.,             ", argstr="--optimizedLandmarksFilenameExtender %s")
    resultsDir = traits.Either(traits.Bool, Directory(), hash_files=False, desc=",               The directory for the results to be written.,             ", argstr="--resultsDir %s")
    mspQualityLevel = traits.Int(desc=",                 Flag cotrols how agressive the MSP is estimated.  0=quick estimate (9 seconds), 1=normal estimate (11 seconds), 2=great estimate (22 seconds), 3=best estimate (58 seconds).,             ", argstr="--mspQualityLevel %d")
    rescaleIntensities = traits.Bool(desc=",                 Flag to turn on rescaling image intensities on input.,             ", argstr="--rescaleIntensities ")
    trimRescaledIntensities = traits.Float(desc=",                 Turn on clipping the rescaled image one-tailed on input.  Units of standard deviations above the mean.  Very large values are very permissive.  Non-positive value turns clipping off.  Defaults to removing 0.00001 of a normal tail above the mean.,             ", argstr="--trimRescaledIntensities %f")
    rescaleIntensitiesOutputRange = InputMultiPath(traits.Int, desc=",                 This pair of integers gives the lower and upper bounds on the signal portion of the output image.  Out-of-field voxels are taken from BackgroundFillValue.,             ", sep=",", argstr="--rescaleIntensitiesOutputRange %s")
    BackgroundFillValue = traits.Str(desc="Fill the background of image with specified short int value. Enter number or use BIGNEG for a large negative number.", argstr="--BackgroundFillValue %s")
    writedebuggingImagesLevel = traits.Int(desc=",                 This flag controls if debugging images are produced.  By default value of 0 is no images.  Anything greater than zero will be increasing level of debugging images.,             ", argstr="--writedebuggingImagesLevel %d")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class BRAINSConstellationModelerOutputSpec(TraitedSpec):
    outputModel = File(desc=",               The full filename of the output model file.,             ", exists=True)
    resultsDir = Directory(desc=",               The directory for the results to be written.,             ", exists=True)


class BRAINSConstellationModeler(SlicerCommandLine):
    """title: Generate Landmarks Model (BRAINS)

category: Utilities.BRAINS

description: Train up a model for BRAINSConstellationDetector

"""

    input_spec = BRAINSConstellationModelerInputSpec
    output_spec = BRAINSConstellationModelerOutputSpec
    _cmd = " BRAINSConstellationModeler "
    _outputs_filenames = {'outputModel':'outputModel.mdl','resultsDir':'resultsDir'}
