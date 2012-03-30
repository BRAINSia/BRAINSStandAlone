from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class extractNrrdVectorIndexInputSpec(CommandLineInputSpec):
    inputVolume = File( exists = True,argstr = "--inputVolume %s")
    vectorIndex = traits.Int( argstr = "--vectorIndex %d")
    setImageOrientation = traits.Enum("AsAcquired","Axial","Coronal","Sagittal", argstr = "--setImageOrientation %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputVolume %s")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")


class extractNrrdVectorIndexOutputSpec(TraitedSpec):
    outputVolume = File( exists = True)


class extractNrrdVectorIndex(CommandLine):

    input_spec = extractNrrdVectorIndexInputSpec
    output_spec = extractNrrdVectorIndexOutputSpec
    _cmd = " extractNrrdVectorIndex "
    _outputs_filenames = {'outputVolume':'outputVolume.nii'}

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
        return super(extractNrrdVectorIndex, self)._format_arg(name, spec, value)

