from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSCutInputSpec(CommandLineInputSpec):
    netConfiguration = File(desc="XML File defining BRAINSCut parameters. OLD NAME. PLEASE USE modelConfigurationFilename instead.", exists=True, argstr="--netConfiguration %s")
    modelConfigurationFilename = File(desc="XML File defining BRAINSCut parameters", exists=True, argstr="--modelConfigurationFilename %s")
    trainModelStartIndex = traits.Int(desc="Starting iteration for training", argstr="--trainModelStartIndex %d")
    verbose = traits.Int(desc="print out some debugging information", argstr="--verbose %d")
    multiStructureThreshold = traits.Bool(desc="multiStructureThreshold module to deal with overlaping area", argstr="--multiStructureThreshold ")
    histogramEqualization = traits.Bool(desc="A Histogram Equalization process could be added to the creating/applying process from Subject To Atlas. Default is false, which genreate input vectors without Histogram Equalization. ", argstr="--histogramEqualization ")
    computeSSEOn = traits.Bool(desc="compute Sum of Square Error (SSE) along the trained model until the number of iteration given in the modelConfigurationFilename file", argstr="--computeSSEOn ")
    generateProbability = traits.Bool(desc="Generate probability map", argstr="--generateProbability ")
    createVectors = traits.Bool(desc="create vectors for training neural net", argstr="--createVectors ")
    trainModel = traits.Bool(desc="train the neural net", argstr="--trainModel ")
    NoTrainingVectorShuffling = traits.Bool(desc="If this flag is on, there will be no shuffling.", argstr="--NoTrainingVectorShuffling ")
    applyModel = traits.Bool(desc="apply the neural net", argstr="--applyModel ")
    validate = traits.Bool(desc="validate data set.Just need for the first time run ( This is for validation of xml file and not working yet )", argstr="--validate ")
    method = traits.Enum("RandomForest", "ANN", argstr="--method %s")
    numberOfTrees = traits.Int(desc=" Random tree: number of trees. This is to be used when only one model with specified depth wish to be created. ", argstr="--numberOfTrees %d")
    randomTreeDepth = traits.Int(desc=" Random tree depth. This is to be used when only one model with specified depth wish to be created. ", argstr="--randomTreeDepth %d")
    modelFilename = traits.Str(desc=" model file name given from user (not by xml  configuration file) ", argstr="--modelFilename %s")


class BRAINSCutOutputSpec(TraitedSpec):
    pass


class BRAINSCut(SlicerCommandLine):
    """title: BRAINSCut (BRAINS)

category: Segmentation.Specialized

description: Automatic Segmentation using neural networks

version:  1.0

license: https://www.nitrc.org/svn/brains/BuildScripts/trunk/License.txt

contributor: Vince Magnotta, Hans Johnson, Greg Harris, Kent Williams, Eunyoung Regina Kim

"""

    input_spec = BRAINSCutInputSpec
    output_spec = BRAINSCutOutputSpec
    _cmd = " BRAINSCut "
    _outputs_filenames = {}
