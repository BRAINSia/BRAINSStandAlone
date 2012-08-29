from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class GradientAnisotropicDiffusionImageFilterInputSpec(CommandLineInputSpec):
    inputVolume = File(desc="Required: input image", exists=True, argstr="--inputVolume %s")
    numberOfIterations = traits.Int(desc="Optional value for number of Iterations", argstr="--numberOfIterations %d")
    timeStep = traits.Float(desc="Time step for diffusion process", argstr="--timeStep %f")
    conductance = traits.Float(desc="Conductance for diffusion process", argstr="--conductance %f")
    outputVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="Required: output image", argstr="--outputVolume %s")


class GradientAnisotropicDiffusionImageFilterOutputSpec(TraitedSpec):
    outputVolume = File(desc="Required: output image", exists=True)


class GradientAnisotropicDiffusionImageFilter(SlicerCommandLine):
    """title: GradientAnisopropicDiffusionFilter

category: Filtering.FeatureDetection

description:  Image Smoothing using Gradient Anisotropic Diffuesion Filer

contributor:  This tool was developed by Eun Young Kim by modifying ITK Example

"""

    input_spec = GradientAnisotropicDiffusionImageFilterInputSpec
    output_spec = GradientAnisotropicDiffusionImageFilterOutputSpec
    _cmd = " GradientAnisotropicDiffusionImageFilter "
    _outputs_filenames = {'outputVolume':'outputVolume.nii'}
