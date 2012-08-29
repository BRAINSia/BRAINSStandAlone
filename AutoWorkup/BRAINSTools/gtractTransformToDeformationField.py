from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class gtractTransformToDeformationFieldInputSpec(CommandLineInputSpec):
    inputTransform = File( exists = True,argstr = "--inputTransform %s")
    inputReferenceVolume = File( exists = True,argstr = "--inputReferenceVolume %s")
    outputDeformationFieldVolume = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputDeformationFieldVolume %s")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")


class gtractTransformToDeformationFieldOutputSpec(TraitedSpec):
    outputDeformationFieldVolume = File( exists = True)


class gtractTransformToDeformationField(CommandLine):

    input_spec = gtractTransformToDeformationFieldInputSpec
    output_spec = gtractTransformToDeformationFieldOutputSpec
    _cmd = " gtractTransformToDeformationField "
    _outputs_filenames = {'outputDeformationFieldVolume':'outputDeformationFieldVolume.nii'}

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
        return super(gtractTransformToDeformationField, self)._format_arg(name, spec, value)
