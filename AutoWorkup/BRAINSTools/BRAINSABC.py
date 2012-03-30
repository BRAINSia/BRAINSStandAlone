from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class BRAINSABCInputSpec(CommandLineInputSpec):
    inputVolumes = InputMultiPath(File(exists=True), argstr = "--inputVolumes %s...")
    atlasDefinition = File( exists = True,argstr = "--atlasDefinition %s")
    inputVolumeTypes = InputMultiPath(traits.Str, sep = ",",argstr = "--inputVolumeTypes %s")
    outputDir = traits.Either(traits.Bool, Directory(), hash_files = False,argstr = "--outputDir %s")
    atlasToSubjectTransformType = traits.Enum("ID","Rigid","Affine","BSpline", argstr = "--atlasToSubjectTransformType %s")
    atlasToSubjectTransform = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--atlasToSubjectTransform %s")
    atlasToSubjectInitialTransform = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--atlasToSubjectInitialTransform %s")
    subjectIntermodeTransformType = traits.Enum("ID","Rigid","Affine","BSpline", argstr = "--subjectIntermodeTransformType %s")
    outputVolumes = traits.Either(traits.Bool, InputMultiPath(File(),), hash_files = False,argstr = "--outputVolumes %s...")
    outputLabels = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputLabels %s")
    outputDirtyLabels = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputDirtyLabels %s")
    posteriorTemplate = traits.Str( argstr = "--posteriorTemplate %s")
    outputFormat = traits.Enum("NIFTI","Meta","Nrrd", argstr = "--outputFormat %s")
    resamplerInterpolatorType = traits.Enum("BSpline","NearestNeighbor","WindowedSinc","Linear","ResampleInPlace","Hamming","Cosine","Welch","Lanczos","Blackman", argstr = "--interpolationMode %s")
    maxIterations = traits.Int( argstr = "--maxIterations %d")
    medianFilterSize = InputMultiPath(traits.Int, sep = ",",argstr = "--medianFilterSize %s")
    filterIteration = traits.Int( argstr = "--filterIteration %d")
    filterTimeStep = traits.Float( argstr = "--filterTimeStep %f")
    filterMethod = traits.Enum("None","CurvatureFlow","GradientAnisotropicDiffusion","Median", argstr = "--filterMethod %s")
    maxBiasDegree = traits.Int( argstr = "--maxBiasDegree %d")
    atlasWarpingOff = traits.Bool( argstr = "--atlasWarpingOff ")
    gridSize = InputMultiPath(traits.Int, sep = ",",argstr = "--gridSize %s")
    defaultSuffix = traits.Str( argstr = "--defaultSuffix %s")
    implicitOutputs = traits.Either(traits.Bool, InputMultiPath(File(),), hash_files = False,argstr = "--implicitOutputs %s...")
    debuglevel = traits.Int( argstr = "--debuglevel %d")
    writeLess = traits.Bool( argstr = "--writeLess ")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")


class BRAINSABCOutputSpec(TraitedSpec):
    outputDir = Directory( exists = True)
    atlasToSubjectTransform = File( exists = True)
    atlasToSubjectInitialTransform = File( exists = True)
    outputVolumes = OutputMultiPath(File(exists=True), exists = True)
    outputLabels = File( exists = True)
    outputDirtyLabels = File( exists = True)
    implicitOutputs = OutputMultiPath(File(exists=True), exists = True)


class BRAINSABC(CommandLine):

    input_spec = BRAINSABCInputSpec
    output_spec = BRAINSABCOutputSpec
    _cmd = " BRAINSABC "
    _outputs_filenames = {'outputLabels':'outputLabels.nii.gz','atlasToSubjectTransform':'atlasToSubjectTransform.mat','atlasToSubjectInitialTransform':'atlasToSubjectInitialTransform.mat','outputDirtyLabels':'outputDirtyLabels.nii.gz','outputVolumes':'outputVolumes.nii.gz','outputDir':'outputDir','implicitOutputs':'implicitOutputs.nii.gz'}

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
        return super(BRAINSABC, self)._format_arg(name, spec, value)

