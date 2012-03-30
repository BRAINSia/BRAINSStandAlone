from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class gtractCostFastMarchingInputSpec(CommandLineInputSpec):
    inputTensorVolume = File( exists = True,argstr = "--inputTensorVolume %s")
    inputAnisotropyVolume = File( exists = True,argstr = "--inputAnisotropyVolume %s")
    inputStartingSeedsLabelMapVolume = File( exists = True,argstr = "--inputStartingSeedsLabelMapVolume %s")
    startingSeedsLabel = traits.Int( argstr = "--startingSeedsLabel %d")
    outputCostVolume = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputCostVolume %s")
    outputSpeedVolume = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputSpeedVolume %s")
    anisotropyWeight = traits.Float( argstr = "--anisotropyWeight %f")
    stoppingValue = traits.Float( argstr = "--stoppingValue %f")
    seedThreshold = traits.Float( argstr = "--seedThreshold %f")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")


class gtractCostFastMarchingOutputSpec(TraitedSpec):
    outputCostVolume = File( exists = True)
    outputSpeedVolume = File( exists = True)


class gtractCostFastMarching(CommandLine):

    input_spec = gtractCostFastMarchingInputSpec
    output_spec = gtractCostFastMarchingOutputSpec
    _cmd = " gtractCostFastMarching "
    _outputs_filenames = {'outputCostVolume':'outputCostVolume.nrrd','outputSpeedVolume':'outputSpeedVolume.nrrd'}

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
        return super(gtractCostFastMarching, self)._format_arg(name, spec, value)

