from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSMultiModeSegmentInputSpec(CommandLineInputSpec):
    inputVolumes = InputMultiPath(File(exists=True), desc="The input image volumes for finding the largest region filled mask.", argstr="--inputVolumes %s...")
    inputMaskVolume = File(desc="The ROI for region to compute histogram levels.", exists=True, argstr="--inputMaskVolume %s")
    outputROIMaskVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="The ROI automatically found from the input image.", argstr="--outputROIMaskVolume %s")
    outputClippedVolumeROI = traits.Either(traits.Bool, File(), hash_files=False, desc="The inputVolume clipped to the region of the brain mask.", argstr="--outputClippedVolumeROI %s")
    lowerThreshold = InputMultiPath(traits.Float, desc="Lower thresholds on the valid histogram regions for each modality", sep=",", argstr="--lowerThreshold %s")
    upperThreshold = InputMultiPath(traits.Float, desc="Upper thresholds on the valid histogram regions for each modality", sep=",", argstr="--upperThreshold %s")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class BRAINSMultiModeSegmentOutputSpec(TraitedSpec):
    outputROIMaskVolume = File(desc="The ROI automatically found from the input image.", exists=True)
    outputClippedVolumeROI = File(desc="The inputVolume clipped to the region of the brain mask.", exists=True)


class BRAINSMultiModeSegment(SlicerCommandLine):
    """title: Segment based on rectangular region of joint histogram (BRAINS)

category: Utilities.BRAINS

description: This tool creates binary regions based on segmenting multiple image modalitities at once.
  

version: 2.4.1

license: https://www.nitrc.org/svn/brains/BuildScripts/trunk/License.txt 

contributor: Hans J. Johnson, hans-johnson -at- uiowa.edu, http://www.psychiatry.uiowa.edu

acknowledgements: Hans Johnson(1,3,4); Gregory Harris(1), Vincent Magnotta(1,2,3);   (1=University of Iowa Department of Psychiatry, 2=University of Iowa Department of Radiology, 3=University of Iowa Department of Biomedical Engineering, 4=University of Iowa Department of Electrical and Computer Engineering)  

"""

    input_spec = BRAINSMultiModeSegmentInputSpec
    output_spec = BRAINSMultiModeSegmentOutputSpec
    _cmd = " BRAINSMultiModeSegment "
    _outputs_filenames = {'outputROIMaskVolume':'outputROIMaskVolume.nii','outputClippedVolumeROI':'outputClippedVolumeROI.nii'}
