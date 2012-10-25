from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSSnapShotWriterInputSpec(CommandLineInputSpec):
    inputVolumes = File(desc="Images to be captured", exists=True, argstr="--inputVolumes %s")  ## check how to set multiple input
    inputBinaryVolumes = File(desc="Binary images to be overlapped on top of inputVolumes", exists=False, argstr="--inputBinaryVolumes %s")  ## check how to set multiple input
    inputPlaneDirection = InputMultiPath(traits.Int, desc="Plane to display. In general, 0=saggital, 1=coronal, and 2=axial plane. (default: 0,1,2)", argstr="inputPlaneDirection %s")
    inputSliceToExtractInPercent = InputMultiPath(traits.Int, desc="2D slice number of input images. Percentage input from 0%-100%. (default: 50,50,50)", argstr="inputSliceToExtractInPercent %s")
    inputSliceToExtractInIndex = InputMultiPath(traits.Int, desc="2D slice number of input images. For autoWorkUp output, which AC-PC aligned, 0,0,0 will be the center.", argstr="inputSliceToExtractInIndex %s")
    inputSliceToExtractInPhysicalPoint = = InputMultiPath(traits.Float, desc="Input mask (binary) volume list to be extracted as 2D image. Multiple input is possible.", argstr="inputSliceToExtractInPhysicalPoint %s")

class BRAINSSnapShotWriterOutputSpec(TraitedSpec):
    outputFilename = File(desc="Resulting screen shots (*png)", exists=True)


class BRAINSSnapShotWriter(SlicerCommandLine):
    """title: Snap Shot Writer (BRAINS)

category: Utilities 

description:


version: 1.0.0

documentation-url: http://www.slicer.org/slicerWiki/index.php/Documentation/4.1/Modules/BRAINSSnapShotWriter

license: https://www.nitrc.org/svn/brains/BuildScripts/trunk/License.txt

contributor: This tool was developed by Eun Young (Regina) Kim

acknowledgements: The development of this tool was supported by funding from grants NS050568 and NS40068 from the National Institute of Neurological Disorders and Stroke and grants MH31593, MH40856, from the National Institute of Mental Health.

"""

    input_spec = BRAINSSnapShotWriterInputSpec
    output_spec = BRAINSSnapShotWriterOutputSpec
    _cmd = " BRAINSSnapShotWriter "
    _outputs_filenames = {'outputImage':'outputImage.png'}
