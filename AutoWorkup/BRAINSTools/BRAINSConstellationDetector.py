from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSConstellationDetectorInputSpec(CommandLineInputSpec):
    houghEyeDetectorMode = traits.Int(desc=",                 This flag controls the mode of Hough eye detector.  By default, value of 1 is for T1W images, while the value of 0 is for T2W and PD images.,             ", argstr="--houghEyeDetectorMode %d")
    inputTemplateModel = File(desc="User-specified template model.,             ", exists=True, argstr="--inputTemplateModel %s")
    LLSModel = File(desc="Linear least squares model filename in HD5 format", exists=True, argstr="--LLSModel %s")
    inputVolume = File(desc="Input image in which to find ACPC points", exists=True, argstr="--inputVolume %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="ACPC-aligned output image with the same voxels, but updated origin, and direction cosign so that the AC point would fall at the physical location (0.0,0.0,0.0), and the mid-sagital plane is the plane where physical L/R coordinate is 0.0.", argstr="--outputVolume %s")
    outputResampledVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="ACPC-aligned output image in a resampled unifor space.  Currently this is a 1mm, 256^3, Identity direction image.", argstr="--outputResampledVolume %s")
    outputTransform = traits.Either(traits.Bool, File(), hash_files=False, desc="The filename for the original space to ACPC alignment to be written (in .mat format).,             ", argstr="--outputTransform %s")
    outputLandmarksInInputSpace = traits.Either(traits.Bool, File(), hash_files=False, desc=",               The filename for the new subject-specific landmark definition file in the same format produced by Slicer3 (.fcsv) with the landmarks in the original image space (the detected RP, AC, PC, and VN4) in it to be written.,             ", argstr="--outputLandmarksInInputSpace %s")
    outputLandmarksInACPCAlignedSpace = traits.Either(traits.Bool, File(), hash_files=False, desc=",               The filename for the new subject-specific landmark definition file in the same format produced by Slicer3 (.fcsv) with the landmarks in the output image space (the detected RP, AC, PC, and VN4) in it to be written.,             ", argstr="--outputLandmarksInACPCAlignedSpace %s")
    outputLandmarkWeights = traits.Either(traits.Bool, File(), hash_files=False, desc=",               The filename for the list of the landmarks and their correspond weight in (.wts) format.,             ", argstr="--outputLandmarkWeights %s")
    inputLandmarksPaired = File(desc=",               Paired use with outputLandmarks. It indicates the input landmark list filename (in a format of .fcsv) which contains the landmarks to be trainsformed to acpc-aligned space. The alignment transform will be calculated form the base landmarks provided, and then the rest of the landmarks are directly transformed to the acpc-aligned space rather than to estimate one by one.,             ", exists=True, argstr="--inputLandmarksPaired %s")
    outputLandmarksPaired = traits.Either(traits.Bool, File(), hash_files=False, desc=",               Paired use with inputLandmarks (in a format of .fcsv). It indicates the output acpc-aligned landmark list filename. The aligned landmarks are the landamrks that are defined in the file named inputLandmarks transformed by the acpc versor transform calculated by the constellation detector.,             ", argstr="--outputLandmarksPaired %s")
    outputMRML = traits.Either(traits.Bool, File(), hash_files=False, desc=",               The filename for the new subject-specific scene definition file in the same format produced by Slicer3 (in .mrml format). Only the components that were specified by the user on command line would be generated. Compatible components include inputVolume, outputVolume, outputLandmarksInInputSpace, outputLandmarksInACPCAlignedSpace, and outputTransform.,             ", argstr="--outputMRML %s")
    outputVerificationScript = traits.Either(traits.Bool, File(), hash_files=False, desc=",               The filename for the Slicer3 script that verifies the aligned landmarks against the aligned image file.  This will happen only in conjunction with saveOutputLandmarks and an outputVolume.,             ", argstr="--outputVerificationScript %s")
    mspQualityLevel = traits.Int(desc=",                 Flag cotrols how agressive the MSP is estimated. 0=quick estimate (9 seconds), 1=normal estimate (11 seconds), 2=great estimate (22 seconds), 3=best estimate (58 seconds), NOTE: -1= Prealigned so no estimate!.,             ", argstr="--mspQualityLevel %d")
    otsuPercentileThreshold = traits.Float(desc=",                 This is a parameter to FindLargestForegroundFilledMask, which is employed when acLowerBound is set and an outputUntransformedClippedVolume is requested.,             ", argstr="--otsuPercentileThreshold %f")
    acLowerBound = traits.Float(desc=",                 When generating a resampled output image, replace the image with the BackgroundFillValue everywhere below the plane This Far in physical units (millimeters) below (inferior to) the AC point (as found by the model.)  The oversize default was chosen to have no effect.  Based on visualizing a thousand masks in the IPIG study, we recommend a limit no smaller than 80.0 mm.,             ", argstr="--acLowerBound %f")
    cutOutHeadInOutputVolume = traits.Bool(desc=",                 Flag to cut out just the head tissue when producing an (un)transformed clipped volume.,             ", argstr="--cutOutHeadInOutputVolume ")
    outputUntransformedClippedVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="Output image in which to store neck-clipped input image, with the use of --acLowerBound and maybe --cutOutHeadInUntransformedVolume.", argstr="--outputUntransformedClippedVolume %s")
    rescaleIntensities = traits.Bool(desc=",                 Flag to turn on rescaling image intensities on input.,             ", argstr="--rescaleIntensities ")
    trimRescaledIntensities = traits.Float(desc=",                 Turn on clipping the rescaled image one-tailed on input.  Units of standard deviations above the mean.  Very large values are very permissive.  Non-positive value turns clipping off.  Defaults to removing 0.00001 of a normal tail above the mean.,             ", argstr="--trimRescaledIntensities %f")
    rescaleIntensitiesOutputRange = InputMultiPath(traits.Int, desc=",                 This pair of integers gives the lower and upper bounds on the signal portion of the output image.  Out-of-field voxels are taken from BackgroundFillValue.,             ", sep=",", argstr="--rescaleIntensitiesOutputRange %s")
    BackgroundFillValue = traits.Str(desc="Fill the background of image with specified short int value. Enter number or use BIGNEG for a large negative number.", argstr="--BackgroundFillValue %s")
    interpolationMode = traits.Enum("NearestNeighbor", "Linear", "ResampleInPlace", "BSpline", "WindowedSinc", "Hamming", "Cosine", "Welch", "Lanczos", "Blackman", desc="Type of interpolation to be used when applying transform to moving volume.  Options are Linear, ResampleInPlace, NearestNeighbor, BSpline, or WindowedSinc", argstr="--interpolationMode %s")
    forceACPoint = InputMultiPath(traits.Float, desc=",                 Use this flag to manually specify the AC point from the original image on the command line.,             ", sep=",", argstr="--forceACPoint %s")
    forcePCPoint = InputMultiPath(traits.Float, desc=",                 Use this flag to manually specify the PC point from the original image on the command line.,             ", sep=",", argstr="--forcePCPoint %s")
    forceVN4Point = InputMultiPath(traits.Float, desc=",                 Use this flag to manually specify the VN4 point from the original image on the command line.,             ", sep=",", argstr="--forceVN4Point %s")
    forceRPPoint = InputMultiPath(traits.Float, desc=",                 Use this flag to manually specify the RP point from the original image on the command line.,             ", sep=",", argstr="--forceRPPoint %s")
    inputLandmarksEMSP = File(desc=",               The filename for the new subject-specific landmark definition file in the same format produced by Slicer3 (in .fcsv) with the landmarks in the estimated MSP aligned space to be loaded. The detector will only process landmarks not enlisted on the file.,             ", exists=True, argstr="--inputLandmarksEMSP %s")
    forceHoughEyeDetectorReportFailure = traits.Bool(desc=",                 Flag indicates whether the Hough eye detector should report failure,             ", argstr="--forceHoughEyeDetectorReportFailure ")
    rmpj = traits.Float(desc=",               Search radius for MPJ in unit of mm,             ", argstr="--rmpj %f")
    rac = traits.Float(desc=",               Search radius for AC in unit of mm,             ", argstr="--rac %f")
    rpc = traits.Float(desc=",               Search radius for PC in unit of mm,             ", argstr="--rpc %f")
    rVN4 = traits.Float(desc=",               Search radius for VN4 in unit of mm,             ", argstr="--rVN4 %f")
    debug = traits.Bool(desc=",               Show internal debugging information.,             ", argstr="--debug ")
    verbose = traits.Bool(desc=",               Show more verbose output,             ", argstr="--verbose ")
    writeBranded2DImage = traits.Either(traits.Bool, File(), hash_files=False, desc=",               The filename for the 2D .png branded midline debugging image.  This will happen only in conjunction with requesting an outputVolume.,             ", argstr="--writeBranded2DImage %s")
    resultsDir = traits.Either(traits.Bool, Directory(), hash_files=False, desc=",               The directory for the debuging images to be written.,             ", argstr="--resultsDir %s")
    writedebuggingImagesLevel = traits.Int(desc=",                 This flag controls if debugging images are produced.  By default value of 0 is no images.  Anything greater than zero will be increasing level of debugging images.,             ", argstr="--writedebuggingImagesLevel %d")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class BRAINSConstellationDetectorOutputSpec(TraitedSpec):
    outputVolume = File(desc="ACPC-aligned output image with the same voxels, but updated origin, and direction cosign so that the AC point would fall at the physical location (0.0,0.0,0.0), and the mid-sagital plane is the plane where physical L/R coordinate is 0.0.", exists=True)
    outputResampledVolume = File(desc="ACPC-aligned output image in a resampled unifor space.  Currently this is a 1mm, 256^3, Identity direction image.", exists=True)
    outputTransform = File(desc="The filename for the original space to ACPC alignment to be written (in .mat format).,             ", exists=True)
    outputLandmarksInInputSpace = File(desc=",               The filename for the new subject-specific landmark definition file in the same format produced by Slicer3 (.fcsv) with the landmarks in the original image space (the detected RP, AC, PC, and VN4) in it to be written.,             ", exists=True)
    outputLandmarksInACPCAlignedSpace = File(desc=",               The filename for the new subject-specific landmark definition file in the same format produced by Slicer3 (.fcsv) with the landmarks in the output image space (the detected RP, AC, PC, and VN4) in it to be written.,             ", exists=True)
    outputLandmarkWeights = File(desc=",               The filename for the list of the landmarks and their correspond weight in (.wts) format.,             ", exists=True)
    outputLandmarksPaired = File(desc=",               Paired use with inputLandmarks (in a format of .fcsv). It indicates the output acpc-aligned landmark list filename. The aligned landmarks are the landamrks that are defined in the file named inputLandmarks transformed by the acpc versor transform calculated by the constellation detector.,             ", exists=True)
    outputMRML = File(desc=",               The filename for the new subject-specific scene definition file in the same format produced by Slicer3 (in .mrml format). Only the components that were specified by the user on command line would be generated. Compatible components include inputVolume, outputVolume, outputLandmarksInInputSpace, outputLandmarksInACPCAlignedSpace, and outputTransform.,             ", exists=True)
    outputVerificationScript = File(desc=",               The filename for the Slicer3 script that verifies the aligned landmarks against the aligned image file.  This will happen only in conjunction with saveOutputLandmarks and an outputVolume.,             ", exists=True)
    outputUntransformedClippedVolume = File(desc="Output image in which to store neck-clipped input image, with the use of --acLowerBound and maybe --cutOutHeadInUntransformedVolume.", exists=True)
    writeBranded2DImage = File(desc=",               The filename for the 2D .png branded midline debugging image.  This will happen only in conjunction with requesting an outputVolume.,             ", exists=True)
    resultsDir = Directory(desc=",               The directory for the debuging images to be written.,             ", exists=True)


