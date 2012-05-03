from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class GenerateSummedGradientImageInputSpec(CommandLineInputSpec):
    inputVolume1 = File(desc="input volume 1, usally t1 image ", exists=True, argstr="--inputVolume1 %s")
    inputVolume2 = File(desc="input volume 2, usally t2 image ", exists=True, argstr="--inputVolume2 %s")
    outputFileName = traits.Either(traits.Bool, File(), hash_files=False, desc="(required) output file name ", argstr="--outputFileName %s")
    MaximumGradient = traits.Bool(desc="If set this flag, it will compute maximum gradient between two input volumes instead of sum of it.", argstr="--MaximumGradient ")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class GenerateSummedGradientImageOutputSpec(TraitedSpec):
    outputFileName = File(desc="(required) output file name ", exists=True)


class GenerateSummedGradientImage(SlicerCommandLine):
    """title: GenerateSummedGradient

category: Filtering.FeatureDetection

description: Automatic FeatureImages using neural networks

version:  1.0

license: https://www.nitrc.org/svn/brains/BuildScripts/trunk/License.txt 

contributor: Greg Harris, Eun Young Kim

"""

    input_spec = GenerateSummedGradientImageInputSpec
    output_spec = GenerateSummedGradientImageOutputSpec
    _cmd = " GenerateSummedGradientImage "
    _outputs_filenames = {'outputFileName':'outputFileName'}
