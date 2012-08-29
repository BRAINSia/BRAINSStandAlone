from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSMushInputSpec(CommandLineInputSpec):
    inputFirstVolume = File(desc="Input image (1) for mixture optimization", exists=True, argstr="--inputFirstVolume %s")
    inputSecondVolume = File(desc="Input image (2) for mixture optimization", exists=True, argstr="--inputSecondVolume %s")
    inputMaskVolume = File(desc="Input label image for mixture optimization", exists=True, argstr="--inputMaskVolume %s")
    outputWeightsFile = traits.Either(traits.Bool, File(), hash_files=False, desc="Output Weights File", argstr="--outputWeightsFile %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="The MUSH image produced from the T1 and T2 weighted images", argstr="--outputVolume %s")
    outputMask = traits.Either(traits.Bool, File(), hash_files=False, desc="The brain volume mask generated from the MUSH image", argstr="--outputMask %s")
    seed = InputMultiPath(traits.Int, desc="Seed Point for Brain Region Filling", sep=",", argstr="--seed %s")
    desiredMean = traits.Float(desc="Desired mean within the mask for weighted sum of both images.", argstr="--desiredMean %f")
    desiredVariance = traits.Float(desc="Desired variance within the mask for weighted sum of both images.", argstr="--desiredVariance %f")
    lowerThresholdFactorPre = traits.Float(desc="Lower threshold factor for finding an initial brain mask", argstr="--lowerThresholdFactorPre %f")
    upperThresholdFactorPre = traits.Float(desc="Upper threshold factor for finding an initial brain mask", argstr="--upperThresholdFactorPre %f")
    lowerThresholdFactor = traits.Float(desc="Lower threshold factor for defining the brain mask", argstr="--lowerThresholdFactor %f")
    upperThresholdFactor = traits.Float(desc="Upper threshold factor for defining the brain mask", argstr="--upperThresholdFactor %f")
    boundingBoxSize = InputMultiPath(traits.Int, desc="Size of the cubic bounding box mask used when no brain mask is present", sep=",", argstr="--boundingBoxSize %s")
    boundingBoxStart = InputMultiPath(traits.Int, desc="XYZ point-coordinate for the start of the cubic bounding box mask used when no brain mask is present", sep=",", argstr="--boundingBoxStart %s")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class BRAINSMushOutputSpec(TraitedSpec):
    outputWeightsFile = File(desc="Output Weights File", exists=True)
    outputVolume = File(desc="The MUSH image produced from the T1 and T2 weighted images", exists=True)
    outputMask = File(desc="The brain volume mask generated from the MUSH image", exists=True)


class BRAINSMush(SlicerCommandLine):
    """title:  Brain Extraction from T1/T2 image (BRAINS)

category: Utilities.BRAINS

description:
  This program: 1) generates a weighted mixture image optimizing the mean and variance and 2) produces a mask of the brain volume


version: 0.1.0.$Revision: 1.4 $(alpha)

documentation-url: http:://mri.radiology.uiowa.edu

license: https://www.nitrc.org/svn/brains/BuildScripts/trunk/License.txt

contributor:
  This tool is a modification by Steven Dunn of a program developed by Greg Harris and Ron Pierson.


acknowledgements:
  This work was developed by the University of Iowa Departments of Radiology and Psychiatry. This software was supported in part of NIH/NINDS award NS050568.


"""

    input_spec = BRAINSMushInputSpec
    output_spec = BRAINSMushOutputSpec
    _cmd = " BRAINSMush "
    _outputs_filenames = {'outputMask':'outputMask.nii.gz','outputWeightsFile':'outputWeightsFile.txt','outputVolume':'outputVolume.nii.gz'}
