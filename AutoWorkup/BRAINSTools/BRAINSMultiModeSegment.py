from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class BRAINSMultiModeSegmentInputSpec(CommandLineInputSpec):
    inputVolumes = InputMultiPath(File(exists=True), argstr = "--inputVolumes %s...")
    inputMaskVolume = File( exists = True,argstr = "--inputMaskVolume %s")
    outputROIMaskVolume = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputROIMaskVolume %s")
    outputClippedVolumeROI = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--outputClippedVolumeROI %s")
    lowerThreshold = InputMultiPath(traits.Float, sep = ",",argstr = "--lowerThreshold %s")
    upperThreshold = InputMultiPath(traits.Float, sep = ",",argstr = "--upperThreshold %s")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")


class BRAINSMultiModeSegmentOutputSpec(TraitedSpec):
    outputROIMaskVolume = File( exists = True)
    outputClippedVolumeROI = File( exists = True)


class BRAINSMultiModeSegment(CommandLine):

    input_spec = BRAINSMultiModeSegmentInputSpec
    output_spec = BRAINSMultiModeSegmentOutputSpec
    _cmd = " BRAINSMultiModeSegment "
    _outputs_filenames = {'outputROIMaskVolume':'outputROIMaskVolume.nii','outputClippedVolumeROI':'outputClippedVolumeROI.nii'}

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
        return super(BRAINSMultiModeSegment, self)._format_arg(name, spec, value)

