# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""

Program:       PINC/nipype/Wrappers/warpImageMultiTransform.py
Date:          Tue Jan  3 13:35:44 2012
Author:        David Welch, dmwelch@NOSPAM.uiowa.edu                                                #
Purpose:       Wrap a Bash script to interface with Nipype

Requirements:  <<< Interface specifications >>>

$ WarpImageMultiTransform_wrapper.sh <AffineTransform> <DeformationField> <MovingReference> <DeformedImage>


"""
from nipype.utils.filemanip import fname_presuffix
from nipype.interfaces.base import ( File, TraitedSpec, Interface, CommandLineInputSpec, CommandLine,
                                     traits, isdefined )

def _gen_fname(self, basename, cwd=None, prefix=None):
    """Generate a filename based on the given parameters.

    The filename will take the form: cwd/<prefix>basename.

    Parameters
    ----------
    basename : str
    Filename to base the new filename on.
    cwd : str
    Path to prefix to the new filename. (default is os.getcwd())
    prefix : str
    Prefix to add to the `basename`.  (defaults is '' )

    Returns
    -------
    fname : str
    New filename based on given parameters.

    """

    if basename == '':
        msg = 'Unable to generate filename for command %s. ' % self.cmd
        msg += 'basename is not set!'
        raise ValueError(msg)
    if cwd is None:
        cwd = os.getcwd()
    if prefix is None:
        prefix = ''
    fname = fname_presuffix(basename, prefix = prefix,
                            use_ext = False, newpath = cwd)
    return fname


### Node Interface
class WarpImageMultiTransformInputSpec( TraitedSpec ):
    affine_transform = File( desc = "Affine Transform file", exists = True, mandatory = True)
    deformation_field = File( desc = "Deformation Field file", exists = True, mandatory = True)
    reference_image = File( desc = "Moving Reference Volume", exists = True, mandatory = True)
    moving_image = File( desc = "Warped Volume path/filename", exists = True, mandatory = False )

class WarpImageMultiTransformOutputSpec(TraitedSpec):
    deformed_image = File( desc = "Warped Volume path/filename", exists = True )

class WarpImageMultiTransform(Interface):
    input_spec = WarpImageMultiTransformInputSpec
    output_spec = WarpImageMultiTransformOutputSpec

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['deformed_image'] = self.inputs.moving_image
        if not isdefined(outputs["deformed_image"]) and isdefined(self.inputs.affine_transform):
            outputs['deformed_image'] = _gen_fname( self.inputs.affine_transform ,
                                                    suffix = "_WIMT",
                                                    use_ext = False)
        return outputs


### CommandLine
class WarpImageMultiTransformCLInputSpec(CommandLineInputSpec):
    affine_transform = File(desc="Affine Transform file", exists=True, mandatory=True, position=0, argstr="%s")
    deformation_field = File(desc="Deformation Field file", exists=True, mandatory=True, position=1, argstr="%s")
    reference_image = File(desc="Moving Reference Volume", exists=True, mandatory=True, position=2, argstr="%s")
    moving_image = File(desc="Warped Volume path/filename", exists=True, mandatory=False, position=3, argstr="%s")
    deformed_image = File(desc = "Warped Volume", mandatory=True, position=4, argstr="%s")
    #, default_value="./Warp_Image_Multi_Transform_Output.nii.gz")

class WarpImageMultiTransformCLOutputSpec(CommandLineInputSpec):
    deformed_image = File(desc = "Output Warped Volume", mandatory=True, argstr="%s")
    pass

class WarpImageMultiTransform(CommandLine):
    _cmd = 'WarpImageMultiTransform_wrapper.sh'
    input_spec = WarpImageMultiTransformCLInputSpec
    output_spec = WarpImageMultiTransformCLOutputSpec

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['deformed_image'] = self.inputs.deformed_image
        if not isdefined(outputs["deformed_image"]) and isdefined(self.inputs.affine_transform):
            outputs['deformed_image'] = _gen_fname( self.inputs.affine_transform ,
                                                    suffix = "_WIMT",
                                                    use_ext = False)
        return outputs

if __name__ == '__main__':
    warp = WarpImageMultiTransform(sys.argv)
    warp.run()
