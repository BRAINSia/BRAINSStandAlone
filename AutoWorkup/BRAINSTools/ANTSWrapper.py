#! /usr/bin/env python
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""

Program:       PINC/nipype/Wrappers/ants.py
Date:          Tue Jan  3 10:47:45 2012
Author:        David Welch, dmwelch@NOSPAM.uiowa.edu                                                #
Purpose:       Wrap a Bash script to interface ANTS with Nipype

Requirements:  <<< Interface specifications >>>

$ ANTS_wrapper.sh <FixedT1Image> <FixedT2Image> <MovingT1Image> <MovingT2Image> <OutputPrefix>

               where the script implicitly generates three output files:
               <OutputPrefix>Affine.txt
               <OutputPrefix>Warp.nii.gz
               <OutputPrefix>InverseWarp.nii.gz


"""
from nipype.interfaces.base import ( File, TraitedSpec, Interface, CommandLineInputSpec, CommandLine, traits )

### CommandLine
class ANTSWrapperCLInputSpec(CommandLineInputSpec):
    fixed_T1_image = File(desc="T1 Fixed Volume", exists=True, mandatory=True, position=0, argstr="%s" )
    fixed_T2_image = File(desc="T2 Fixed Volume", exists=True, mandatory=True, position=1, argstr="%s" )
    moving_T1_image = File(desc="T1 Moving Volume", exists=True, mandatory=True, position=2, argstr="%s" )
    moving_T2_image = File(desc="T2 Moving Volume", exists=True, mandatory=True, position=3, argstr="%s" )
    initialTransform = File( desc = "Initial Transform", exists = True, mandatory = True, position=5, argstr="%s" )
    prefix_desc = "Output volume prefix for Affine.txt, _1Warp.nii.gz, and _1InverseWarp.nii.gz"
    output_prefix = traits.Str(desc=prefix_desc, exists=True, mandatory=False, position=4, argstr="%s",
                               default_value="./ANTS_" )

class ANTSWrapperCLOutputSpec(CommandLineInputSpec):
    output_affine = File( desc = "Affine Transform Text File", exists = True, mandatory = False)
    output_warp = File( desc = "Warped Output Volume", exists = True, mandatory = True )
    output_invwarp = File( desc = "Inverse Warp Output Volume", exists = True, mandatory = False)

class ANTSWrapper(CommandLine):
    _cmd = 'ANTS_wrapper.sh'
    input_spec = ANTSWrapperCLInputSpec
    output_spec = ANTSWrapperCLOutputSpec

    def _list_outputs(self):
        """
        The ANTS package implicitly outputs three files based on the prefix given at the commandline:
        {prefix}Affine.txt, {prefix}_{index}Warp.nii.gz, and {prefix}_{index}InverseWarp.nii.gz.  This function exposes
        them for subsequent nodes.
        """
        from os.path import abspath
        outputs = self.output_spec().get()
        #outputs['output_affine'] = abspath( self.inputs.output_prefix + 'Affine.txt')
        outputs['output_affine'] = abspath( self.inputs.initialTransform )
        outputs['output_warp'] = abspath( self.inputs.output_prefix + '1' + 'Warp.nii.gz')
        outputs['output_invwarp'] = abspath( self.inputs.output_prefix + '1' + 'InverseWarp.nii.gz')
        return outputs

if __name__ == '__main__':
    ants = ANTSWrapper(sys.argv)
    ants.run()
