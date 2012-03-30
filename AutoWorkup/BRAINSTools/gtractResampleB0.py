from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class gtractResampleB0InputSpec(CommandLineInputSpec):
    inputVolume = File( exists = True,argstr = "--inputVolume %s")
    inputAnatomicalVolume = File( exists = True,argstr = "--inputAnatomicalVolume %s")
    inputTransform = File( exists = True,argstr = "--inputTransform %s")
    vectorIndex = traits.Int( argstr = "--vectorIndex %d")
    transformType = traits.Enum("Rigid","B-Spline", argstr = "--transformType %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputVolume %s")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")


class gtractResampleB0OutputSpec(TraitedSpec):
    outputVolume = File( exists = True)


class gtractResampleB0(CommandLine):

    input_spec = gtractResampleB0InputSpec
    output_spec = gtractResampleB0OutputSpec
    _cmd = " gtractResampleB0 "
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
        return super(gtractResampleB0, self)._format_arg(name, spec, value)

