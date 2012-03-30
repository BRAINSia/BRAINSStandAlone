from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class BRAINSConstellationModelerInputSpec(CommandLineInputSpec):
    verbose = traits.Bool( argstr = "--verbose ")
    inputTrainingList = File( exists = True,argstr = "--inputTrainingList %s")
    outputModel = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputModel %s")
    saveOptimizedLandmarks = traits.Bool( argstr = "--saveOptimizedLandmarks ")
    optimizedLandmarksFilenameExtender = traits.Str( argstr = "--optimizedLandmarksFilenameExtender %s")
    resultsDir = traits.Either(traits.Bool, Directory(), hash_files = False,argstr = "--resultsDir %s")
    mspQualityLevel = traits.Int( argstr = "--mspQualityLevel %d")
    rescaleIntensities = traits.Bool( argstr = "--rescaleIntensities ")
    trimRescaledIntensities = traits.Float( argstr = "--trimRescaledIntensities %f")
    rescaleIntensitiesOutputRange = InputMultiPath(traits.Int, sep = ",",argstr = "--rescaleIntensitiesOutputRange %s")
    backgroundFillValueString = traits.Str( argstr = "--BackgroundFillValue %s")
    writedebuggingImagesLevel = traits.Int( argstr = "--writedebuggingImagesLevel %d")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")


class BRAINSConstellationModelerOutputSpec(TraitedSpec):
    outputModel = File( exists = True)
    resultsDir = Directory( exists = True)


class BRAINSConstellationModeler(CommandLine):

    input_spec = BRAINSConstellationModelerInputSpec
    output_spec = BRAINSConstellationModelerOutputSpec
    _cmd = " BRAINSConstellationModeler "
    _outputs_filenames = {'outputModel':'outputModel.mdl','resultsDir':'resultsDir'}

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
        return super(BRAINSConstellationModeler, self)._format_arg(name, spec, value)

