from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class BRAINSCutInputSpec(CommandLineInputSpec):
    netConfiguration = File( exists = True,argstr = "--netConfiguration %s")
    trainModelStartIndex = traits.Int( argstr = "--trainModelStartIndex %d")
    verbose = traits.Int( argstr = "--verbose %d")
    multiStructureThreshold = traits.Bool( argstr = "--multiStructureThreshold ")
    histogramEqualization = traits.Bool( argstr = "--histogramEqualization ")
    computeSSEOn = traits.Bool( argstr = "--computeSSEOn ")
    generateProbability = traits.Bool( argstr = "--generateProbability ")
    createVectors = traits.Bool( argstr = "--createVectors ")
    trainModel = traits.Bool( argstr = "--trainModel ")
    applyModel = traits.Bool( argstr = "--applyModel ")
    validate = traits.Bool( argstr = "--validate ")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")
    implicitOutputs = traits.Either(traits.Bool, InputMultiPath(File(),), hash_files = False,argstr = "--implicitOutputs %s...")


class BRAINSCutOutputSpec(TraitedSpec):
    implicitOutputs = OutputMultiPath(File(exists=True), exists = True)


class BRAINSCut(CommandLine):

    input_spec = BRAINSCutInputSpec
    output_spec = BRAINSCutOutputSpec
    _cmd = " BRAINSCut "
    _outputs_filenames = {'implicitOutputs':'implicitOutputs.nii.gz'}

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
        return super(BRAINSCut, self)._format_arg(name, spec, value)

