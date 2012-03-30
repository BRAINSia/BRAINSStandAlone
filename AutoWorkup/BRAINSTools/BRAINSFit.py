from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class BRAINSFitInputSpec(CommandLineInputSpec):
    fixedVolume = File( exists = True,argstr = "--fixedVolume %s")
    movingVolume = File( exists = True,argstr = "--movingVolume %s")
    bsplineTransform = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--bsplineTransform %s")
    linearTransform = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--linearTransform %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputVolume %s")
    initialTransform = File( exists = True,argstr = "--initialTransform %s")
    initializeTransformMode = traits.Enum("Off","useMomentsAlign","useCenterOfHeadAlign","useGeometryAlign","useCenterOfROIAlign", argstr = "--initializeTransformMode %s")
    useRigid = traits.Bool( argstr = "--useRigid ")
    useScaleVersor3D = traits.Bool( argstr = "--useScaleVersor3D ")
    useScaleSkewVersor3D = traits.Bool( argstr = "--useScaleSkewVersor3D ")
    useAffine = traits.Bool( argstr = "--useAffine ")
    useBSpline = traits.Bool( argstr = "--useBSpline ")
    useComposite = traits.Bool( argstr = "--useComposite ")
    numberOfSamples = traits.Int( argstr = "--numberOfSamples %d")
    splineGridSize = InputMultiPath(traits.Int, sep = ",",argstr = "--splineGridSize %s")
    numberOfIterations = InputMultiPath(traits.Int, sep = ",",argstr = "--numberOfIterations %s")
    maskProcessingMode = traits.Enum("NOMASK","ROIAUTO","ROI", argstr = "--maskProcessingMode %s")
    fixedBinaryVolume = File( exists = True,argstr = "--fixedBinaryVolume %s")
    movingBinaryVolume = File( exists = True,argstr = "--movingBinaryVolume %s")
    outputFixedVolumeROI = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputFixedVolumeROI %s")
    outputMovingVolumeROI = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputMovingVolumeROI %s")
    outputVolumePixelType = traits.Enum("float","short","ushort","int","uint","uchar", argstr = "--outputVolumePixelType %s")
    backgroundFillValue = traits.Float( argstr = "--backgroundFillValue %f")
    maskInferiorCutOffFromCenter = traits.Float( argstr = "--maskInferiorCutOffFromCenter %f")
    scaleOutputValues = traits.Bool( argstr = "--scaleOutputValues ")
    interpolationMode = traits.Enum("NearestNeighbor","Linear","ResampleInPlace","BSpline","WindowedSinc","Hamming","Cosine","Welch","Lanczos","Blackman", argstr = "--interpolationMode %s")
    minimumStepLength = InputMultiPath(traits.Float, sep = ",",argstr = "--minimumStepLength %s")
    translationScale = traits.Float( argstr = "--translationScale %f")
    reproportionScale = traits.Float( argstr = "--reproportionScale %f")
    skewScale = traits.Float( argstr = "--skewScale %f")
    maxBSplineDisplacement = traits.Float( argstr = "--maxBSplineDisplacement %f")
    histogramMatch = traits.Bool( argstr = "--histogramMatch ")
    numberOfHistogramBins = traits.Int( argstr = "--numberOfHistogramBins %d")
    numberOfMatchPoints = traits.Int( argstr = "--numberOfMatchPoints %d")
    strippedOutputTransform = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--strippedOutputTransform %s")
    transformType = InputMultiPath(traits.Str, sep = ",",argstr = "--transformType %s")
    outputTransform = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputTransform %s")
    fixedVolumeTimeIndex = traits.Int( argstr = "--fixedVolumeTimeIndex %d")
    movingVolumeTimeIndex = traits.Int( argstr = "--movingVolumeTimeIndex %d")
    medianFilterSize = InputMultiPath(traits.Int, sep = ",",argstr = "--medianFilterSize %s")
    removeIntensityOutliers = traits.Float( argstr = "--removeIntensityOutliers %f")
    useCachingOfBSplineWeightsMode = traits.Enum("ON","OFF", argstr = "--useCachingOfBSplineWeightsMode %s")
    useExplicitPDFDerivativesMode = traits.Enum("AUTO","ON","OFF", argstr = "--useExplicitPDFDerivativesMode %s")
    ROIAutoDilateSize = traits.Float( argstr = "--ROIAutoDilateSize %f")
    ROIAutoClosingSize = traits.Float( argstr = "--ROIAutoClosingSize %f")
    relaxationFactor = traits.Float( argstr = "--relaxationFactor %f")
    maximumStepLength = traits.Float( argstr = "--maximumStepLength %f")
    failureExitCode = traits.Int( argstr = "--failureExitCode %d")
    writeTransformOnFailure = traits.Bool( argstr = "--writeTransformOnFailure ")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")
    forceMINumberOfThreads = traits.Int( argstr = "--forceMINumberOfThreads %d")
    debugLevel = traits.Int( argstr = "--debugLevel %d")
    costFunctionConvergenceFactor = traits.Float( argstr = "--costFunctionConvergenceFactor %f")
    projectedGradientTolerance = traits.Float( argstr = "--projectedGradientTolerance %f")
    UseDebugImageViewer = traits.Bool( argstr = "--gui ")
    PromptAfterImageSend = traits.Bool( argstr = "--promptUser ")
    useMomentsAlign = traits.Bool( argstr = "--NEVER_USE_THIS_FLAG_IT_IS_OUTDATED_00 ")
    useGeometryAlign = traits.Bool( argstr = "--NEVER_USE_THIS_FLAG_IT_IS_OUTDATED_01 ")
    useCenterOfHeadAlign = traits.Bool( argstr = "--NEVER_USE_THIS_FLAG_IT_IS_OUTDATED_02 ")
    permitParameterVariation = InputMultiPath(traits.Int, sep = ",",argstr = "--permitParameterVariation %s")
    costMetric = traits.Enum("MMI","MSE","NC","MC", argstr = "--costMetric %s")


class BRAINSFitOutputSpec(TraitedSpec):
    bsplineTransform = File( exists = True)
    linearTransform = File( exists = True)
    outputVolume = File( exists = True)
    outputFixedVolumeROI = File( exists = True)
    outputMovingVolumeROI = File( exists = True)
    strippedOutputTransform = File( exists = True)
    outputTransform = File( exists = True)


class BRAINSFit(CommandLine):

    input_spec = BRAINSFitInputSpec
    output_spec = BRAINSFitOutputSpec
    _cmd = " BRAINSFit "
    _outputs_filenames = {'outputVolume':'outputVolume.nii','bsplineTransform':'bsplineTransform.mat','outputTransform':'outputTransform.mat','outputFixedVolumeROI':'outputFixedVolumeROI.nii','strippedOutputTransform':'strippedOutputTransform.mat','outputMovingVolumeROI':'outputMovingVolumeROI.nii','linearTransform':'linearTransform.mat'}

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
        return super(BRAINSFit, self)._format_arg(name, spec, value)

