from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSABCInputSpec(CommandLineInputSpec):
    inputVolumes = InputMultiPath(File(exists=True), desc="The list of input image files to be segmented.", argstr="--inputVolumes %s...")
    atlasDefinition = File(desc="Contains all parameters for Atlas", exists=True, argstr="--atlasDefinition %s")
    inputVolumeTypes = InputMultiPath(traits.Str, desc="The list of input image types corresponding to the inputVolumes.", sep=",", argstr="--inputVolumeTypes %s")
    outputDir = traits.Either(traits.Bool, Directory(), hash_files=False, desc="Ouput directory", argstr="--outputDir %s")
    atlasToSubjectTransformType = traits.Enum("ID", "Rigid", "Affine", "BSpline","SyN", desc=" What type of linear transform type do you want to use to register the atlas to the reference subject image.", argstr="--atlasToSubjectTransformType %s")
    atlasToSubjectTransform = traits.Either(traits.Bool, File(), hash_files=False, desc="The trasform from atlas to the subject", argstr="--atlasToSubjectTransform %s")
    atlasToSubjectInitialTransform = traits.Either(traits.Bool, File(), hash_files=False, desc="The initial trasform from atlas to the subject", argstr="--atlasToSubjectInitialTransform %s")
    subjectIntermodeTransformType = traits.Enum("ID", "Rigid", "Affine", "BSpline", desc=" What type of linear transform type do you want to use to register the atlas to the reference subject image.", argstr="--subjectIntermodeTransformType %s")
    outputVolumes = traits.Either(traits.Bool, InputMultiPath(File(), ), hash_files=False, desc="Corrected Output Images: should specify the same number of images as inputVolume, if only one element is given, then it is used as a file pattern where %s is replaced by the imageVolumeType, and %d by the index list location.", argstr="--outputVolumes %s...")
    outputLabels = traits.Either(traits.Bool, File(), hash_files=False, desc="Output Label Image", argstr="--outputLabels %s")
    outputDirtyLabels = traits.Either(traits.Bool, File(), hash_files=False, desc="Output Dirty Label Image", argstr="--outputDirtyLabels %s")
    posteriorTemplate = traits.Str(desc="filename template for Posterior output files", argstr="--posteriorTemplate %s")
    outputFormat = traits.Enum("NIFTI", "Meta", "Nrrd", desc="Output format", argstr="--outputFormat %s")
    interpolationMode = traits.Enum("BSpline", "NearestNeighbor", "WindowedSinc", "Linear", "ResampleInPlace", "Hamming", "Cosine", "Welch", "Lanczos", "Blackman", desc="Type of interpolation to be used when applying transform to moving volume.  Options are Linear, NearestNeighbor, BSpline, WindowedSinc, or ResampleInPlace.  The ResampleInPlace option will create an image with the same discrete voxel values and will adjust the origin and direction of the physical space interpretation.", argstr="--interpolationMode %s")
    maxIterations = traits.Int(desc="Filter iterations", argstr="--maxIterations %d")
    medianFilterSize = InputMultiPath(traits.Int, desc="The radius for the optional MedianImageFilter preprocessing in all 3 directions.", sep=",", argstr="--medianFilterSize %s")
    filterIteration = traits.Int(desc="Filter iterations", argstr="--filterIteration %d")
    filterTimeStep = traits.Float(desc="Filter time step should be less than (PixelSpacing/(1^(DIM+1)), value is set to negative, then allow automatic setting of this value. ", argstr="--filterTimeStep %f")
    filterMethod = traits.Enum("None", "CurvatureFlow", "GradientAnisotropicDiffusion", "Median", desc="Filter method for preprocessing of registration", argstr="--filterMethod %s")
    maxBiasDegree = traits.Int(desc="Maximum bias degree", argstr="--maxBiasDegree %d")
    atlasWarpingOff = traits.Bool(desc="Deformable registration of atlas to subject", argstr="--atlasWarpingOff ")
    gridSize = InputMultiPath(traits.Int, desc="Grid size for atlas warping with BSplines", sep=",", argstr="--gridSize %s")
    defaultSuffix = traits.Str(argstr="--defaultSuffix %s")
    implicitOutputs = traits.Either(traits.Bool, InputMultiPath(File(), ), hash_files=False, desc="Outputs to be made available to NiPype. Needed because not all BRAINSABC outputs have command line arguments.", argstr="--implicitOutputs %s...")
    debuglevel = traits.Int(desc="Display debug messages, and produce debug intermediate results.  0=OFF, 1=Minimal, 10=Maximum debugging.", argstr="--debuglevel %d")
    writeLess = traits.Bool(desc="Does not write posteriors and filtered, bias corrected images", argstr="--writeLess ")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class BRAINSABCOutputSpec(TraitedSpec):
    outputDir = Directory(desc="Ouput directory", exists=True)
    atlasToSubjectTransform = File(desc="The trasform from atlas to the subject", exists=True)
    atlasToSubjectInitialTransform = File(desc="The initial trasform from atlas to the subject", exists=True)
    outputVolumes = OutputMultiPath(File(exists=True), desc="Corrected Output Images: should specify the same number of images as inputVolume, if only one element is given, then it is used as a file pattern where %s is replaced by the imageVolumeType, and %d by the index list location.", exists=True)
    outputLabels = File(desc="Output Label Image", exists=True)
    outputDirtyLabels = File(desc="Output Dirty Label Image", exists=True)
    implicitOutputs = OutputMultiPath(File(exists=True), desc="Outputs to be made available to NiPype. Needed because not all BRAINSABC outputs have command line arguments.", exists=True)


class BRAINSABC(SlicerCommandLine):
    """title: Intra-subject registration, bias Correction, and tissue classification (BRAINS)

category: Segmentation.Specialized

description: Atlas-based tissue segmentation method.  This is an algorithmic extension of work done by XXXX at UNC and Utah XXXX need more description here.


"""

    input_spec = BRAINSABCInputSpec
    output_spec = BRAINSABCOutputSpec
    _cmd = " BRAINSABC "
    _outputs_filenames = {'outputLabels':'outputLabels.nii.gz','atlasToSubjectTransform':'atlasToSubjectTransform.mat','atlasToSubjectInitialTransform':'atlasToSubjectInitialTransform.mat','outputDirtyLabels':'outputDirtyLabels.nii.gz','outputVolumes':'outputVolumes.nii.gz','outputDir':'outputDir','implicitOutputs':'implicitOutputs.nii.gz'}
