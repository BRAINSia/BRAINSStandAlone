from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class gtractInvertDeformationFieldInputSpec(CommandLineInputSpec):
    baseImage = File( exists = True,argstr = "--baseImage %s")
    deformationImage = File( exists = True,argstr = "--deformationImage %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputVolume %s")
    subsamplingFactor = traits.Int( argstr = "--subsamplingFactor %d")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")


class gtractInvertDeformationFieldOutputSpec(TraitedSpec):
    outputVolume = File( exists = True)


class gtractInvertDeformationField(CommandLine):

    input_spec = gtractInvertDeformationFieldInputSpec
    output_spec = gtractInvertDeformationFieldOutputSpec
    _cmd = " gtractInvertDeformationField "
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
        return super(gtractInvertDeformationField, self)._format_arg(name, spec, value)

