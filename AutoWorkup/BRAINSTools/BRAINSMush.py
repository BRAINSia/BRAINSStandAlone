from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class BRAINSMushInputSpec(CommandLineInputSpec):
    inputFirstVolume = File( exists = True,argstr = "--inputFirstVolume %s")
    inputSecondVolume = File( exists = True,argstr = "--inputSecondVolume %s")
    inputMaskVolume = File( exists = True,argstr = "--inputMaskVolume %s")
    outputWeightsFile = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputWeightsFile %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputVolume %s")
    outputMask = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputMask %s")
    seed = InputMultiPath(traits.Int, sep = ",",argstr = "--seed %s")
    desiredMean = traits.Float( argstr = "--desiredMean %f")
    desiredVariance = traits.Float( argstr = "--desiredVariance %f")
    lowerThresholdFactorPre = traits.Float( argstr = "--lowerThresholdFactorPre %f")
    upperThresholdFactorPre = traits.Float( argstr = "--upperThresholdFactorPre %f")
    lowerThresholdFactor = traits.Float( argstr = "--lowerThresholdFactor %f")
    upperThresholdFactor = traits.Float( argstr = "--upperThresholdFactor %f")
    boundingBoxSize = InputMultiPath(traits.Int, sep = ",",argstr = "--boundingBoxSize %s")
    boundingBoxStart = InputMultiPath(traits.Int, sep = ",",argstr = "--boundingBoxStart %s")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")


class BRAINSMushOutputSpec(TraitedSpec):
    outputWeightsFile = File( exists = True)
    outputVolume = File( exists = True)
    outputMask = File( exists = True)


class BRAINSMush(CommandLine):

    input_spec = BRAINSMushInputSpec
    output_spec = BRAINSMushOutputSpec
    _cmd = " BRAINSMush "
    _outputs_filenames = {'outputMask':'outputMask.nii.gz','outputWeightsFile':'outputWeightsFile.txt','outputVolume':'outputVolume.nii.gz'}

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
        return super(BRAINSMush, self)._format_arg(name, spec, value)

