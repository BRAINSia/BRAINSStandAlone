from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class BRAINSLmkTransformInputSpec(CommandLineInputSpec):
    inputMovingLandmarks = File( exists = True,argstr = "--inputMovingLandmarks %s")
    inputFixedLandmarks = File( exists = True,argstr = "--inputFixedLandmarks %s")
    outputAffineTransform = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputAffineTransform %s")
    inputMovingVolume = File( exists = True,argstr = "--inputMovingVolume %s")
    inputReferenceVolume = File( exists = True,argstr = "--inputReferenceVolume %s")
    outputResampledVolume = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputResampledVolume %s")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")


class BRAINSLmkTransformOutputSpec(TraitedSpec):
    outputAffineTransform = File( exists = True)
    outputResampledVolume = File( exists = True)


class BRAINSLmkTransform(CommandLine):

    input_spec = BRAINSLmkTransformInputSpec
    output_spec = BRAINSLmkTransformOutputSpec
    _cmd = " BRAINSLmkTransform "
    _outputs_filenames = {'outputResampledVolume':'outputResampledVolume.nii','outputAffineTransform':'outputAffineTransform.mat'}

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
        return super(BRAINSLmkTransform, self)._format_arg(name, spec, value)

