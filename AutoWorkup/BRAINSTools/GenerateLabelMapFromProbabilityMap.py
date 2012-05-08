from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class GenerateLabelMapFromProbabilityMapInputSpec(CommandLineInputSpec):
    inputVolumes = InputMultiPath(File(exists=True), desc="The Input probaiblity images to be computed for lable maps", argstr="--inputVolumes %s...")
    outputLabelVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="The Input binary image for region of interest", argstr="--outputLabelVolume %s")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class GenerateLabelMapFromProbabilityMapOutputSpec(TraitedSpec):
    outputLabelVolume = File(desc="The Input binary image for region of interest", exists=True)


class GenerateLabelMapFromProbabilityMap(SlicerCommandLine):
    """title: Label Map from Probability Images

category: Utilities.BRAINS

description: 
    Given a list of probability maps for labels, create a discrete label map where only the highest probability region is used for the labeling.
  

version: 0.1

contributor: University of Iowa Department of Psychiatry, http:://www.psychiatry.uiowa.edu
  

"""

    input_spec = GenerateLabelMapFromProbabilityMapInputSpec
    output_spec = GenerateLabelMapFromProbabilityMapOutputSpec
    _cmd = " GenerateLabelMapFromProbabilityMap "
    _outputs_filenames = {'outputLabelVolume':'outputLabelVolume.nii.gz'}
