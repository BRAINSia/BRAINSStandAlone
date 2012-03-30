from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class VBRAINSDemonWarpInputSpec(CommandLineInputSpec):
    movingVolume = InputMultiPath(File(exists=True), argstr = "--movingVolume %s...")
    fixedVolume = InputMultiPath(File(exists=True), argstr = "--fixedVolume %s...")
    inputPixelType = traits.Enum("float","short","ushort","int","uchar", argstr = "--inputPixelType %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputVolume %s")
    outputDisplacementFieldVolume = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputDisplacementFieldVolume %s")
    outputPixelType = traits.Enum("float","short","ushort","int","uchar", argstr = "--outputPixelType %s")
    interpolationMode = traits.Enum("NearestNeighbor","Linear","ResampleInPlace","BSpline","WindowedSinc","Hamming","Cosine","Welch","Lanczos","Blackman", argstr = "--interpolationMode %s")
    registrationFilterType = traits.Enum("Demons","FastSymmetricForces","Diffeomorphic","LogDemons","SymmetricLogDemons", argstr = "--registrationFilterType %s")
    smoothDisplacementFieldSigma = traits.Float( argstr = "--smoothDisplacementFieldSigma %f")
    numberOfPyramidLevels = traits.Int( argstr = "--numberOfPyramidLevels %d")
    minimumFixedPyramid = InputMultiPath(traits.Int, sep = ",",argstr = "--minimumFixedPyramid %s")
    minimumMovingPyramid = InputMultiPath(traits.Int, sep = ",",argstr = "--minimumMovingPyramid %s")
    arrayOfPyramidLevelIterations = InputMultiPath(traits.Int, sep = ",",argstr = "--arrayOfPyramidLevelIterations %s")
    histogramMatch = traits.Bool( argstr = "--histogramMatch ")
    numberOfHistogramBins = traits.Int( argstr = "--numberOfHistogramBins %d")
    numberOfMatchPoints = traits.Int( argstr = "--numberOfMatchPoints %d")
    medianFilterSize = InputMultiPath(traits.Int, sep = ",",argstr = "--medianFilterSize %s")
    initializeWithDisplacementField = File( exists = True,argstr = "--initializeWithDisplacementField %s")
    initializeWithTransform = File( exists = True,argstr = "--initializeWithTransform %s")
    makeBOBF = traits.Bool( argstr = "--makeBOBF ")
    fixedBinaryVolume = File( exists = True,argstr = "--fixedBinaryVolume %s")
    movingBinaryVolume = File( exists = True,argstr = "--movingBinaryVolume %s")
    lowerThresholdForBOBF = traits.Int( argstr = "--lowerThresholdForBOBF %d")
    upperThresholdForBOBF = traits.Int( argstr = "--upperThresholdForBOBF %d")
    backgroundFillValue = traits.Int( argstr = "--backgroundFillValue %d")
    seedForBOBF = InputMultiPath(traits.Int, sep = ",",argstr = "--seedForBOBF %s")
    neighborhoodForBOBF = InputMultiPath(traits.Int, sep = ",",argstr = "--neighborhoodForBOBF %s")
    outputDisplacementFieldPrefix = traits.Str( argstr = "--outputDisplacementFieldPrefix %s")
    outputCheckerboardVolume = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputCheckerboardVolume %s")
    checkerboardPatternSubdivisions = InputMultiPath(traits.Int, sep = ",",argstr = "--checkerboardPatternSubdivisions %s")
    outputNormalized = traits.Bool( argstr = "--outputNormalized ")
    outputDebug = traits.Bool( argstr = "--outputDebug ")
    weightFactors = InputMultiPath(traits.Float, sep = ",",argstr = "--weightFactors %s")
    gradientType = traits.Enum("0","1","2", argstr = "--gradient_type %s")
    smoothingUp = traits.Float( argstr = "--upFieldSmoothing %f")
    maxStepLength = traits.Float( argstr = "--max_step_length %f")
    turnOffDiffeomorph = traits.Bool( argstr = "--use_vanilla_dem ")
    UseDebugImageViewer = traits.Bool( argstr = "--gui ")
    PromptAfterImageSend = traits.Bool( argstr = "--promptUser ")
    numberOfBCHApproximationTerms = traits.Int( argstr = "--numberOfBCHApproximationTerms %d")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")


class VBRAINSDemonWarpOutputSpec(TraitedSpec):
    outputVolume = File( exists = True)
    outputDisplacementFieldVolume = File( exists = True)
    outputCheckerboardVolume = File( exists = True)


class VBRAINSDemonWarp(CommandLine):

    input_spec = VBRAINSDemonWarpInputSpec
    output_spec = VBRAINSDemonWarpOutputSpec
    _cmd = " VBRAINSDemonWarp "
    _outputs_filenames = {'outputVolume':'outputVolume.nii','outputCheckerboardVolume':'outputCheckerboardVolume.nii','outputDisplacementFieldVolume':'outputDisplacementFieldVolume.nrrd'}

    def _list_outputs(self):
        outputs = self.output_spec().get()
        for name in outputs.keys():
            coresponding_input = getattr(self.inputs, name)
            if isdefined(coresponding_input):
                if isinstance(coresponding_input, bool) and coresponding_input == True:
                    outputs[name] = os.path.abspath(self._outputs_filenames[name])
                else:
                    if isinstance(coresponding_input, list):
                        outputs[name] = [os.path.abspath(inp) for inp in coresponding_input]
                    else:
                        outputs[name] = os.path.abspath(coresponding_input)
        return outputs

    def _format_arg(self, name, spec, value):
        if name in self._outputs_filenames.keys():
            if isinstance(value, bool):
                if value == True:
                    value = os.path.abspath(self._outputs_filenames[name])
                else:
                    return ""
        return super(VBRAINSDemonWarp, self)._format_arg(name, spec, value)

