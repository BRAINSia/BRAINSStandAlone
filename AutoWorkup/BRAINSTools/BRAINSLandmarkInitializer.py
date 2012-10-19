from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSLandmarkInitializerInputSpec(CommandLineInputSpec):
    inputFixedLandmarkFilename = File(desc="input fixed landmark. *.fcsv", exists=True, argstr="--inputFixedLandmarkFilename %s")
    inputMovingLandmarkFilename = File(desc="input moving landmark. *.fcsv", exists=True, argstr="--inputMovingLandmarkFilename %s")
    inputWeightFilename = File(desc="Input weight file name for landmarks. Higher weighted landmark will be considered more heavily. Weights are propotional, that is the magnitude of weights will be normalized by its minimum and maximum value. ", exists=True, argstr="--inputWeightFilename %s")
    outputTransformFilename = traits.Either(traits.Bool, File(), hash_files=False, desc="output transform file name (ex: ./outputTransform.h5) ", argstr="--outputTransformFilename %s")


class BRAINSLandmarkInitializerOutputSpec(TraitedSpec):
    outputTransformFilename = File(desc="output transform file name (ex: ./outputTransform.h5) ", exists=True)


class BRAINSLandmarkInitializer(SlicerCommandLine):
    """title: BRAINSLandmarkInitializer

category: Utilities.BRAINS

description: Create transformation file (*mat) from a pair of landmarks (*fcsv) files.

version:  1.0

license: https://www.nitrc.org/svn/brains/BuildScripts/trunk/License.txt

contributor: Eunyoung Regina Kim

"""

    input_spec = BRAINSLandmarkInitializerInputSpec
    output_spec = BRAINSLandmarkInitializerOutputSpec
    _cmd = " BRAINSLandmarkInitializer "
    _outputs_filenames = {'outputTransformFilename':'outputTransformFilename'}
