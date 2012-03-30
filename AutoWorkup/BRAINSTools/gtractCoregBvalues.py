from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class gtractCoregBvaluesInputSpec(CommandLineInputSpec):
    movingVolume = File( exists = True,argstr = "--movingVolume %s")
    fixedVolume = File( exists = True,argstr = "--fixedVolume %s")
    fixedVolumeIndex = traits.Int( argstr = "--fixedVolumeIndex %d")
    outputVolume = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputVolume %s")
    outputTransform = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputTransform %s")
    eddyCurrentCorrection = traits.Bool( argstr = "--eddyCurrentCorrection ")
    numberOfIterations = traits.Int( argstr = "--numberOfIterations %d")
    numberOfSpatialSamples = traits.Int( argstr = "--numberOfSpatialSamples %d")
    relaxationFactor = traits.Float( argstr = "--relaxationFactor %f")
    maximumStepSize = traits.Float( argstr = "--maximumStepSize %f")
    minimumStepSize = traits.Float( argstr = "--minimumStepSize %f")
    spatialScale = traits.Float( argstr = "--spatialScale %f")
    registerB0Only = traits.Bool( argstr = "--registerB0Only ")
    debugLevel = traits.Int( argstr = "--debugLevel %d")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")


class gtractCoregBvaluesOutputSpec(TraitedSpec):
    outputVolume = File( exists = True)
    outputTransform = File( exists = True)


class gtractCoregBvalues(CommandLine):

    input_spec = gtractCoregBvaluesInputSpec
    output_spec = gtractCoregBvaluesOutputSpec
    _cmd = " gtractCoregBvalues "
    _outputs_filenames = {'outputVolume':'outputVolume.nrrd','outputTransform':'outputTransform.mat'}

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
        return super(gtractCoregBvalues, self)._format_arg(name, spec, value)

