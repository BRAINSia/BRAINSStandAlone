from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class gtractTensorInputSpec(CommandLineInputSpec):
    inputVolume = File( exists = True,argstr = "--inputVolume %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputVolume %s")
    medianFilterSize = InputMultiPath(traits.Int, sep = ",",argstr = "--medianFilterSize %s")
    maskProcessingMode = traits.Enum("NOMASK","ROIAUTO","ROI", argstr = "--maskProcessingMode %s")
    maskVolume = File( exists = True,argstr = "--maskVolume %s")
    backgroundSuppressingThreshold = traits.Int( argstr = "--backgroundSuppressingThreshold %d")
    resampleIsotropic = traits.Bool( argstr = "--resampleIsotropic ")
    voxelSize = traits.Float( argstr = "--size %f")
    b0Index = traits.Int( argstr = "--b0Index %d")
    applyMeasurementFrame = traits.Bool( argstr = "--applyMeasurementFrame ")
    ignoreIndex = InputMultiPath(traits.Int, sep = ",",argstr = "--ignoreIndex %s")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")


class gtractTensorOutputSpec(TraitedSpec):
    outputVolume = File( exists = True)


class gtractTensor(CommandLine):

    input_spec = gtractTensorInputSpec
    output_spec = gtractTensorOutputSpec
    _cmd = " gtractTensor "
    _outputs_filenames = {'outputVolume':'outputVolume.nrrd'}

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
        return super(gtractTensor, self)._format_arg(name, spec, value)

