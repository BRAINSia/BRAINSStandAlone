from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSLinearModelerEPCAInputSpec(CommandLineInputSpec):
    inputTrainingList = File(desc="Input Training Landmark List Filename,             ", exists=True, argstr="--inputTrainingList %s")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class BRAINSLinearModelerEPCAOutputSpec(TraitedSpec):
    pass


class BRAINSLinearModelerEPCA(SlicerCommandLine):
    """title: Landmark Linear Modeler (BRAINS)

category: Utilities.BRAINS

description:
      Training linear model using EPCA. Implementation based on my MS thesis, "A METHOD FOR AUTOMATED LANDMARK CONSTELLATION DETECTION USING EVOLUTIONARY PRINCIPAL COMPONENTS AND STATISTICAL SHAPE MODELS"



version: 1.0

documentation-url: http://www.nitrc.org/projects/brainscdetector/

"""

    input_spec = BRAINSLinearModelerEPCAInputSpec
    output_spec = BRAINSLinearModelerEPCAOutputSpec
    _cmd = " BRAINSLinearModelerEPCA "
    _outputs_filenames = {}
