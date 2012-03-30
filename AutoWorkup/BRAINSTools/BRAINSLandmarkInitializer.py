from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class BRAINSLandmarkInitializerInputSpec(CommandLineInputSpec):
    inputFixedLandmarkFilename = File( exists = True,argstr = "--inputFixedLandmarkFilename %s")
    inputMovingLandmarkFilename = File( exists = True,argstr = "--inputMovingLandmarkFilename %s")
    inputWeightFilename = File( exists = True,argstr = "--inputWeightFilename %s")
    outputTransformFilename = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputTransformFilename %s")


class BRAINSLandmarkInitializerOutputSpec(TraitedSpec):
    outputTransformFilename = File( exists = True)


class BRAINSLandmarkInitializer(CommandLine):

    input_spec = BRAINSLandmarkInitializerInputSpec
    output_spec = BRAINSLandmarkInitializerOutputSpec
    _cmd = " BRAINSLandmarkInitializer "
    _outputs_filenames = {'outputTransformFilename':'outputTransformFilename'}

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
        return super(BRAINSLandmarkInitializer, self)._format_arg(name, spec, value)

