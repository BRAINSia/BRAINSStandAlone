from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class gtractInvertBSplineTransformInputSpec(CommandLineInputSpec):
    inputReferenceVolume = File( exists = True,argstr = "--inputReferenceVolume %s")
    inputTransform = File( exists = True,argstr = "--inputTransform %s")
    outputTransform = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputTransform %s")
    landmarkDensity = InputMultiPath(traits.Int, sep = ",",argstr = "--landmarkDensity %s")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")


class gtractInvertBSplineTransformOutputSpec(TraitedSpec):
    outputTransform = File( exists = True)


class gtractInvertBSplineTransform(CommandLine):

    input_spec = gtractInvertBSplineTransformInputSpec
    output_spec = gtractInvertBSplineTransformOutputSpec
    _cmd = " gtractInvertBSplineTransform "
    _outputs_filenames = {'outputTransform':'outputTransform.mat'}

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
        return super(gtractInvertBSplineTransform, self)._format_arg(name, spec, value)

