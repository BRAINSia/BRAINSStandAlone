# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""

Program:       PINC/nipype/Wrappers/warpImageMultiTransform.py
Date:          Tue Jan  3 13:35:44 2012
Author:        David Welch, dmwelch@NOSPAM.uiowa.edu                                                #
Purpose:       Wrap a Bash script to interface with Nipype

Requirements:  <<< Interface specifications >>>

$ WarpAllAtlas_wrapper.sh <AffineTransform> <DeformationField> <MovingReference> <DeformedImage>


"""
from nipype.utils.filemanip import fname_presuffix
from nipype.interfaces.base import ( File, Directory, TraitedSpec, Interface, CommandLineInputSpec, CommandLine,
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
class WarpAllAtlasInputSpec( TraitedSpec ):
    affine_transform = File( desc = "Affine Transform file", exists = True, mandatory = True)
    deformation_field = File( desc = "Deformation Field file", exists = True, mandatory = True)
    reference_image = File( desc = "Moving Reference Volume", exists = True, mandatory = True)
    moving_atlas = File( desc = "Warped Volume path/filename", exists = True, mandatory = False )

class WarpAllAtlasOutputSpec(TraitedSpec):
    deformed_atlas = File( desc = "Warped Volume path/filename", exists = True )

class WarpAllAtlas(Interface):
    input_spec = WarpAllAtlasInputSpec
    output_spec = WarpAllAtlasOutputSpec

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['deformed_atlas'] = self.inputs.moving_atlas
        if not isdefined(outputs["deformed_atlas"]) and isdefined(self.inputs.affine_transform):
            outputs['deformed_atlas'] = _gen_fname( self.inputs.affine_transform ,
                                                    suffix = "_WIMT",
                                                    use_ext = False)
        return outputs


### CommandLine
class WarpAllAtlasCLInputSpec(CommandLineInputSpec):
    affine_transform = File(desc="Affine Transform file", exists=True, mandatory=True, position=0, argstr="%s")
    deformation_field = File(desc="Deformation Field file", exists=True, mandatory=True, position=1, argstr="%s")
    reference_image = File(desc="Moving Reference Volume", exists=True, mandatory=True, position=2, argstr="%s")
    moving_atlas = Directory(desc="Warped Volume path/filename", exists=True, mandatory=True, position=3, argstr="%s")
    deformed_atlas = Directory(desc = "Warped Volume", mandatory=True, position=4, argstr="%s")
    #, default_value="./Warp_Image_Multi_Transform_Output.nii.gz")
    pass

class WarpAllAtlasCLOutputSpec(CommandLineInputSpec):
    deformed_atlas = Directory(desc = "Output Warped Volume", mandatory=True, argstr="%s")
    pass

class WarpAllAtlas(CommandLine):
    _cmd = 'WarpAllAtlas_wrapper.sh'
    input_spec = WarpAllAtlasCLInputSpec
    output_spec = WarpAllAtlasCLOutputSpec

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['deformed_atlas'] = self.inputs.deformed_atlas
        if not isdefined(outputs["deformed_atlas"]) and isdefined(self.inputs.affine_transform):
            outputs['deformed_atlas'] = _gen_fname( self.inputs.affine_transform ,
                                                    suffix = "_WIMT",
                                                    use_ext = False)
        return outputs

if __name__ == '__main__':
    warp = WarpAllAtlas(sys.argv)
    warp.run()