class BRAINSConstellationDetector(SlicerCommandLine):
    """title: Brain Landmark Constellation Detector (BRAINS)

category: Segmentation.Specialized

description: 
    This program will find the mid-sagittal plane, a constellation of landmarks in a volume, and create an AC/PC aligned data set with the AC point at the center of the voxel lattice (labeled at the origin of the image physical space.)  Part of this work is an extention of the algorithms originally described by Dr. Babak A. Ardekani, Alvin H. Bachman, Model-based automatic detection of the anterior and posterior commissures on MRI scans, NeuroImage, Volume 46, Issue 3, 1 July 2009, Pages 677-682, ISSN 1053-8119, DOI: 10.1016/j.neuroimage.2009.02.030.  (http://www.sciencedirect.com/science/article/B6WNP-4VRP25C-4/2/8207b962a38aa83c822c6379bc43fe4c)
  

version: 1.0

documentation-url: http://www.nitrc.org/projects/brainscdetector/

"""

    input_spec = BRAINSConstellationDetectorInputSpec
    output_spec = BRAINSConstellationDetectorOutputSpec
    _cmd = " BRAINSConstellationDetector "
    _outputs_filenames = {'outputVolume':'outputVolume.nii.gz','outputResampledVolume':'outputResampledVolume.nii.gz','outputMRML':'outputMRML.mrml','outputLandmarksPaired':'outputLandmarksPaired.fcsv','resultsDir':'resultsDir','outputTransform':'outputTransform.mat','writeBranded2DImage':'writeBranded2DImage.png','outputLandmarksInACPCAlignedSpace':'outputLandmarksInACPCAlignedSpace.fcsv','outputLandmarksInInputSpace':'outputLandmarksInInputSpace.fcsv','outputLandmarkWeights':'outputLandmarkWeights.wts','outputUntransformedClippedVolume':'outputUntransformedClippedVolume.nii.gz','outputVerificationScript':'outputVerificationScript.sh'}
