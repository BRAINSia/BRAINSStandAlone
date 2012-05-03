from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSInitializedControlPointsInputSpec(CommandLineInputSpec):
    inputVolume = File(desc="Input Volume", exists=True, argstr="--inputVolume %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="Output Volume", argstr="--outputVolume %s")
    splineGridSize = InputMultiPath(traits.Int, desc="The number of subdivisions of the BSpline Grid to be centered on the image space.  Each dimension must have at least 3 subdivisions for the BSpline to be correctly computed. ", sep=",", argstr="--splineGridSize %s")
    permuteOrder = InputMultiPath(traits.Int, desc="The permutation order for the images.  The default is 0,1,2 (i.e. no permutation)", sep=",", argstr="--permuteOrder %s")
    outputLandmarksFile = traits.Str(desc="Output filename", argstr="--outputLandmarksFile %s")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class BRAINSInitializedControlPointsOutputSpec(TraitedSpec):
    outputVolume = File(desc="Output Volume", exists=True)


class BRAINSInitializedControlPoints(SlicerCommandLine):
    """title: Initialized Control Points (BRAINS)

category:  Utilities.BRAINS 

description: 
  Outputs bspline control points as landmarks
  

version: 0.1.0.$Revision: 916 $(alpha)

license: https://www.nitrc.org/svn/brains/BuildScripts/trunk/License.txt 

contributor: Mark Scully

acknowledgements: 
This work is part of the National Alliance for Medical Image Computing (NAMIC), funded by the National Institutes of Health through the NIH Roadmap for Medical Research, Grant U54 EB005149.  Additional support for Mark Scully and Hans Johnson at the University of Iowa.


"""

    input_spec = BRAINSInitializedControlPointsInputSpec
    output_spec = BRAINSInitializedControlPointsOutputSpec
    _cmd = " BRAINSInitializedControlPoints "
    _outputs_filenames = {'outputVolume':'outputVolume.nii'}
