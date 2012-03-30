from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os

class BRAINSAlignMSPInputSpec(CommandLineInputSpec):
    inputVolume = File( exists = True,argstr = "--inputVolume %s")
    resampleMSP = traits.Either(traits.Bool, File(), hash_files = False,argstr = "--OutputresampleMSP %s")
    verbose = traits.Bool( argstr = "--verbose ")
    resultsDir = traits.Either(traits.Bool, Directory(), hash_files = False,argstr = "--resultsDir %s")
    writedebuggingImagesLevel = traits.Int( argstr = "--writedebuggingImagesLevel %d")
    mspQualityLevel = traits.Int( argstr = "--mspQualityLevel %d")
    rescaleIntensities = traits.Bool( argstr = "--rescaleIntensities ")
    trimRescaledIntensities = traits.Float( argstr = "--trimRescaledIntensities %f")
    rescaleIntensitiesOutputRange = InputMultiPath(traits.Int, sep = ",",argstr = "--rescaleIntensitiesOutputRange %s")
    backgroundFillValueString = traits.Str( argstr = "--BackgroundFillValue %s")
    interpolationMode = traits.Enum("NearestNeighbor","Linear","ResampleInPlace","BSpline","WindowedSinc","Hamming","Cosine","Welch","Lanczos","Blackman", argstr = "--interpolationMode %s")
    numberOfThreads = traits.Int( argstr = "--numberOfThreads %d")


class BRAINSAlignMSPOutputSpec(TraitedSpec):
    resampleMSP = File( exists = True)
    resultsDir = Directory( exists = True)


class BRAINSAlignMSP(CommandLine):

    input_spec = BRAINSAlignMSPInputSpec
    output_spec = BRAINSAlignMSPOutputSpec
    _cmd = " BRAINSAlignMSP "
    _outputs_filenames = {'resampleMSP':'resampleMSP.nii','resultsDir':'resultsDir'}

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
        return super(BRAINSAlignMSP, self)._format_arg(name, spec, value)

