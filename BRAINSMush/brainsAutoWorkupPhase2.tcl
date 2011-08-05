################################################################################
# Program:   BRAINS (Brain Research: Analysis of Images, Networks, and Systems)
# Module:    $RCSfile: $
# Language:  TCL
# Date:      $Date:  $
# Version:   $Revision: $
# 
#   Copyright (c) Iowa Mental Health Clinical Research Center. All rights reserved.
#   See BRAINSCopyright.txt or http://www.psychiatry.uiowa.edu/HTML/Copyright.html 
#   for details.
# 
#      This software is distributed WITHOUT ANY WARRANTY; without even 
#      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
#      PURPOSE.  See the above copyright notices for more information.
#
################################################################################


namespace eval Brains::AutoWorkup {



  # Brains::AutoWorkup::FindACPCAlignmentUsingT1BrainMaskAndAtlas --
  # 
  #  This function, FindACPCAlignmentUsingT1BrainMaskAndAtlas, does Phase 2.  
  #
  # Arguments:
  #  T1RawBfc                     - FileName of intensity remapped, unrotated raw image from Phase 1.
  #  T1RawBfcBrainMask            - FileName of T1-RAW-aligned T1-SkullStrip Smoothed mask from Phase 1.
  #  T2RawT1BfcBrainMask          - FileName of T1-RAW-aligned T2-SkullStrip Smoothed mask from Phase 1.
  #  T1RawBayesianLabelMap        - FileName of T1-RAW-aligned Bayesian segmentation image from Phase 1.
  #  T1RawLabeledBrainMask        - FileName of T1-RAW-aligned good brain mask from Phase 1.
  #  AtlasBrain255                - FileName of atlas brain probability from summing brain masks
  #  AtlasTemplateAvg             - FileName of atlas brain template from T1 averaging
  #  AtlasBrainMask               - FileName of atlas brain mask, once used to develop scaling transform but no longer
  #  AtlasCortexMask              - FileName of atlas cerebrum-only mask used to estimate Talairach bounds later
  #  AtlasTalairach               - FileName of talairach parameters based on AtlasBrainMask and average ACPC point locaions
  #  AtlasBrainMaskThreshold      - Threshold to generate atlas brain mask used to develop scaling transform
  #  FORCE_ACPC_FROM_RAW          - Flag tested against ACPC_FORCE
  #  ACPC_RawSpace_TextFile       - File with AC and PC points in MM as text
  #  ScratchDirectory             - Temporary scratch directory
  #  AtlasScalingTransform        - FileName of a transform to map atlas data to acquisition aspect ratios
  #  ScaledAtlasBrain255          - FileName of scaled atlas brain probability
  #  ScaledAtlasTemplateAvg       - FileName of scaled atlas brain template from T1 averaging
  #  ScaledAtlasBrainMask         - FileName of scaled atlas brain mask used to clip ScaledAtlasTemplateAvg when fitting T1RawBfc to it
  #  ScaledAtlasCortexMask        - FileName of scaled atlas cerebrum-only mask for clipping Talairach estimators
  #  T1RawRotationTransform       - FileName of a transform to map raw T1 onto scaled atlas data
  #  T1RotatedT1RawBfcBrainMask   - FileName of T1-RAW-aligned T1-SkullStrip Smoothed mask rotated into place
  #  T1RotatedBayesianLabelMap    - FileName of NN-resampled Bayesian segmentation rotated into place
  #  T1RotatedLabeledBrainMask    - FileName of NN-resampled good brain mask rotated into place
  #  T1RotatedBfcImage            - FileName of BSpline-resampled T1 image rotated into place
  #  T1RawLabelMapACPCTalairach   - FileName of talairach parameters based on 
  #
  # Results:
  #  Generates the resampled-to-scale Atlas images, the ACPC-aligned brain mask and T1 image,
  #  and associated transforms and TalairachParameters.
  
  proc FindACPCAlignmentUsingT1BrainMaskAndAtlas { T1RawBfc T1RawBfcBrainMask T2RawT1BfcBrainMask T1RawBayesianLabelMap T1RawLabeledBrainMask AtlasBrain255 AtlasTemplateAvg AtlasTemplateShape AtlasCortexMask AtlasTalairach FORCE_ACPC_FROM_RAW ACPC_RawSpace_TextFile ScratchDirectory AtlasScalingTransform ScaledAtlasBrain255 ScaledAtlasTemplateAvg ScaledAtlasTemplateShape ScaledAtlasBrainMask ScaledAtlasCortexMask T1RawRotationTransform T1RotatedT1RawBfcBrainMask T1RotatedBayesianLabelMap T1RotatedLabeledBrainMask T1RotatedBfcImage T1RawLabelMapACPCTalairach {numberOfSamples 500000} {minimumStepSize .05} {numberOfIterations 1500} {InterpolationType WSincWelch5}} {

      ## I hoisted this further for experimentation, and I settled on:  
      set AtlasBrainMaskThreshold 90
  
      puts -nonewline "======= EXECUTING Phase 2: FindACPCAlignmentUsingT1BrainMaskAndAtlas: "
      puts -nonewline "$T1RawBfc $T1RawBfcBrainMask $T2RawT1BfcBrainMask $T1RawBayesianLabelMap $T1RawLabeledBrainMask "
      puts -nonewline "$AtlasBrain255 $AtlasTemplateAvg $AtlasTemplateShape $AtlasCortexMask $AtlasTalairach "
      puts -nonewline "$AtlasBrainMaskThreshold $FORCE_ACPC_FROM_RAW $ACPC_RawSpace_TextFile $ScratchDirectory "
      puts -nonewline "$AtlasScalingTransform $ScaledAtlasBrain255 $ScaledAtlasTemplateAvg $ScaledAtlasTemplateShape $ScaledAtlasBrainMask "
      puts -nonewline "$ScaledAtlasCortexMask $T1RawRotationTransform $T1RotatedT1RawBfcBrainMask  "
      puts -nonewline "$T1RotatedBayesianLabelMap $T1RotatedLabeledBrainMask $T1RotatedBfcImage $T1RawLabelMapACPCTalairach "
      puts "======= Phase 2 ======= "
      
      ## ## ##
      ##
      ##   This is atypical logic, but it means we can delete the ScratchDirectory such as delete_Phase_Two,
      ##   and not irritate the method into re-running if the end results are up to date.
      ##  
      if {[string equal $FORCE_ACPC_FROM_RAW ACPC_FORCE] == 1} {
          set basisList [list ${T1RawBfc} ${T1RawBfcBrainMask} ${T2RawT1BfcBrainMask} ${T1RawBayesianLabelMap} ${T1RawLabeledBrainMask} ${AtlasBrain255} ${AtlasTemplateAvg} ${AtlasTemplateShape} ${AtlasCortexMask} ${AtlasTalairach} ${ACPC_RawSpace_TextFile}]
      } else {
          set basisList [list ${T1RawBfc} ${T1RawBfcBrainMask} ${T2RawT1BfcBrainMask} ${T1RawBayesianLabelMap} ${T1RawLabeledBrainMask} ${AtlasBrain255} ${AtlasTemplateAvg} ${AtlasTemplateShape} ${AtlasCortexMask} ${AtlasTalairach}]
      }
      if {[file exists $ScratchDirectory] == 0} {
          if {[CheckOutputsNewer [list ${AtlasScalingTransform} ${ScaledAtlasBrain255} ${ScaledAtlasTemplateAvg} ${ScaledAtlasTemplateShape} ${ScaledAtlasBrainMask} ${ScaledAtlasCortexMask} ${T1RawRotationTransform} ${T1RotatedT1RawBfcBrainMask} ${T1RotatedBayesianLabelMap} ${T1RotatedLabeledBrainMask} ${T1RotatedBfcImage} ${T1RawLabelMapACPCTalairach}] \
                                  ${basisList} ] == true} {
               return 0
          }
      }

      file mkdir $ScratchDirectory
      
      ## ## ##
      ##
      ##    This replacement for GenerateSubjectAutoAlignmentToAverageACPCCenteredSpace
      ##    breaks down Phase 2 into a few separate steps:
  
  
      set result [Brains::AutoWorkup::ScaleACPCAtlasToT1 $T1RawLabeledBrainMask $AtlasBrain255 $AtlasTemplateAvg $AtlasTemplateShape $AtlasCortexMask $AtlasBrainMaskThreshold $ScratchDirectory $AtlasScalingTransform $ScaledAtlasBrain255 $ScaledAtlasTemplateAvg $ScaledAtlasTemplateShape $ScaledAtlasBrainMask $ScaledAtlasCortexMask ${numberOfSamples} ${minimumStepSize} ${numberOfIterations}]
      if { $result == 1 } {
        return 1
      }
  
  
      set result [Brains::AutoWorkup::TransformRawT1ToScaledACPCAtlas $T1RawBfc ${T1RawBfcBrainMask} ${T2RawT1BfcBrainMask} $T1RawBayesianLabelMap $T1RawLabeledBrainMask $ScaledAtlasTemplateAvg $ScaledAtlasBrain255 $ScaledAtlasTemplateShape $ScaledAtlasBrainMask $FORCE_ACPC_FROM_RAW $ACPC_RawSpace_TextFile $ScratchDirectory $T1RawRotationTransform $T1RotatedT1RawBfcBrainMask $T1RotatedBayesianLabelMap $T1RotatedLabeledBrainMask $T1RotatedBfcImage ${numberOfSamples} ${minimumStepSize} ${numberOfIterations} ${InterpolationType}]
      if { $result == 1 } {
        return 1
      }
  
  
      set result [Brains::AutoWorkup::MapACPCAlignedTalairachParameters $AtlasTemplateAvg $AtlasTalairach $AtlasScalingTransform $FORCE_ACPC_FROM_RAW $ACPC_RawSpace_TextFile $T1RawBfc $T1RawRotationTransform $T1RotatedLabeledBrainMask $ScratchDirectory $T1RawLabelMapACPCTalairach ]
      if { $result == 1 } {
        return 1
      }
  
  
      return 0
  }
  
  
  
  # Brains::AutoWorkup::ScaleACPCAtlasToT1 --
  #
  #  This function only develops and applies the AtlasScalingTransform.
  #
  # Arguments:
  #  T1RawLabeledBrainMask        - FileName of T1-RAW-aligned good brain mask from Phase 1.
  #  AtlasBrain255                - FileName of atlas brain probability from summing brain masks
  #  AtlasTemplateAvg             - FileName of atlas brain template from T1 averaging
  #  AtlasCortexMask              - FileName of atlas cerebrum-only mask used to estimate Talairach bounds later
  #  AtlasBrainMaskThreshold      - Threshold for generating atlas brain mask used to develop scaling transform
  #  ScratchDirectory             - Temporary scratch directory
  #  AtlasScalingTransform        - FileName of a transform to map atlas data to acquisition aspect ratios
  #  ScaledAtlasBrain255          - FileName of scaled atlas brain probability
  #  ScaledAtlasTemplateAvg       - FileName of scaled atlas brain template from T1 averaging
  #  ScaledAtlasBrainMask         - FileName of scaled atlas brain mask for clipping the fixed image in TransformRawT1ToScaledACPCAtlas
  #  ScaledAtlasCortexMask        - FileName of scaled atlas cerebrum-only mask for clipping Talairach estimators
  #
  # Results:
  #  The transform mapping the Atlas is applied to produce a scaled atlas to fit to.
  
  proc ScaleACPCAtlasToT1 { T1RawLabeledBrainMask AtlasBrain255 AtlasTemplateAvg AtlasTemplateShape AtlasCortexMask AtlasBrainMaskThreshold ScratchDirectory AtlasScalingTransform ScaledAtlasBrain255 ScaledAtlasTemplateAvg ScaledAtlasTemplateShape ScaledAtlasBrainMask ScaledAtlasCortexMask  numberOfSamples minimumStepSize numberOfIterations } {
    
    set Temp_AtlasBrainMask ${ScratchDirectory}/Threshold_${AtlasBrainMaskThreshold}_AtlasBrainMask.nii.gz
    if {[CheckOutputsNewer \
        [list ${Temp_AtlasBrainMask} ] \
        [list ${AtlasBrain255} ]] == false} {
      set result [Brains::AutoWorkup::BinaryMaskImageRange ${AtlasBrainMaskThreshold} 10000 $AtlasBrain255 $Temp_AtlasBrainMask "Signed-16bit" ]
      puts "Wrote ${Temp_AtlasBrainMask}"
    }

      ## Obtain a properly rotated, arbitrarily translated T1 mask to compare as to scale.
      #
      #  REFACTOR:  If we could save an itk transform parameters file prior to converting to Affine, 
      #  why can't we use the scale parameters themselves?
      #
      #

        set Temp_T1RawLabeledBrainClosed ${ScratchDirectory}/Unoriented_T1RawLabeledBrain_Closed.nii.gz
        if {[CheckOutputsNewer \
            [list ${Temp_T1RawLabeledBrainClosed} ] \
            [list ${T1RawLabeledBrainMask} ]] == false} {

            set Radius 5
            set brainMask [Brains::itk::LoadImage $T1RawLabeledBrainMask "Signed-16bit"]
            set m1 [Brains::itk::ApplyStructuringElementToMaskImage ${brainMask} Dilate Ball ${Radius}]
            set m2 [Brains::itk::ApplyStructuringElementToMaskImage ${m1} Erode Ball ${Radius}]
            set Radius 15
            set m3 [Brains::itk::ApplyStructuringElementToMaskImage ${m2} Erode Ball ${Radius}]
            set m4 [Brains::itk::ApplyStructuringElementToMaskImage ${m3} Dilate Ball ${Radius}]
            Brains::itk::SaveImage $m4 $Temp_T1RawLabeledBrainClosed
            $brainMask Delete
            $m1 Delete
            $m2 Delete
            $m3 Delete
            $m4 Delete
        }

      ## First, find the scaling fit of the T1 mask to the mask histogram.
    set Temp_RawBrainToAtlasBrainRigidAlignment ${ScratchDirectory}/RawBrainToAtlasBrainRigidAlignment.xfm

    set FitSignedDistancesNotMaskToProbability 1
    if $FitSignedDistancesNotMaskToProbability {

          ## ! Changed this registration from fitting the mask image and its probability histogram
          ##   to fitting two mask signed distance images, since the purpose of this portion of code is 
          ##   to correctly orient the mask with whatever scaling and shifting
          ##   will make the bounding box calipers meaningful, which is used to establish the scaled atlas 
          ##   target for a rigid fit in a later step (TransformRawT1ToScaledACPCAtlas).  

        set Temp_AtlasBrainSignedDistance ${ScratchDirectory}/Threshold_${AtlasBrainMaskThreshold}_AtlasBrain_SignedDistance.nii.gz
        if {[CheckOutputsNewer \
            [list ${Temp_AtlasBrainSignedDistance} ] \
            [list ${Temp_AtlasBrainMask} ]] == false} {
          set result [Brains::AutoWorkup::SignedDistance ${Temp_AtlasBrainMask} ${Temp_AtlasBrainSignedDistance} ]
        }

        set Temp_T1RawLabeledBrainSignedDistance ${ScratchDirectory}/Unoriented_T1RawLabeledBrain_SignedDistance.nii.gz
        if {[CheckOutputsNewer \
            [list ${Temp_T1RawLabeledBrainSignedDistance} ] \
            [list ${Temp_T1RawLabeledBrainClosed} ]] == false} {
          set result [Brains::AutoWorkup::SignedDistance ${Temp_T1RawLabeledBrainClosed} ${Temp_T1RawLabeledBrainSignedDistance} ]
        }

        if {[CheckOutputsNewer \
            [list ${Temp_RawBrainToAtlasBrainRigidAlignment} ] \
            [list ${Temp_T1RawLabeledBrainSignedDistance} ${Temp_AtlasBrainSignedDistance} ]] == false} {

          ## Chose rigid-only, not scaled, for signed distance fitting since we only  want alignment,
          ## and the scale parameters distract the optimizer into stretching meaninglessly and 
          ## permanently embarking on a failed fit for ANY numberOfIterations.
          ##
                Brains::AutoWorkup::RigidRegistration ${Temp_T1RawLabeledBrainSignedDistance}  \
                                    ${Temp_AtlasBrainSignedDistance}  \
                                    ${Temp_RawBrainToAtlasBrainRigidAlignment} \
                                    ${numberOfSamples} 1000 ${numberOfIterations} ${minimumStepSize};

        }
    } else {
        ## and this business with the nine-parameter fit is now deprecated.  It kept testing up unreliably.
        ## Then I found my bug, and restored the fixed image to be AtlasBrain255, not Temp_AtlasBrainMask.
        ## Still, the signed-distance fits are much better.

        set Temp_RawBrainToAtlasBrainInitialRigid ${ScratchDirectory}/RawBrainToAtlasBrainInitializer.xfm
        set Temp_RawBrainToAtlasBrainFreeScale ${ScratchDirectory}/RawBrainToAtlasBrainFreeScale.xfm

        if {[CheckOutputsNewer \
            [list ${Temp_RawBrainToAtlasBrainRigidAlignment} ${Temp_RawBrainToAtlasBrainFreeScale} ${Temp_RawBrainToAtlasBrainInitialRigid} ] \
            [list ${T1RawLabeledBrainMask} ${AtlasBrain255} ]] == false} {

                Brains::AutoWorkup::NineParameterImageToTemplateMIRegistration ${T1RawLabeledBrainMask} ${AtlasBrain255} \
                ${T1RawLabeledBrainMask} ${Temp_AtlasBrainMask} \
                ${Temp_RawBrainToAtlasBrainInitialRigid} \
                ${Temp_RawBrainToAtlasBrainFreeScale} \
                ${Temp_RawBrainToAtlasBrainRigidAlignment} \
                ${numberOfSamples} 250 ${numberOfIterations} ${minimumStepSize};

        }
    }


    ## Resample a properly rotated, arbitrarily translated T1 mask to compare as to scale.
    
    set Temp_InitialOrientedBrainMask ${ScratchDirectory}/InitialOrientedBrainMask.nii.gz
    if {[CheckOutputsNewer \
        [list ${Temp_InitialOrientedBrainMask} ] \
        [list ${Temp_T1RawLabeledBrainClosed} ${AtlasTemplateAvg} ${Temp_RawBrainToAtlasBrainRigidAlignment} ]] == false} {
      set interpolationType NearestNeighbor
      set DataType "Signed-16bit"
      set useCoronalOrientation 0
      Brains::itkUtils::ResampleBinaryImageFileWithTransformFile $Temp_T1RawLabeledBrainClosed $AtlasTemplateAvg $Temp_RawBrainToAtlasBrainRigidAlignment $Temp_InitialOrientedBrainMask $interpolationType $DataType $useCoronalOrientation
    }


    ## Piece together a scaling transform based on bounding boxes for Atlas and Initial masks.
    if {[CheckOutputsNewer \
        [list ${AtlasScalingTransform} ] \
        [list ${Temp_AtlasBrainMask} ${Temp_InitialOrientedBrainMask} ]] == false} {
        set result [Brains::AutoWorkup::ComputeMaskBoundingBoxScaleTransformAndSave $Temp_AtlasBrainMask $Temp_InitialOrientedBrainMask $AtlasScalingTransform]
    }    


    ##
    #  ScaledAtlasTemplateAvg       - 
    if {[CheckOutputsNewer \
        [list ${ScaledAtlasTemplateAvg} ] \
        [list ${AtlasTemplateAvg} ${AtlasScalingTransform} ]] == false} {
      set interpolationType Linear
      set DataType "Signed-16bit"
      set useCoronalOrientation 0
      set result [Brains::itkUtils::ResampleImageFileWithTransformFile $AtlasTemplateAvg $AtlasTemplateAvg $AtlasScalingTransform $ScaledAtlasTemplateAvg $interpolationType $DataType $useCoronalOrientation]
      if { $result == 1 } {
        return 1
      }
      puts "Wrote ${ScaledAtlasTemplateAvg}"
    }

if 1 {
    ##
    #  ScaledAtlasTemplateShape       - REFACTOR:  Scale the mask image and do SignedDistance on that.
    set Temp_AtlasScaledBrainMask ${ScratchDirectory}/AtlasScaledBrainMask.nii.gz
    if {[CheckOutputsNewer \
        [list ${Temp_AtlasScaledBrainMask} ] \
        [list ${Temp_T1RawLabeledBrainClosed} ${AtlasTemplateAvg} ${Temp_RawBrainToAtlasBrainRigidAlignment} ]] == false} {
      set interpolationType NearestNeighbor
      set DataType "Signed-16bit"
      set useCoronalOrientation 0
      Brains::itkUtils::ResampleBinaryImageFileWithTransformFile $Temp_AtlasBrainMask $AtlasTemplateAvg $AtlasScalingTransform $Temp_AtlasScaledBrainMask $interpolationType $DataType $useCoronalOrientation
    }
    if {[CheckOutputsNewer \
        [list ${ScaledAtlasTemplateShape} ] \
        [list ${Temp_AtlasScaledBrainMask} ]] == false} {
      set result [Brains::AutoWorkup::SignedDistance ${Temp_AtlasScaledBrainMask} ${ScaledAtlasTemplateShape} ]
      puts "Wrote ${ScaledAtlasTemplateShape}"
    }
} else {
    if {[CheckOutputsNewer \
        [list ${ScaledAtlasTemplateShape} ] \
        [list ${AtlasTemplateAvg} ${AtlasTemplateShape} ]] == false} {
      set interpolationType Linear
      set DataType "Signed-16bit"
      set useCoronalOrientation 0
      set result [Brains::itkUtils::ResampleImageFileWithTransformFile $AtlasTemplateShape $AtlasTemplateAvg $AtlasScalingTransform $ScaledAtlasTemplateShape $interpolationType $DataType $useCoronalOrientation]
      if { $result == 1 } {
        return 1
      }
      puts "Wrote ${ScaledAtlasTemplateShape}"
    }

}
    ##
    #  ScaledAtlasBrain255          - 
    if {[CheckOutputsNewer \
        [list ${ScaledAtlasBrain255} ] \
        [list ${AtlasBrain255} ${AtlasTemplateAvg} ${AtlasScalingTransform} ]] == false} {
      set interpolationType Linear
      set DataType "Signed-16bit"
      set useCoronalOrientation 0
      set result [Brains::itkUtils::ResampleImageFileWithTransformFile $AtlasBrain255 $AtlasTemplateAvg $AtlasScalingTransform $ScaledAtlasBrain255 $interpolationType $DataType $useCoronalOrientation]
      if { $result == 1 } {
        return 1
      }
      puts "Wrote ${ScaledAtlasBrain255}"
    }

    ##
    #  ScaledAtlasBrainMask         - Thresholded at 90 out of about 255 on ScaledAtlasBrain255
    if {[CheckOutputsNewer \
        [list ${ScaledAtlasBrainMask} ] \
        [list ${ScaledAtlasBrain255} ]] == false} {
      set result [Brains::AutoWorkup::BinaryMaskImageRange ${AtlasBrainMaskThreshold} 10000 ${ScaledAtlasBrain255} ${ScaledAtlasBrainMask} "Signed-16bit" ]
      puts "Wrote ${ScaledAtlasBrainMask}"
    }

    ##
    #  ScaledAtlasCortexMask        - 
    if {[CheckOutputsNewer \
        [list ${ScaledAtlasCortexMask} ] \
        [list ${AtlasCortexMask} ${AtlasTemplateAvg} ${AtlasScalingTransform} ]] == false} {
      set interpolationType Linear
      set DataType "Signed-16bit"
      set useCoronalOrientation 0
      set result [Brains::itkUtils::ResampleBinaryImageFileWithTransformFile $AtlasCortexMask $AtlasTemplateAvg $AtlasScalingTransform $ScaledAtlasCortexMask $interpolationType $DataType $useCoronalOrientation]
      if { $result == 1 } {
        return 1
      }
      puts "Wrote ${ScaledAtlasCortexMask}"
    }
    
    Brains::Utils::CheckFileExistance [ list ${AtlasScalingTransform} ${ScaledAtlasBrain255} ${ScaledAtlasTemplateAvg} ${ScaledAtlasBrainMask} ${ScaledAtlasCortexMask} ]
  
    return 0
  }
  
  
  # Brains::AutoWorkup::TransformRawT1ToScaledACPCAtlas --
  #
  #  This function fits the Bfc Raw T1 to the scaled atlas and maps various information-bearing
  #  image files forward from T1 Raw space to T1 AlignedToACPC space.
  #
  # Arguments:
  #  T1RawBfc                     - FileName of intensity remapped, unrotated raw image from Phase 1.
  #  T1RawBfcBrainMask            - FileName of T1-RAW-aligned T1-SkullStrip Smoothed mask from Phase 1.
  #  T2RawT1BfcBrainMask          - FileName of T1-RAW-aligned T2-SkullStrip Smoothed mask from Phase 1.
  #  T1RawBayesianLabelMap        - FileName of T1-RAW-aligned Bayesian segmentation image from Phase 1.
  #  T1RawLabeledBrainMask        - FileName of T1-RAW-aligned good brain mask from Phase 1.
  #  ScaledAtlasTemplateAvg       - FileName of scaled atlas brain template from T1 averaging
  #  ScaledAtlasBrainMask         - FileName of scaled atlas brain mask used to clip ScaledAtlasTemplateAvg when fitting T1RawBfc to it
  #  FORCE_ACPC_FROM_RAW          - Flag tested against ACPC_FORCE
  #  ACPC_RawSpace_TextFile       - File with AC and PC points in MM as text
  #  ScratchDirectory             - Temporary scratch directory
  #  T1RawRotationTransform       - FileName of a transform to map raw T1 onto scaled atlas data
  #  T1RotatedT1RawBfcBrainMask   - FileName of T1-RAW-aligned T1-SkullStrip Smoothed mask rotated into place
  #  T1RotatedBayesianLabelMap    - FileName of NN-resampled Bayesian segmentation rotated into place
  #  T1RotatedLabeledBrainMask    - FileName of NN-resampled good brain mask rotated into place
  #  T1RotatedBfcImage            - FileName of BSpline-resampled T1 image rotated into place
  #
  # Results:
  #  The transform mapping the raw T1 to the scaled atlas is applied to 
  #  produce ACPC-aligned resampled BFC T1.
  
  proc TransformRawT1ToScaledACPCAtlas { T1RawBfc T1RawBfcBrainMask T2RawT1BfcBrainMask T1RawBayesianLabelMap T1RawLabeledBrainMask ScaledAtlasTemplateAvg ScaledAtlasBrain255 ScaledAtlasTemplateShape ScaledAtlasBrainMask FORCE_ACPC_FROM_RAW ACPC_RawSpace_TextFile ScratchDirectory T1RawRotationTransform T1RotatedT1RawBfcBrainMask T1RotatedBayesianLabelMap T1RotatedLabeledBrainMask T1RotatedBfcImage numberOfSamples minimumStepSize numberOfIterations InterpolationType } {

    set FitClippedNotShaped 0
    if {${FitClippedNotShaped} == 1} {  
      # clip image ScaledAtlasTemplateAvg to mask ScaledAtlasBrainMask and save in temp FixedScaledAtlasClipped
        set Temp_FixedScaledAtlasClipped ${ScratchDirectory}/clipped_150_[file tail ${ScaledAtlasTemplateAvg}]
        if {[CheckOutputsNewer \
            [list ${Temp_FixedScaledAtlasClipped} ] \
            [list ${ScaledAtlasTemplateAvg} ${ScaledAtlasBrainMask} ]] == false} {
          set atlasOutsideValueWhenClipping 150
          set result [Brains::AutoWorkup::ClipImage16 ${ScaledAtlasTemplateAvg} ${ScaledAtlasBrainMask} ${Temp_FixedScaledAtlasClipped} ${atlasOutsideValueWhenClipping}]
          puts "Wrote ${Temp_FixedScaledAtlasClipped}"
        }


      # clip image T1RawBfc to mask T1RawLabeledBrainMask and save in temp MovingT1BfcClipped
        set Temp_MovingT1BfcClipped ${ScratchDirectory}/clipped_m_[file tail ${T1RawBfc}]
        if {[CheckOutputsNewer \
            [list ${Temp_MovingT1BfcClipped} ] \
            [list ${T1RawBfc} ${T1RawLabeledBrainMask} ${T1RawBayesianLabelMap} ]] == false} {
          set Temp_StatsFile ${ScratchDirectory}/[file rootname [file rootname [file tail ${T1RawBayesianLabelMap}]]]_T1BfcStatistics.txt
          set result [Brains::AutoWorkup::WriteLabelImageStatisticsToFile $T1RawBfc $T1RawBayesianLabelMap $Temp_StatsFile]
          set flpt [open $Temp_StatsFile r]
          gets $flpt statisticsTable
          close $flpt
          puts "Statistics read as: ${statisticsTable}"
          ## rows 0-4 are x, y, csf, gray, white; 1 is Mean, 4 is StdDev.; value is in position 2.
          set rawT1OutsideValueWhenClipping [expr int( [lindex [lindex [lindex ${statisticsTable} 2] 1] 2] ) ]

          set result [Brains::AutoWorkup::ClipImage16 ${T1RawBfc} ${T1RawLabeledBrainMask} ${Temp_MovingT1BfcClipped} ${rawT1OutsideValueWhenClipping}]
          puts "Wrote ${Temp_MovingT1BfcClipped}"
        }
    } else {
        #  Prepare for a fitting alternative, maybe with signed distances again?  That worked better than expected.
        #  Vince was proposing an iterative closest point surface-to-surface fit -- more software, less running time
        #  than signed distances.  Ron wants to emphasize shape here:  the outline only, not the wm spine as well.

        set Temp_T1RawLabeledBrainClosed ${ScratchDirectory}/Unoriented_T1RawLabeledBrain_Closed.nii.gz
        if {[CheckOutputsNewer \
            [list ${Temp_T1RawLabeledBrainClosed} ] \
            [list ${T1RawLabeledBrainMask} ]] == false} {

            set ErosionRadius 10
            set brainMask [Brains::itk::LoadImage $T1RawLabeledBrainMask "Signed-16bit"]
            set m1 [Brains::itk::ApplyStructuringElementToMaskImage ${brainMask} Dilate Ball ${ErosionRadius}]
            set m2 [Brains::itk::ApplyStructuringElementToMaskImage ${m1} Erode Ball ${ErosionRadius}]
            set ErosionRadius 15
            set m3 [Brains::itk::ApplyStructuringElementToMaskImage ${m2} Erode Ball ${ErosionRadius}]
            set m4 [Brains::itk::ApplyStructuringElementToMaskImage ${m3} Dilate Ball ${ErosionRadius}]
            Brains::itk::SaveImage $m4 $Temp_T1RawLabeledBrainClosed
            $brainMask Delete
            $m1 Delete
            $m2 Delete
            $m3 Delete
            $m4 Delete
        }

if 1 {
        set Temp_MovingT1BfcBrainShape ${ScratchDirectory}/Unoriented_T1RawLabeledBrain_SignedDistance.nii.gz
        if {[CheckOutputsNewer \
            [list ${Temp_MovingT1BfcBrainShape} ] \
            [list ${Temp_T1RawLabeledBrainClosed} ]] == false} {
          set result [Brains::AutoWorkup::SignedDistance ${Temp_T1RawLabeledBrainClosed} ${Temp_MovingT1BfcBrainShape} ]
        }
}

    }
  
  # find RigidRegistration of MovingT1BfcClipped to FixedScaledAtlasClipped and write temp InitialT1RawRotationTransform
    
    if {${FitClippedNotShaped} == 0} {
        #
            set Temp_InitialT1RawRotationTransform ${ScratchDirectory}/Initial_[file tail ${T1RawRotationTransform}]

if 1 {
            if {[Brains::Utils::CheckOutputsNewer \
                [list ${Temp_InitialT1RawRotationTransform} ] \
                [list ${Temp_MovingT1BfcBrainShape} ${ScaledAtlasTemplateShape} ]] == false} {

               set forceCoronal 0
               RigidRegistration ${Temp_MovingT1BfcBrainShape} \
                                 ${ScaledAtlasTemplateShape} \
                                 ${Temp_InitialT1RawRotationTransform} \
                                 ${numberOfSamples} 1000 ${numberOfIterations} ${minimumStepSize} ${forceCoronal}
              puts "Wrote ${Temp_InitialT1RawRotationTransform}"
            }
} else {
            if {[Brains::Utils::CheckOutputsNewer \
                [list ${Temp_InitialT1RawRotationTransform} ] \
                [list ${Temp_T1RawLabeledBrainClosed} ${ScaledAtlasBrain255} ]] == false} {

               set forceCoronal 0
               RigidRegistration ${Temp_T1RawLabeledBrainClosed} \
                                 ${ScaledAtlasBrain255} \
                                 ${Temp_InitialT1RawRotationTransform} \
                                 ${numberOfSamples} 1000 ${numberOfIterations} ${minimumStepSize} ${forceCoronal}
              puts "Wrote ${Temp_InitialT1RawRotationTransform}"
            }
}


    } else {
        #
            set Temp_InitialT1RawRotationTransform ${ScratchDirectory}/Initial_[file tail ${T1RawRotationTransform}]
            if {[Brains::Utils::CheckOutputsNewer \
                [list ${Temp_InitialT1RawRotationTransform} ] \
                [list ${Temp_MovingT1BfcClipped} ${Temp_FixedScaledAtlasClipped} ]] == false} {

               set forceCoronal 0
               RigidRegistration ${Temp_MovingT1BfcClipped} \
                                 ${Temp_FixedScaledAtlasClipped} \
                                 ${Temp_InitialT1RawRotationTransform} \
                                 ${numberOfSamples} 1000 ${numberOfIterations} ${minimumStepSize} ${forceCoronal}
              puts "Wrote ${Temp_InitialT1RawRotationTransform}"
            }

    }


## ##
#
#  REFACTOR:  We debugged our way into forcing the ACPC points to get the right outcome, and now that 
#  the AtlasScaling is better debugged than in AUTO.v020, the ACPC_FORCE option image nudge "shouldn't 
#  be necessary," at least in the common cases and if we obtain a better fit than before with SignedDistances.   
#  And standardizing the atlas to be DirectionRIP and OriginCenter, 
#

  # This Works: pin down AC point, then shift InitialT1RawRotationTransform and write T1RawRotationTransform
    if {[string equal ${FORCE_ACPC_FROM_RAW} ACPC_FORCE] == 1} {
        if {[CheckOutputsNewer \
                [list ${T1RawRotationTransform}  ] \
                [list ${Temp_InitialT1RawRotationTransform} ]] == false} {
            set result [Brains::AutoWorkup::ShiftToPredefinedRawSpaceACPCLocations ${ACPC_RawSpace_TextFile} ${Temp_InitialT1RawRotationTransform} ${T1RawBfc} ${ScaledAtlasTemplateAvg} ${T1RawRotationTransform} ]
            

                # clip image T1RawBfc to mask T1RawLabeledBrainMask and save in temp MovingT1BfcClipped
                  set Temp_MovingT1BfcClipped ${ScratchDirectory}/clipped_0_[file tail ${T1RawBfc}]
                  if {[CheckOutputsNewer \
                      [list ${Temp_MovingT1BfcClipped} ] \
                      [list ${T1RawBfc} ${T1RawLabeledBrainMask} ]] == false} {
                    set rawT1OutsideValueWhenClipping 0
                    set result [Brains::AutoWorkup::ClipImage16 ${T1RawBfc} ${T1RawLabeledBrainMask} ${Temp_MovingT1BfcClipped} ${rawT1OutsideValueWhenClipping}]
                    puts "Wrote ${Temp_MovingT1BfcClipped}"
                  }

                  set Temp_IntronDebugImage ${ScratchDirectory}/clipped_rotated_reshifted_[file tail ${T1RotatedBfcImage}]
                  set interpolationType Linear
                  set DataType "Signed-16bit"
                  set useCoronalOrientation 0
                  set result [Brains::itkUtils::ResampleImageFileWithTransformFile ${Temp_MovingT1BfcClipped} ${ScaledAtlasTemplateAvg} ${T1RawRotationTransform} $Temp_IntronDebugImage $interpolationType $DataType $useCoronalOrientation]

        }
    } else {
        ###### Just copy the file with no modifications. This is the best guess when manual ACPC is not defined.
        ###### DEBUG -- This is where some HDNLW could better detect where the AC and PC points really belong.
        if {[CheckOutputsNewer \
                [list ${T1RawRotationTransform}  ] \
                [list ${Temp_InitialT1RawRotationTransform} ]] == false} {
            file copy -force ${Temp_InitialT1RawRotationTransform}  ${T1RawRotationTransform};
        }
    }



  
  # resample T1RawBfc with T1RawRotationTransform interpolating BSpline and save in T1RotatedBfcImage
    if {[CheckOutputsNewer \
        [list ${T1RotatedBfcImage} ] \
        [list ${T1RawBfc} ${ScaledAtlasTemplateAvg} ${T1RawRotationTransform} ]] == false} {
      set interpolationType ${InterpolationType}
      set DataType "Signed-16bit"
      set useCoronalOrientation 0
      set result [Brains::itkUtils::ResampleImageFileWithTransformFile $T1RawBfc $ScaledAtlasTemplateAvg $T1RawRotationTransform $T1RotatedBfcImage $interpolationType $DataType $useCoronalOrientation]
      if { $result == 1 } {
        return 1
      }
      puts "Wrote ${T1RotatedBfcImage}"
    }
  
  # resample T1RawBayesianLabelMap with T1RawRotationTransform interpolating NearestNeighbor and save in T1RotatedBayesianLabelMap
    if {[CheckOutputsNewer \
        [list ${T1RotatedBayesianLabelMap} ] \
        [list ${T1RawBayesianLabelMap} ${ScaledAtlasTemplateAvg} ${T1RawRotationTransform} ]] == false} {
      set interpolationType NearestNeighbor
      set DataType "Signed-16bit"
      set useCoronalOrientation 0
      set result [Brains::itkUtils::ResampleImageFileWithTransformFile $T1RawBayesianLabelMap $ScaledAtlasTemplateAvg $T1RawRotationTransform $T1RotatedBayesianLabelMap $interpolationType $DataType $useCoronalOrientation]
      if { $result == 1 } {
        return 1
      }
      puts "Wrote ${T1RotatedBayesianLabelMap}"
    }


  # resample T1RawBfcBrainMask with T1RawRotationTransform interpolating Binary/Linear and save in T1RotatedT1RawBfcBrainMask
    if {[CheckOutputsNewer \
        [list ${T1RotatedT1RawBfcBrainMask} ] \
        [list ${T1RawBfcBrainMask} ${ScaledAtlasTemplateAvg} ${T1RawRotationTransform} ]] == false} {
      set interpolationType Linear
      set DataType "Signed-16bit"
      set useCoronalOrientation 0
      set result [Brains::itkUtils::ResampleBinaryImageFileWithTransformFile $T1RawBfcBrainMask $ScaledAtlasTemplateAvg $T1RawRotationTransform $T1RotatedT1RawBfcBrainMask $interpolationType $DataType $useCoronalOrientation]
      if { $result == 1 } {
        return 1
      }
      puts "Wrote ${T1RotatedT1RawBfcBrainMask}"
    }




if 0 {

  # resample T2RawT1BfcBrainMask with T1RawRotationTransform interpolating Binary/Linear and save in T1RotatedT2RawT1BfcBrainMask
    if {[CheckOutputsNewer \
        [list ${T1RotatedT2RawT1BfcBrainMask} ] \
        [list ${T2RawT1BfcBrainMask} ${ScaledAtlasTemplateAvg} ${T1RawRotationTransform} ]] == false} {
      set interpolationType Linear
      set DataType "Signed-16bit"
      set useCoronalOrientation 0
      set result [Brains::itkUtils::ResampleBinaryImageFileWithTransformFile $T2RawT1BfcBrainMask $ScaledAtlasTemplateAvg $T1RawRotationTransform $T1RotatedT2RawT1BfcBrainMask $interpolationType $DataType $useCoronalOrientation]
      if { $result == 1 } {
        return 1
      }
      puts "Wrote ${T1RotatedT2RawT1BfcBrainMask}"
    }

}

  
  # resample T1RawLabeledBrainMask with T1RawRotationTransform interpolating Binary/Linear and save in T1RotatedLabeledBrainMask
    if {[CheckOutputsNewer \
        [list ${T1RotatedLabeledBrainMask} ] \
        [list ${T1RawLabeledBrainMask} ${ScaledAtlasTemplateAvg} ${T1RawRotationTransform} ]] == false} {
      set interpolationType Linear
      set DataType "Signed-16bit"
      set useCoronalOrientation 0
      set result [Brains::itkUtils::ResampleBinaryImageFileWithTransformFile $T1RawLabeledBrainMask $ScaledAtlasTemplateAvg $T1RawRotationTransform $T1RotatedLabeledBrainMask $interpolationType $DataType $useCoronalOrientation]
      if { $result == 1 } {
        return 1
      }
      puts "Wrote ${T1RotatedLabeledBrainMask}"
    }


  # clip image T1RotatedBfcImage to mask T1RotatedLabeledBrainMask and save in temp T1RotatedBfcClipped
    set Temp_T1RotatedBfcClipped ${ScratchDirectory}/clipped_[file tail ${T1RotatedBfcImage}]
    if {[CheckOutputsNewer \
        [list ${Temp_T1RotatedBfcClipped} ] \
        [list ${T1RotatedBfcImage} ${T1RotatedLabeledBrainMask} ]] == false} {
      set result [Brains::AutoWorkup::ClipImage16 ${T1RotatedBfcImage} ${T1RotatedLabeledBrainMask} ${Temp_T1RotatedBfcClipped} 0]
      puts "Wrote ${Temp_T1RotatedBfcClipped}"
    }


  
    Brains::Utils::CheckFileExistance [ list ${T1RawRotationTransform} ${T1RotatedBayesianLabelMap} ${T1RotatedLabeledBrainMask} ${T1RotatedBfcImage} ${Temp_T1RotatedBfcClipped} ]
    
    return 0
  
  }
  
  
  # Brains::AutoWorkup::MapACPCAlignedTalairachParameters --
  #
  #  This function picks up the PC point, either from the ACPC_RawSpace_TextFile record of
  #  prior workup via the T1RawRotationTransform or from the average Atlas and its Talairach
  #  via the AtlasScalingTransform.  The AC point is statutory and constant, it is the center of the
  #  image, 127, 127, 127. The SLA and IRP will come from the T1RotatedLabeledBrainMask's bounding box.
  #
  # Arguments:
  #
  # Results:
  #  The transform mapping the Atlas is applied to Atlas Talairach Parameters.

  proc MapACPCAlignedTalairachParameters { AtlasTemplateAvg AtlasTalairach AtlasScalingTransform FORCE_ACPC_FROM_RAW ACPC_RawSpace_TextFile T1RawBfc T1RawRotationTransform T1RotatedLabeledBrainMask ScratchDirectory T1RawLabelMapACPCTalairach } {


    if {[string equal $FORCE_ACPC_FROM_RAW ACPC_FORCE] == 1} {
        set basisList [list ${AtlasTemplateAvg} ${AtlasTalairach} ${AtlasScalingTransform} ${ACPC_RawSpace_TextFile} ${T1RawRotationTransform} ${T1RotatedLabeledBrainMask}]
    } else {
        set basisList [list ${AtlasTemplateAvg} ${AtlasTalairach} ${AtlasScalingTransform} ${T1RawRotationTransform} ${T1RotatedLabeledBrainMask}]
    }
    if {[CheckOutputsNewer \
        [list ${T1RawLabelMapACPCTalairach} ] ${basisList}] == false} {


        set atlasTemplateImage [Brains::itk::LoadImage ${AtlasTemplateAvg} "Signed-16bit"]
        set ACPCImageRes [Brains::Utils::GetImageSpacing ${atlasTemplateImage}] 
        set ACPCImageDims [Brains::Utils::GetImageSize ${atlasTemplateImage}]
        set ACPCImageOrigin [Brains::Utils::GetImageOrigin ${atlasTemplateImage}]

        ${atlasTemplateImage} Delete

        set rawImage [Brains::itk::LoadImage ${T1RawBfc} "Signed-16bit"]
        set rawImageRes [Brains::Utils::GetImageSpacing ${rawImage}] 
        set rawImageDims [Brains::Utils::GetImageSize ${rawImage}]
        set rawImageOrigin [Brains::Utils::GetImageOrigin ${rawImage}]

        ${rawImage} Delete


        if {[string equal ${FORCE_ACPC_FROM_RAW} ACPC_FORCE] == 1} {

            ##  pick up the PC point from the ACPC_RawSpace_TextFile record of
            #   the prior workup, and transform via the T1RawRotationTransform

            set PC_Pt_in_TemplateInitSpaceMM [ GetACPCPointInMMFromCustomLandmark ${ACPC_RawSpace_TextFile} PC ${rawImageOrigin} ];
            puts "\nT1Raw PC point picked manually, PC_Pt_in_TemplateInitSpaceMM: ${PC_Pt_in_TemplateInitSpaceMM}\n"

            ## Note:  Landmarks in this custom file are given in MM.

            set T1RawRotationTxfm [Brains::itkUtils::readItkTransform ${T1RawRotationTransform} ]

            set InverseT1RawRotationTxfm [itkAffineTransformD3_New]
            $T1RawRotationTxfm GetInverse [$InverseT1RawRotationTxfm GetPointer]

            set originalPoint [itkPointD3]
            $originalPoint SetElement 0 [expr [lindex $PC_Pt_in_TemplateInitSpaceMM 0] ]
            $originalPoint SetElement 1 [expr [lindex $PC_Pt_in_TemplateInitSpaceMM 1] ]
            $originalPoint SetElement 2 [expr [lindex $PC_Pt_in_TemplateInitSpaceMM 2] ]

            set transformedPoint [$InverseT1RawRotationTxfm TransformPoint $originalPoint]

            set PC_InAlignedSpace_MM [list  [$transformedPoint GetElement 0] \
                                             [$transformedPoint GetElement 1] \
                                             [$transformedPoint GetElement 2]]
            puts "\nDesired location of PC point in InverseTransformedT1RawRotation, PC_InAlignedSpace_MM: ${PC_InAlignedSpace_MM}\n"

            $T1RawRotationTxfm Delete
            $InverseT1RawRotationTxfm Delete

            ##  NAIL THE AC POINT TO THE MIDDLE OF THE IMAGE
            #   based on work done by Brains::AutoWorkup::ShiftToPredefinedRawSpaceACPCLocations
            set AC_InAlignedSpace_MM [ list  0.0  0.0  0.0  ];

        } else {

            ##  pick up the AC and PC points from the average Atlas and its Talairach
            #   and transform via the AtlasScalingTransform

            set TalParametersInAtlasSpace [Brains::Utils::LoadSafe Talairach-parameters $AtlasTalairach ]
            set TalPointsInAtlasSpace [b2 get talairach points ${TalParametersInAtlasSpace}]
            b2 destroy talairach-parameters ${TalParametersInAtlasSpace}

            ## Note:  Landmarks in talairach file are given in voxel locations, so a conversion to MM is necessary.

            set AC_Pt_in_TemplateInitSpaceMM [Brains::Utils::ConvertFromIndexToMMLocation \
                      [list [Brains::Utils::ltraceSafe 0 ${TalPointsInAtlasSpace} 0 0] \
                             [Brains::Utils::ltraceSafe 0 ${TalPointsInAtlasSpace} 0 1] \
                             [Brains::Utils::ltraceSafe 0 ${TalPointsInAtlasSpace} 0 2]] $ACPCImageRes $ACPCImageOrigin]
            #set AC_Pt_in_TemplateInitSpaceMM [ list  0.0  0.0  0.0  ];

            set PC_Pt_in_TemplateInitSpaceMM [Brains::Utils::ConvertFromIndexToMMLocation \
                      [list [Brains::Utils::ltraceSafe 0 ${TalPointsInAtlasSpace} 1 0] \
                             [Brains::Utils::ltraceSafe 0 ${TalPointsInAtlasSpace} 1 1] \
                             [Brains::Utils::ltraceSafe 0 ${TalPointsInAtlasSpace} 1 2]] $ACPCImageRes $ACPCImageOrigin]


            set AtlasScalingTxfm [Brains::itkUtils::readItkTransform ${AtlasScalingTransform} ]

            set InverseAtlasScalingTxfm [itkAffineTransformD3_New]
            $AtlasScalingTxfm GetInverse [$InverseAtlasScalingTxfm GetPointer]

            set originalPoint [itkPointD3]
            $originalPoint SetElement 0 [expr [lindex $PC_Pt_in_TemplateInitSpaceMM 0] ]
            $originalPoint SetElement 1 [expr [lindex $PC_Pt_in_TemplateInitSpaceMM 1] ]
            $originalPoint SetElement 2 [expr [lindex $PC_Pt_in_TemplateInitSpaceMM 2] ]

            set transformedPoint [$InverseAtlasScalingTxfm TransformPoint $originalPoint]

            set PC_InAlignedSpace_MM [list [$transformedPoint GetElement 0] \
                                            [$transformedPoint GetElement 1] \
                                            [$transformedPoint GetElement 2]]
            puts "\nDesired location of PC point in InverseTransformedAtlasScaling, PC_InAlignedSpace_MM: ${PC_InAlignedSpace_MM}\n"


            set originalPoint [itkPointD3]
            $originalPoint SetElement 0 [expr [lindex $AC_Pt_in_TemplateInitSpaceMM 0] ]
            $originalPoint SetElement 1 [expr [lindex $AC_Pt_in_TemplateInitSpaceMM 1] ]
            $originalPoint SetElement 2 [expr [lindex $AC_Pt_in_TemplateInitSpaceMM 2] ]

            set transformedPoint [$InverseAtlasScalingTxfm TransformPoint $originalPoint]

            #set AC_InAlignedSpace_MM [ list  0.0  0.0  0.0  ];
            set AC_InAlignedSpace_MM [list [$transformedPoint GetElement 0] \
                                            [$transformedPoint GetElement 1] \
                                            [$transformedPoint GetElement 2]]
            puts "\nDesired location of AC point in InverseTransformedAtlasScaling, AC_InAlignedSpace_MM: ${AC_InAlignedSpace_MM}\n"

            $AtlasScalingTxfm Delete
            $InverseAtlasScalingTxfm Delete
        }

        ## The SLA and IRP will come from the T1RotatedLabeledBrainMask's bounding box.

        set T1RotatedLabeledBrainMaskImage [ Brains::Utils::LoadSafe image  ${T1RotatedLabeledBrainMask} ];
        set T1RotatedLabeledBrainMask [ b2 threshold image  ${T1RotatedLabeledBrainMaskImage} 1 ];
        set T1RotatedLabeledBrainBounds [ b2 measure bounds mask ${T1RotatedLabeledBrainMask} ];
        b2 destroy image ${T1RotatedLabeledBrainMaskImage}
        b2 destroy mask ${T1RotatedLabeledBrainMask}
        set SLA_Pt_InAlignedSpace_Index [list [Brains::Utils::ltraceSafe 0 ${T1RotatedLabeledBrainBounds} 1 1] \
                                               [Brains::Utils::ltraceSafe 0 ${T1RotatedLabeledBrainBounds} 3 1] \
                                               [Brains::Utils::ltraceSafe 0 ${T1RotatedLabeledBrainBounds} 5 1]]
        set IRP_Pt_InAlignedSpace_Index [list [Brains::Utils::ltraceSafe 0 ${T1RotatedLabeledBrainBounds} 0 1] \
                                               [Brains::Utils::ltraceSafe 0 ${T1RotatedLabeledBrainBounds} 2 1] \
                                               [Brains::Utils::ltraceSafe 0 ${T1RotatedLabeledBrainBounds} 4 1]]

        set AC_Pt_InAlignedSpace_Index [Brains::Utils::ConvertFromMMToIndexLocation  ${AC_InAlignedSpace_MM} ${ACPCImageRes} $ACPCImageOrigin ]
        set PC_Pt_InAlignedSpace_Index [Brains::Utils::ConvertFromMMToIndexLocation  ${PC_InAlignedSpace_MM} ${ACPCImageRes} $ACPCImageOrigin ]

        set Center_InAlignedSpace_Index [ list \
                        [expr ([lindex ${ACPCImageDims} 0] * 0.5) - 1 ] \
                        [expr ([lindex ${ACPCImageDims} 1] * 0.5) - 1 ] \
                        [expr ([lindex ${ACPCImageDims} 2] * 0.5) - 1 ] \
                        ];
        set AC_Loc_InAlignedSpace_Index [list [lindex ${Center_InAlignedSpace_Index} 0] \
                                               [lindex ${Center_InAlignedSpace_Index} 1] \
                                               [lindex ${AC_Pt_InAlignedSpace_Index} 2]]
        set PC_Loc_InAlignedSpace_Index [list [lindex ${Center_InAlignedSpace_Index} 0] \
                                               [lindex ${Center_InAlignedSpace_Index} 1] \
                                               [lindex ${PC_Pt_InAlignedSpace_Index} 2]]

        puts "AC:  ${AC_InAlignedSpace_MM}  mm;  ${AC_Pt_InAlignedSpace_Index}  voxels;  ${AC_Loc_InAlignedSpace_Index}  snapped;  "
        puts "PC:  ${PC_InAlignedSpace_MM}  mm;  ${PC_Pt_InAlignedSpace_Index}  voxels;  ${PC_Loc_InAlignedSpace_Index}  snapped;  "
        puts "SLA: ${SLA_Pt_InAlignedSpace_Index}"
        puts "IRP: ${IRP_Pt_InAlignedSpace_Index}"

        Brains::Utils::ExitOnFailure [ set TalParametersInAlignedSpace [b2 create talairach-parameters ${ACPCImageDims} ${ACPCImageRes} ${AC_Loc_InAlignedSpace_Index} ${PC_Loc_InAlignedSpace_Index} ${SLA_Pt_InAlignedSpace_Index} ${IRP_Pt_InAlignedSpace_Index}]] "creating TalParametersInAlignedSpace"
        Brains::Utils::ExitOnFailure [ b2 save talairach-parameters ${T1RawLabelMapACPCTalairach} brains3 ${TalParametersInAlignedSpace} ] "saving TalParametersInAlignedSpace to file ${T1RawLabelMapACPCTalairach}"
        b2 destroy talairach-parameters ${TalParametersInAlignedSpace}
    }
    
    return 0

  }
  
  
  
  
  
  # Brains::AutoWorkup::MultiModalAlignedBrainMaskAndT2PD --
  # 
  #  This function, FindACPCAlignmentUsingT1BrainMaskAndAtlas, does Phase 3.  
  #
  # Arguments:
  #  T2RawBfc
  #  PDRawBfc
  #  T1AlignedToACPCLabeledBrainMask
  #  T1AlignedToACPCBfcImage
  #  T1AlignedToACPCBayesianLabelMap
  #  T1AlignedToACPCLabeledBrainMask
  #  T1AlignedToACPCT1BfcBrainMask
  #  numberOfSamples
  #  minimumStepSize
  #  numberOfIterations
  #  InterpolationType
  #  ScratchDirectory
  #  T2RawAlignToACPCTransform
  #  T2AlignedToACPCBfcImage
  #  T2AlignedToACPCBfcBrainMask
  #  PDRawAlignToACPCTransform
  #  PDAlignedToACPCBfcImage
  #  MushAlignedToACPCBfcImage
  #  MushAlignedToACPCBfcBrainMask
  #  STAPLEAlignedToACPCBrainProbability
  #  STAPLEAlignedToACPCBrainMaskComponentTable
  #  STAPLEAlignedToACPCBfcBrainMask
  #
  # Results:
  #  Generates the T2 and PD aligned to T1 and Atlas, makes a mush brain and thresholds it,
  #  forms a STAPLE ground truth probability image from the 4 principal brain mask images found so far.
  
  proc MultiModalAlignedBrainMaskAndT2PD { T2RawBfc PDRawBfc T2RawT1BfcBrainMask T1AlignedToACPCLabeledBrainMask T1AlignedToACPCBfcImage T1AlignedToACPCBayesianLabelMap T1RawAlignToACPCTransform T1AlignedToACPCT1BfcBrainMask numberOfSamples minimumStepSize numberOfIterations InterpolationType ScratchDirectory T2RawAlignToACPCTransform T2AlignedToACPCBfcImage T2AlignedToACPCBfcBrainMask PDRawAlignToACPCTransform PDAlignedToACPCBfcImage MushAlignedToACPCBfcImage MushAlignedToACPCBfcBrainMask STAPLEAlignedToACPCBrainProbability STAPLEAlignedToACPCBrainMaskComponentTable STAPLEAlignedToACPCBfcBrainMask TrimmedMushAlignedToACPCBfcBrainMask } {
  
  
      puts -nonewline "======= EXECUTING Phase 3: MultiModalAlignedBrainMaskAndT2PD: "
      puts -nonewline "$T2RawBfc $PDRawBfc $T2RawT1BfcBrainMask $T1AlignedToACPCLabeledBrainMask $T1AlignedToACPCBfcImage "
      puts -nonewline "$T1AlignedToACPCBayesianLabelMap $T1RawAlignToACPCTransform "
      puts -nonewline "$T1AlignedToACPCT1BfcBrainMask "
      puts -nonewline "$numberOfSamples $minimumStepSize $numberOfIterations $InterpolationType $ScratchDirectory  "
      puts -nonewline "$T2RawAlignToACPCTransform $T2AlignedToACPCBfcImage $T2AlignedToACPCBfcBrainMask  "
      puts -nonewline "$PDRawAlignToACPCTransform $PDAlignedToACPCBfcImage  "
      puts -nonewline "$MushAlignedToACPCBfcImage $MushAlignedToACPCBfcBrainMask $STAPLEAlignedToACPCBrainProbability  "
      puts -nonewline "$STAPLEAlignedToACPCBrainMaskComponentTable $STAPLEAlignedToACPCBfcBrainMask $TrimmedMushAlignedToACPCBfcBrainMask"
      
      ## ## ##
      ##
      ##  This is atypical logic, but it means we can delete the ScratchDirectory such as delete_Phase_3,
      ##  and not irritate the method into re-running if the end results are up to date.
      ##  
        if {[file exists $ScratchDirectory] == 0} {
            if {[CheckOutputsNewer [list $T2RawAlignToACPCTransform $T2AlignedToACPCBfcImage $PDRawAlignToACPCTransform $PDAlignedToACPCBfcImage $MushAlignedToACPCBfcImage $MushAlignedToACPCBfcBrainMask $STAPLEAlignedToACPCBrainProbability $STAPLEAlignedToACPCBrainMaskComponentTable $STAPLEAlignedToACPCBfcBrainMask $TrimmedMushAlignedToACPCBfcBrainMask] \
                                    [list $T2RawBfc $PDRawBfc $T2RawT1BfcBrainMask $T1AlignedToACPCLabeledBrainMask $T1AlignedToACPCBfcImage $T1AlignedToACPCBayesianLabelMap] ] == true} {
                 return 0
            }
        }
        
      file mkdir $ScratchDirectory

  
    ##Phase Three:  Brains::AutoWorkup::FitRawImageToAlignedT1AndResample
    #
    Brains::AutoWorkup::FitRawImageToAlignedT1AndResample ${T2RawBfc} ${T2RawT1BfcBrainMask} ${T1RawAlignToACPCTransform} ${T1AlignedToACPCLabeledBrainMask} ${T1AlignedToACPCBfcImage} \
    $ScratchDirectory \
    ${T2RawAlignToACPCTransform} ${T2AlignedToACPCBfcImage} \
    ${numberOfSamples} ${minimumStepSize} ${numberOfIterations} ${InterpolationType}


  # resample T2RawT1BfcBrainMask with T2RawAlignToACPCTransform interpolating Binary/Linear and save in T2AlignedToACPCBfcBrainMask
    if {[CheckOutputsNewer \
        [list ${T2AlignedToACPCBfcBrainMask} ] \
        [list ${T2RawT1BfcBrainMask} ${T1AlignedToACPCBfcImage} ${T2RawAlignToACPCTransform} ]] == false} {
      set interpolationType Linear
      set DataType "Signed-16bit"
      set useCoronalOrientation 0
      set result [Brains::itkUtils::ResampleBinaryImageFileWithTransformFile $T2RawT1BfcBrainMask $T1AlignedToACPCBfcImage $T2RawAlignToACPCTransform $T2AlignedToACPCBfcBrainMask $interpolationType $DataType $useCoronalOrientation]
      if { $result == 1 } {
        return 1
      }
      puts "Wrote ${T2AlignedToACPCBfcBrainMask}"
    }


    if {[string length ${PDRawBfc}] > 1} {
        Brains::AutoWorkup::FitRawImageToAlignedT1AndResample ${PDRawBfc} ${T2RawT1BfcBrainMask} ${T1RawAlignToACPCTransform} ${T1AlignedToACPCLabeledBrainMask} ${T1AlignedToACPCBfcImage} \
        $ScratchDirectory \
        ${PDRawAlignToACPCTransform} ${PDAlignedToACPCBfcImage} \
        ${numberOfSamples} ${minimumStepSize} ${numberOfIterations} ${InterpolationType}
    }

if 0 {
    # approximate mush brain and its mask.
    set ErosionRadius 4
    set ClosingRadius 0
    Brains::AutoWorkup::MushImageAndMaskFromInitialWorkup ${T1AlignedToACPCBfcImage} ${T2AlignedToACPCBfcImage} ${T1AlignedToACPCBayesianLabelMap} \
    $ScratchDirectory \
    ${MushAlignedToACPCBfcImage} ${MushAlignedToACPCBfcBrainMask} $ErosionRadius $ClosingRadius
} else {

    # optimality-based mush brain and its mask.
    set ClosingRadius 0
    Brains::AutoWorkup::OptimalMushImageAndMaskFromInitialWorkup ${T1AlignedToACPCBfcImage} ${T2AlignedToACPCBfcImage} ${T1AlignedToACPCLabeledBrainMask} \
    $ScratchDirectory \
    ${MushAlignedToACPCBfcImage} ${MushAlignedToACPCBfcBrainMask} $ClosingRadius

    if 0 {
        set MushAlignedBrainMask_UsingEdgeImage [file rootname [file rootname ${MushAlignedToACPCBfcBrainMask}]]_UsingEdgeImage.nii.gz
        # optimality-based mush brain and its mask.
        set EdgeFormingRadius 3
        set ClosingRadius 0
        Brains::AutoWorkup::OptimalMushImageAndMaskFromInitialWorkup_UsingEdgeImage ${T1AlignedToACPCBfcImage} ${T2AlignedToACPCBfcImage} ${T1AlignedToACPCLabeledBrainMask} \
        $ScratchDirectory \
        ${MushAlignedToACPCBfcImage} ${MushAlignedToACPCBfcBrainMask} $EdgeFormingRadius $ClosingRadius
    }
}
    # Assemble the 4 principal brain masks found so far with the STAPLE image method.
    #  --- Make that three: removed ${T1AlignedToACPCLabeledBrainMask}
    set ProbabilityThreshold 0.99
    Brains::AutoWorkup::STAPLEImageAndMaskFromInitialWorkup [list ${MushAlignedToACPCBfcBrainMask}  ${T1AlignedToACPCT1BfcBrainMask} ${T2AlignedToACPCBfcBrainMask}] \
    $ScratchDirectory \
    ${STAPLEAlignedToACPCBrainProbability} ${STAPLEAlignedToACPCBrainMaskComponentTable} \
    ${STAPLEAlignedToACPCBfcBrainMask} ${TrimmedMushAlignedToACPCBfcBrainMask} ${ProbabilityThreshold}

    return 0
  
  }
  
  
  


  # Brains::AutoWorkup::FitRawImageToAlignedT1AndResample  --
  #
  #  This function, FitRawImageToAlignedT1AndResample, is called for T2 and PD separately in Phase 3.
  #
  # Arguments:
  #  T2RawBfcImage                 -  
  #  T1RotatedLabeledBrainMask     -  
  #  T1RotatedBfcImage             -  
  #  ScratchDirectory              -  
  #  T2RotationTransform           -  
  #  T2AlignedImage                -  
  #  numberOfSamples               -  
  #  minimumStepSize               -  
  #  numberOfIterations            -  
  #  
  # Results:
  #  The transform mapping the RawImage to the T1RotatedBfcImage is applied to produce an image aligned to T1ACPC.

  proc FitRawImageToAlignedT1AndResample { T2RawBfcImage T2RawT1BfcBrainMask T1RawAlignToACPCTransform T1RotatedLabeledBrainMask T1RotatedBfcImage ScratchDirectory T2RotationTransform T2AlignedImage numberOfSamples minimumStepSize numberOfIterations InterpolationType } {

        
      if {[file exists $T2RawBfcImage] == 0} {
        return 0
      }
        
        set BaseName [file rootname [file rootname [file tail $T2RawBfcImage]]]


      # clip image T1RotatedBfcImage to mask T1RotatedLabeledBrainMask and save in temp MovingT1BfcClipped
        set Temp_FixedT1BfcClipped ${ScratchDirectory}/clipped_0_[file tail ${T1RotatedBfcImage}]
        if {[CheckOutputsNewer \
            [list ${Temp_FixedT1BfcClipped} ] \
            [list ${T1RotatedBfcImage} ${T1RotatedLabeledBrainMask} ]] == false} {
          set T1OutsideValueWhenClipping 0

          set result [Brains::AutoWorkup::ClipImage16 ${T1RotatedBfcImage} ${T1RotatedLabeledBrainMask} ${Temp_FixedT1BfcClipped} ${T1OutsideValueWhenClipping}]
          puts "Wrote ${Temp_FixedT1BfcClipped}"
        }

      # clip image T2RawBfcImage to mask T2InitialBrainMask and save in temp MovingT2BfcClipped
        set Temp_MovingT2BfcClipped ${ScratchDirectory}/clipped_0_[file tail ${T2RawBfcImage}]
        if {[CheckOutputsNewer \
            [list ${Temp_MovingT2BfcClipped} ] \
            [list ${T2RawBfcImage} ${T2RawT1BfcBrainMask} ]] == false} {
          set T2OutsideValueWhenClipping 0

          set result [Brains::AutoWorkup::ClipImage16 ${T2RawBfcImage} ${T2RawT1BfcBrainMask} ${Temp_MovingT2BfcClipped} ${T2OutsideValueWhenClipping}]
          puts "Wrote ${Temp_MovingT2BfcClipped}"
        }

        
        # REFACTOR:  Sneaking a hint.
        if {[file exists ${T1RawAlignToACPCTransform}] == 1} {
        
            # set T2RawAlignedTransform [file dirname $T2RotationTransform]/delete_Ph_1/T2RawAligned.xfm
            # Should compose the transforms T2RawAlignedTransform and T1RawAlignToACPCTransform for a good hint.

            set translationScale 500
            # set minimumStepSizeFineGrained [expr ${minimumStepSize} * 0.5]
            set useCoronalOrientation 0
            set failureExitCode 1
            if {[CheckOutputsNewer [list $T2RotationTransform] [list $Temp_MovingT2BfcClipped $Temp_FixedT1BfcClipped $T1RawAlignToACPCTransform] ] == false} {
              set result [Brains::AutoWorkup::RigidInitializedRegistration $Temp_MovingT2BfcClipped $Temp_FixedT1BfcClipped \
                              $T1RawAlignToACPCTransform $T2RotationTransform \
                              $numberOfSamples $translationScale $numberOfIterations $minimumStepSize \
                              $useCoronalOrientation $failureExitCode]
              if { $result == 1 } {
                return 1
              }
            }
        } else {
        
            set translationScale 500
            # set minimumStepSizeFineGrained [expr ${minimumStepSize} * 0.5]
            set useCoronalOrientation 0
            set failureExitCode 1
            if {[CheckOutputsNewer [list $T2RotationTransform] [list $Temp_MovingT2BfcClipped $Temp_FixedT1BfcClipped] ] == false} {
              set result [Brains::AutoWorkup::RigidRegistration $Temp_MovingT2BfcClipped $Temp_FixedT1BfcClipped \
                              $T2RotationTransform \
                              $numberOfSamples $translationScale $numberOfIterations $minimumStepSize \
                              $useCoronalOrientation $failureExitCode]
              if { $result == 1 } {
                return 1
              }
            }
        }
        
        

        if {[CheckOutputsNewer [list $T2AlignedImage] [list $T2RawBfcImage $T2RotationTransform] ] == false} {
          set result [Brains::itkUtils::ResampleImageFileWithTransformFile $T2RawBfcImage $T1RotatedBfcImage $T2RotationTransform $T2AlignedImage ${InterpolationType} Signed-16bit $useCoronalOrientation]
          if { $result == 1 } {
            return 1
          }
        }

    return 0

  }



  # Brains::AutoWorkup::MushImageAndMaskFromInitialWorkup  --
  #
  #  This function, MushImageAndMaskFromInitialWorkup, does Phase 3, or rather, a follow-up part of it.
  #  Finds a mush image and mask from aligned t1, t2, and BayesianLabelMap images.
  #
  # Arguments:
  #  T1AlignedToACPCBfcImage            -  
  #  T2AlignedToACPCBfcImage            -  Must be a T2, not a PD, and coregistered to the T1.
  #  T1AlignedToACPCBayesianLabelMap    -  
  #  ScratchDirectory                   -  
  #  MushAlignedToACPCBfcImage          -  
  #  MushAlignedToACPCBfcBrainMask      -  
  #  
  # Results:
  #  The transform mapping the RawImage to the T1RotatedBfcImage is applied to produce an image aligned to T1ACPC.

  proc MushImageAndMaskFromInitialWorkup { T1AlignedToACPCBfcImage T2AlignedToACPCBfcImage T1AlignedToACPCBayesianLabelMap ScratchDirectory MushAlignedToACPCBfcImage MushAlignedToACPCBfcBrainMask {ErosionRadius 4} {ClosingRadius 0} } {
  
      set Temp_BayesianLabelMap_CSFLabelMask ${ScratchDirectory}/[file rootname [file rootname [file tail ${T1AlignedToACPCBayesianLabelMap}]]]_CSFLabelMask.nii.gz
      if {[CheckOutputsNewer [list $Temp_BayesianLabelMap_CSFLabelMask] [list $T1AlignedToACPCBayesianLabelMap] ] == false} {
        Brains::AutoWorkup::BinaryMaskImageRange 3 3 $T1AlignedToACPCBayesianLabelMap $Temp_BayesianLabelMap_CSFLabelMask "Signed-16bit"
      } 

      set Temp_BayesianLabelMap_GrayLabelMask ${ScratchDirectory}/[file rootname [file rootname [file tail ${T1AlignedToACPCBayesianLabelMap}]]]_GrayLabelMask.nii.gz
      if {[CheckOutputsNewer [list $Temp_BayesianLabelMap_GrayLabelMask] [list $T1AlignedToACPCBayesianLabelMap] ] == false} {
        Brains::AutoWorkup::BinaryMaskImageRange 4 4 $T1AlignedToACPCBayesianLabelMap $Temp_BayesianLabelMap_GrayLabelMask "Signed-16bit"
      } 

      set Temp_BayesianLabelMap_WhiteLabelMask ${ScratchDirectory}/[file rootname [file rootname [file tail ${T1AlignedToACPCBayesianLabelMap}]]]_WhiteLabelMask.nii.gz
      if {[CheckOutputsNewer [list $Temp_BayesianLabelMap_WhiteLabelMask] [list $T1AlignedToACPCBayesianLabelMap] ] == false} {
        Brains::AutoWorkup::BinaryMaskImageRange 5 5 $T1AlignedToACPCBayesianLabelMap $Temp_BayesianLabelMap_WhiteLabelMask "Signed-16bit"
      } 
      
      set Temp_BayesianLabelMap_CSFExemplarMask ${ScratchDirectory}/[file rootname [file rootname [file tail ${T1AlignedToACPCBayesianLabelMap}]]]_CSFExemplarMask.nii.gz
      if {[CheckOutputsNewer [list $Temp_BayesianLabelMap_CSFExemplarMask] [list $Temp_BayesianLabelMap_CSFLabelMask] ] == false} {
        Brains::AutoWorkup::BinaryMaskMorphology $Temp_BayesianLabelMap_CSFLabelMask $Temp_BayesianLabelMap_CSFExemplarMask Erode Ball 1 "Signed-16bit"
      } 
      
      set Temp_BayesianLabelMap_WhiteExemplarMask ${ScratchDirectory}/[file rootname [file rootname [file tail ${T1AlignedToACPCBayesianLabelMap}]]]_WhiteExemplarMask.nii.gz
      if {[CheckOutputsNewer [list $Temp_BayesianLabelMap_WhiteExemplarMask] [list $Temp_BayesianLabelMap_WhiteLabelMask] ] == false} {
        Brains::AutoWorkup::BinaryMaskMorphology $Temp_BayesianLabelMap_WhiteLabelMask $Temp_BayesianLabelMap_WhiteExemplarMask Erode Ball 1 "Signed-16bit"
      } 


      Brains::AutoWorkup::MushImageAndMask $T1AlignedToACPCBfcImage $T2AlignedToACPCBfcImage $Temp_BayesianLabelMap_CSFExemplarMask $Temp_BayesianLabelMap_WhiteExemplarMask $Temp_BayesianLabelMap_GrayLabelMask $ScratchDirectory $MushAlignedToACPCBfcImage $MushAlignedToACPCBfcBrainMask $ErosionRadius $ClosingRadius

    return 0

  }


  ##  Do not do this with a PD image.
  ##
  proc MushImageAndMask {T1AlignedToACPCBfcImage T2AlignedToACPCBfcImage Temp_BayesianLabelMap_CSFExemplarMask Temp_BayesianLabelMap_WhiteExemplarMask Temp_BayesianLabelMap_GrayLabelMask ScratchDirectory MushAlignedToACPCBfcImage MushAlignedToACPCBfcBrainMask {ErosionRadius 4} {ClosingRadius 0}} {
  
      if {[CheckOutputsNewer [list $MushAlignedToACPCBfcImage] [list $T1AlignedToACPCBfcImage $T2AlignedToACPCBfcImage $Temp_BayesianLabelMap_CSFExemplarMask $Temp_BayesianLabelMap_WhiteExemplarMask] ] == false} {
        
        # Get 4 mean measurements, rescale, sum and save.
        set T1Image [Brains::itk::LoadImage ${T1AlignedToACPCBfcImage} Float-Single]
        set T2Image [Brains::itk::LoadImage ${T2AlignedToACPCBfcImage} Float-Single]
        set CSFMask [Brains::itk::LoadImage ${Temp_BayesianLabelMap_CSFExemplarMask} Signed-16bit]
        set  WMMask [Brains::itk::LoadImage ${Temp_BayesianLabelMap_WhiteExemplarMask} Signed-16bit]
        
        set CSF_T1_Table [Brains::itk::measureLabelImageStatistics $CSFMask $T1Image]
        puts "CSF_T1_Table ${CSF_T1_Table}"
        set CSF_T2_Table [Brains::itk::measureLabelImageStatistics $CSFMask $T2Image]
        puts "CSF_T2_Table ${CSF_T2_Table}"
        set WM_T1_Table [Brains::itk::measureLabelImageStatistics $WMMask $T1Image]
        puts "WM_T1_Table ${WM_T1_Table}"
        set WM_T2_Table [Brains::itk::measureLabelImageStatistics $WMMask $T2Image]
        puts "WM_T2_Table ${WM_T2_Table}"

            set t1csf [Brains::Utils::ltraceSafe 0.0 $CSF_T1_Table 0 1 2]
            set t1wm [Brains::Utils::ltraceSafe 0.0 $WM_T1_Table 0 1 2]
            set t2csf [Brains::Utils::ltraceSafe 0.0 $CSF_T2_Table 0 1 2]
            set t2wm [Brains::Utils::ltraceSafe 0.0 $WM_T2_Table 0 1 2]
puts "\nt1csf: ${t1csf} t1wm: ${t1wm} t2csf: ${t2csf} t2wm: ${t2wm}\n"
            set xnumA [expr $t2csf / $t2wm]
            set xnum [expr 1 - $xnumA]
            set xdenA [expr $t2csf * $t1wm / $t2wm]
            set xden [expr $t1csf - $xdenA]
            set x [expr 128 * $xnum / $xden]
            set y1 [expr 128 / $t2wm]
            set y2 [expr $x * $t1wm / $t2wm]
            set y [expr $y1 - $y2]
            
        set NewT1Image [Brains::itk::ShiftScaleImage $T1Image 0 $x]
        set NewT2Image [Brains::itk::ShiftScaleImage $T2Image 0 $y]
        
        set ResultImage [Brains::itk::ImageMath $NewT1Image $NewT2Image Add Float-Single]
        Brains::itk::SaveImage ${ResultImage} ${MushAlignedToACPCBfcImage}
        ${T1Image} Delete
        ${T2Image} Delete
        ${CSFMask} Delete
        ${WMMask} Delete
        ${NewT1Image} Delete
        ${NewT2Image} Delete
        ${ResultImage} Delete
        
      } 

      if {[CheckOutputsNewer [list $MushAlignedToACPCBfcBrainMask] [list $MushAlignedToACPCBfcImage $Temp_BayesianLabelMap_GrayLabelMask] ] == false} {



if 0 {        
        # Threshold 128 +|- 46;   erode(4)-LargestFilledMask(0)-dilate(4)
        
        set Temp_MushThresholdBrainMask ${ScratchDirectory}/[file rootname [file rootname [file tail ${MushAlignedToACPCBfcBrainMask}]]]_Threshold.nii.gz
        if {[CheckOutputsNewer [list $Temp_MushThresholdBrainMask] [list $MushAlignedToACPCBfcImage] ] == false} {
          set lower [expr 128 - 46]
          set upper [expr 128 + 46]
          Brains::AutoWorkup::BinaryMaskImageRange $lower $upper $MushAlignedToACPCBfcImage $Temp_MushThresholdBrainMask "Signed-16bit"
        } 

        if {[CheckOutputsNewer [list $MushAlignedToACPCBfcBrainMask] [list $Temp_MushThresholdBrainMask] ] == false} {
          set thresholdImage [Brains::itk::LoadImage $Temp_MushThresholdBrainMask "Signed-16bit"]
          puts "erode by ${ErosionRadius}"
          set erodedMask [Brains::itk::ApplyStructuringElementToMaskImage $thresholdImage Erode Ball $ErosionRadius]
          puts "LargestRegionFilledMask 1 1 ${ClosingRadius}"
          set coreMaskImage [Brains::itk::LargestRegionFilledMask ${erodedMask} 1 1 $ClosingRadius]
          puts "dilate by ${ErosionRadius}"
          set LabelMask [Brains::itk::ApplyStructuringElementToMaskImage $coreMaskImage Dilate Ball ${ErosionRadius}]
          Brains::itk::SaveImage $LabelMask $MushAlignedToACPCBfcBrainMask
        } 

} else {

        # Threshold mean-gm +|- C * stddev-gm;   
        # erode(1)-LargestFilledMask(5)-erode(3)-dilate(4)-LargestFilledMask(0)
        
        set Temp_MushThresholdBrainMask ${ScratchDirectory}/[file rootname [file rootname [file tail ${MushAlignedToACPCBfcBrainMask}]]]_Threshold.nii.gz
        if {[CheckOutputsNewer [list $Temp_MushThresholdBrainMask] [list $MushAlignedToACPCBfcImage ${Temp_BayesianLabelMap_GrayLabelMask}] ] == false} {

          set ROIMask [Brains::itk::LoadImage ${Temp_BayesianLabelMap_GrayLabelMask} Signed-16bit]
          set MushImage [Brains::itk::LoadImage ${MushAlignedToACPCBfcImage} Float-Single]
          set ROI_Mush_Table [Brains::itk::measureLabelImageStatistics $ROIMask $MushImage]
          ${ROIMask} Delete
          ${MushImage} Delete
          
          set MushROIMean [Brains::Utils::ltraceSafe 0.0 $ROI_Mush_Table 0 1 2]
          set MushROIStdDev [Brains::Utils::ltraceSafe 0.0 $ROI_Mush_Table 0 4 2]          
          set lwindow [expr 1.96 * ${MushROIStdDev} ]
          set lower [expr int( ${MushROIMean} - $lwindow ) ]
          set uwindow [expr 4.0 * ${MushROIStdDev} ]
          set upper [expr int( 128.0 + $uwindow ) ]
          puts "\nMushROIMean ${MushROIMean} MushROIStdDev ${MushROIStdDev} lower ${lower} upper ${upper} "
          Brains::AutoWorkup::BinaryMaskImageRange $lower $upper $MushAlignedToACPCBfcImage $Temp_MushThresholdBrainMask "Signed-16bit"
        } 

        if {[CheckOutputsNewer [list $MushAlignedToACPCBfcBrainMask] [list $Temp_MushThresholdBrainMask] ] == false} {
          set thresholdImage [Brains::itk::LoadImage $Temp_MushThresholdBrainMask "Signed-16bit"]
          puts "erode by 1"
          set erodedMask [Brains::itk::ApplyStructuringElementToMaskImage $thresholdImage Erode Ball 1]
          set coreMaskImage [Brains::itk::LargestRegionFilledMask ${erodedMask} 1 1 5]
          puts "erode by 2"
          set cleanErosionMask [Brains::itk::ApplyStructuringElementToMaskImage $coreMaskImage Erode Ball 2]
          set connectedErosionMask [Brains::itk::LargestRegionFilledMask ${cleanErosionMask} 1 1 0]
          puts "dilate by 3"
          set cleanMask [Brains::itk::ApplyStructuringElementToMaskImage $connectedErosionMask Dilate Ball 3]
          Brains::itk::SaveImage $cleanMask $MushAlignedToACPCBfcBrainMask
          
          $thresholdImage Delete
          $erodedMask Delete
          $coreMaskImage Delete
          $cleanErosionMask Delete
          $connectedErosionMask Delete
          $cleanMask Delete
        } 

}



      } 
  }





  # Brains::AutoWorkup::OptimalMushImageAndMaskFromInitialWorkup  --
  #
  #  This function, MushImageAndMaskFromInitialWorkup, does Phase 3, or rather, a follow-up part of it.
  #  Finds a mush image and mask from aligned t1, t2, and rough BrainMask images.
  #
  # Arguments:
  #  T1AlignedToACPCBfcImage            -  
  #  T2AlignedToACPCBfcImage            -  May be a T2 or PD, and coregistered to the T1.
  #  AnyAlignedToACPCBrainMask          -  A rough brain region that happens to be available.
  #  ScratchDirectory                   -  
  #  MushAlignedToACPCBfcImage          -  
  #  MushAlignedToACPCBfcBrainMask      -  
  #  
  # Results:
  #  The transform mapping the RawImage to the T1RotatedBfcImage is applied to produce an image aligned to T1ACPC.

  proc OptimalMushImageAndMaskFromInitialWorkup_UsingEdgeImage { T1AlignedToACPCBfcImage T2AlignedToACPCBfcImage AnyAlignedToACPCBrainMask ScratchDirectory MushAlignedToACPCBfcImage MushAlignedToACPCBfcBrainMask {LesserEdgeFormingRadius 3} {ClosingRadius 5} } {
  
      
      if {[CheckOutputsNewer [list $MushAlignedToACPCBfcImage] [list $T1AlignedToACPCBfcImage $T2AlignedToACPCBfcImage $AnyAlignedToACPCBrainMask] ] == false} {
          OptimizeMushMixture $T1AlignedToACPCBfcImage $T2AlignedToACPCBfcImage $AnyAlignedToACPCBrainMask $MushAlignedToACPCBfcImage
      } 


      # set EdgeFormingRadius 1
      set Temp_MushThresholdBrainMask ${ScratchDirectory}/[file rootname [file rootname [file tail ${MushAlignedToACPCBfcBrainMask}]]]_Threshold.nii.gz
      if {[CheckOutputsNewer [list $MushAlignedToACPCBfcBrainMask $Temp_MushThresholdBrainMask] [list $MushAlignedToACPCBfcImage $AnyAlignedToACPCBrainMask] ] == false} {


        # Threshold mean-gm +|- C * stddev-gm;   
        # erode(1)-LargestFilledMask(5)-erode(3)-dilate(4)-LargestFilledMask(0)
        
        if {[CheckOutputsNewer [list $Temp_MushThresholdBrainMask] [list $MushAlignedToACPCBfcImage ${AnyAlignedToACPCBrainMask}] ] == false} {

          set mushImage [Brains::itk::LoadImage ${MushAlignedToACPCBfcImage} Float-Single]
          set Temp_MushEdgeImage ${ScratchDirectory}/[file rootname [file rootname [file tail ${MushAlignedToACPCBfcBrainMask}]]]_Edges.nii.gz
          set GreaterEdgeFormingRadius [expr ${LesserEdgeFormingRadius} + 1]
          puts "grayscale erode by ${GreaterEdgeFormingRadius}"

          set minImage [Brains::itk::ApplyStructuringElementToGrayscaleImage $mushImage Erode Ball ${GreaterEdgeFormingRadius}]
          puts "grayscale dilate by ${LesserEdgeFormingRadius}"

          set maxImage [Brains::itk::ApplyStructuringElementToGrayscaleImage $mushImage Dilate Ball ${LesserEdgeFormingRadius}]
          puts "subtract"
          set edgeImage [Brains::itk::ImageMath $maxImage $minImage Subtract Float-Single]
          ${minImage} Delete
          ${maxImage} Delete
          Brains::itk::SaveImage $edgeImage $Temp_MushEdgeImage

          set ROIMask [Brains::itk::LoadImage ${AnyAlignedToACPCBrainMask} Signed-16bit]
          set caution 7
          puts "erode by ${caution}"
 
          set CautiousROIMask [Brains::itk::ApplyStructuringElementToMaskImage ${ROIMask} Erode Ball ${caution}]
          ${ROIMask} Delete
          set ROI_Mush_Table [Brains::itk::measureLabelImageStatistics $CautiousROIMask $mushImage]
          set ROI_Edge_Table [Brains::itk::measureLabelImageStatistics $CautiousROIMask $edgeImage]
          ${CautiousROIMask} Delete

          set MushROIMean [Brains::Utils::ltraceSafe 0.0 $ROI_Mush_Table 0 1 2]
          set MushROIStdDev [Brains::Utils::ltraceSafe 0.0 $ROI_Mush_Table 0 4 2]          
          set lower [expr round( ${MushROIMean} * 0.5 ) ]
          set upper [expr round( ${MushROIMean} + ${MushROIStdDev} * 100.0 ) ]
          puts "\nMushROIMean ${MushROIMean} MushROIStdDev ${MushROIStdDev} lower ${lower} upper ${upper} "
          set threshToHeadMask [Brains::itk::BinaryThresholdImage ${mushImage} ${lower} ${upper} 0]
          ${mushImage} Delete
          set clipToHeadMask [Brains::itk::LargestRegionFilledMask ${threshToHeadMask} 1 1 10]
          ${threshToHeadMask} Delete

          set EdgeROIMean [Brains::Utils::ltraceSafe 0.0 $ROI_Edge_Table 0 1 2]
          set EdgeROIStdDev [Brains::Utils::ltraceSafe 0.0 $ROI_Edge_Table 0 4 2]          
          set lwindow [expr 0.1 * ${EdgeROIStdDev} - 0.5 ]
          set lower [expr round( 0.0 + $lwindow ) ]
          # round the lower bound down but the upper bound up.
          set uwindow [expr 1.0 * ${EdgeROIStdDev} + 0.5 ]
          set upper [expr round( ${EdgeROIMean} + $uwindow ) ]
          puts "\nEdgeROIMean ${EdgeROIMean} EdgeROIStdDev ${EdgeROIStdDev} lower ${lower} upper ${upper} "
          set threshToBrainMask [Brains::itk::BinaryThresholdImage ${edgeImage} ${lower} ${upper} 0]
          ${edgeImage} Delete

          set threshMask  [Brains::itk::ImageMath $threshToBrainMask $clipToHeadMask Minimum "Signed-16bit"]
          Brains::itk::SaveImage ${threshMask} ${Temp_MushThresholdBrainMask}
          
          ${threshMask} Delete
          ${threshToBrainMask} Delete
          ${clipToHeadMask} Delete
        } 

        if {[CheckOutputsNewer [list $MushAlignedToACPCBfcBrainMask] [list $Temp_MushThresholdBrainMask] ] == false} {
          ## REFACTOR:  Make this a fancy erosion clean function of two filenames and ErosionRadius > 0.
          set threshMask [Brains::itk::LoadImage $Temp_MushThresholdBrainMask "Signed-16bit"]
          set maskA ${threshMask};
          for {set up 3; set down 2} {${up} > 0} {incr up -1; incr down 1} {

            puts "erode by ${up}"
            ##REFACTOR:  This pair here could use principles of ClassicBrainCleanDura
            set erodedMask [Brains::itk::ApplyStructuringElementToMaskImage ${maskA} Erode Ball ${up}]
            set coreMask [Brains::itk::LargestRegionFilledMask ${erodedMask} 1 1 ${down}]
            lappend deletionList $coreMask
            ## Wasted fencepost at the end
            if {${up} > 1} {
              set expand [expr ${up} * 2]
              puts "dilate by ${expand}"
              set cleanMask [Brains::itk::ApplyStructuringElementToMaskImage $coreMask Dilate Ball ${expand}]
              puts "intersect plausible region with original threshold mask"
              set maskA  [Brains::itk::ImageMath $threshMask $cleanMask Minimum "Signed-16bit"]
              $erodedMask Delete
              lappend deletionList $cleanMask
              lappend deletionList $maskA
            }
          }
          set finish_up [expr 1 + 1 + ${LesserEdgeFormingRadius} ]
          # i.e., last erode plus edge thickness.
          puts "adjust by ${finish_up}"
          set adjustedMask [Brains::itk::ApplyStructuringElementToMaskImage ${coreMask} Dilate Ball ${finish_up}]
          set resultMask [Brains::itk::LargestRegionFilledMask ${adjustedMask} 1 1 ${ClosingRadius}]
          Brains::itk::SaveImage $resultMask $MushAlignedToACPCBfcBrainMask
          
          $threshMask Delete
          foreach deleteMe ${deletionList} { $deleteMe Delete }
          $adjustedMask Delete
          $resultMask Delete
        }
      } 
  }


  proc OptimalMushImageAndMaskFromInitialWorkup { T1AlignedToACPCBfcImage T2AlignedToACPCBfcImage AnyAlignedToACPCBrainMask ScratchDirectory MushAlignedToACPCBfcImage MushAlignedToACPCBfcBrainMask {ClosingRadius 5} } {
  
      if {[CheckOutputsNewer [list $MushAlignedToACPCBfcImage] [list $T1AlignedToACPCBfcImage $T2AlignedToACPCBfcImage $AnyAlignedToACPCBrainMask] ] == false} {
          OptimizeMushMixture $T1AlignedToACPCBfcImage $T2AlignedToACPCBfcImage $AnyAlignedToACPCBrainMask $MushAlignedToACPCBfcImage
      } 

      if {[CheckOutputsNewer [list $MushAlignedToACPCBfcBrainMask] [list $MushAlignedToACPCBfcImage $AnyAlignedToACPCBrainMask] ] == false} {
          MushPiece $MushAlignedToACPCBfcImage $AnyAlignedToACPCBrainMask -5.0 5.0 $ScratchDirectory $MushAlignedToACPCBfcBrainMask
      } 
  }




  proc OptimalMushImageAndMaskFromInitialWorkup_Bootstrapped { T1AlignedToACPCBfcImage T2AlignedToACPCBfcImage ScratchDirectory MushAlignedToACPCBfcImage MushAlignedToACPCBfcBrainMask {ClosingRadius 5} } {
  
      set AnyAlignedToACPCBrainMask ${ScratchDirectory}/[file rootname [file rootname [file tail ${MushAlignedToACPCBfcBrainMask}]]]_BootstrapMask.nii.gz
      if {[CheckOutputsNewer [list $AnyAlignedToACPCBrainMask] [list $T1AlignedToACPCBfcImage $T2AlignedToACPCBfcImage] ] == false} {

          set Temp_QuasiMushImage ${ScratchDirectory}/[file rootname [file rootname [file tail ${MushAlignedToACPCBfcImage}]]]_BootstrapImage.nii.gz
          if {[CheckOutputsNewer [list ${Temp_QuasiMushImage}] [list ${T1AlignedToACPCBfcImage} ${T2AlignedToACPCBfcImage}] ] == false} {
              set t1Image [Brains::itk::LoadImage ${T1AlignedToACPCBfcImage} Float-Single]
              set t2Image [Brains::itk::LoadImage ${T2AlignedToACPCBfcImage} Float-Single]
              set quasiMushImage [Brains::itk::ImageMath $t1Image $t2Image Add "Float-Single"]
              Brains::itk::SaveImage $quasiMushImage ${Temp_QuasiMushImage}
              $t1Image Delete
              $t2Image Delete
              $quasiMushImage Delete
          } 

          MushPiece $Temp_QuasiMushImage "." 0.5 3.0 $ScratchDirectory $AnyAlignedToACPCBrainMask

      } 

      if {[CheckOutputsNewer [list $MushAlignedToACPCBfcImage] [list $T1AlignedToACPCBfcImage $T2AlignedToACPCBfcImage $AnyAlignedToACPCBrainMask] ] == false} {
          OptimizeMushMixture $T1AlignedToACPCBfcImage $T2AlignedToACPCBfcImage $AnyAlignedToACPCBrainMask $MushAlignedToACPCBfcImage
      } 

      if {[CheckOutputsNewer [list $MushAlignedToACPCBfcBrainMask] [list $MushAlignedToACPCBfcImage $AnyAlignedToACPCBrainMask] ] == false} {
          MushPiece $MushAlignedToACPCBfcImage $AnyAlignedToACPCBrainMask -5.0 5.0 $ScratchDirectory $MushAlignedToACPCBfcBrainMask
      } 
  }




  proc MushPiece {MushAlignedToACPCBfcImage AnyAlignedToACPCBrainMask SpreadLower SpreadUpper ScratchDirectory MushAlignedToACPCBfcBrainMask} {
      set Temp_MushThresholdBrainMask ${ScratchDirectory}/[file rootname [file rootname [file tail ${MushAlignedToACPCBfcBrainMask}]]]_Mush${SpreadUpper}SigmaThreshold.nii.gz
      if {[CheckOutputsNewer [list $MushAlignedToACPCBfcBrainMask $Temp_MushThresholdBrainMask] [list $MushAlignedToACPCBfcImage $AnyAlignedToACPCBrainMask] ] == false} {

        if {[CheckOutputsNewer [list $Temp_MushThresholdBrainMask] [list $MushAlignedToACPCBfcImage ${AnyAlignedToACPCBrainMask}] ] == false} {

          set mushImage [Brains::itk::LoadImage ${MushAlignedToACPCBfcImage} Float-Single]

          if {[string length ${AnyAlignedToACPCBrainMask}] > 1} {
            set ROIMask [Brains::itk::LoadImage ${AnyAlignedToACPCBrainMask} Signed-16bit]
            set caution 7
            puts "erode by ${caution}"
            set CautiousROIMask [Brains::itk::ApplyStructuringElementToMaskImage ${ROIMask} Erode Ball ${caution}]
            ${ROIMask} Delete
            set ROI_Mush_Table [Brains::itk::measureLabelImageStatistics $CautiousROIMask $mushImage]
            ${CautiousROIMask} Delete
            set MushROIMean [Brains::Utils::ltraceSafe 0.0 $ROI_Mush_Table 0 1 2]
            set MushROIStdDev [Brains::Utils::ltraceSafe 0.0 $ROI_Mush_Table 0 4 2]          
          } else {
            set ROI_Mush_Table [Brains::itk::measureImageStatistics $mushImage]
            set MushROIMean [Brains::Utils::ltraceSafe 0.0 $ROI_Mush_Table 0 1]
            set MushROIStdDev [Brains::Utils::ltraceSafe 0.0 $ROI_Mush_Table 3 1]          
          }

          set lower [expr round( ${MushROIMean} * 0.5 ) ]
          set upper [expr round( ${MushROIMean} + ${MushROIStdDev} * 100.0 ) ]
          puts "\nMushROIMean ${MushROIMean} MushROIStdDev ${MushROIStdDev} lower ${lower} upper ${upper} "
          set threshToHeadMask [Brains::itk::BinaryThresholdImage ${mushImage} ${lower} ${upper} 0]
          set clipToHeadMask [Brains::itk::LargestRegionFilledMask ${threshToHeadMask} 1 1 10]
          ${threshToHeadMask} Delete



          set lwindow [expr ${SpreadLower} * ${MushROIStdDev} ]
          set lower [expr round( ${MushROIMean} + $lwindow ) ]
          # round the lower bound down but the upper bound up.
          set uwindow [expr ${SpreadUpper} * ${MushROIStdDev} ]
          set upper [expr round( ${MushROIMean} + $uwindow ) ]
          puts "\nMushROIMean ${MushROIMean} MushROIStdDev ${MushROIStdDev} lower ${lower} upper ${upper} "
          set threshToBrainMask [Brains::itk::BinaryThresholdImage ${mushImage} ${lower} ${upper} 0]
          ${mushImage} Delete

          set threshMask  [Brains::itk::ImageMath $threshToBrainMask $clipToHeadMask Minimum "Signed-16bit"]
          Brains::itk::SaveImage ${threshMask} ${Temp_MushThresholdBrainMask}
          
          ${threshMask} Delete
          ${threshToBrainMask} Delete
          ${clipToHeadMask} Delete
        } 

        if {[CheckOutputsNewer [list $MushAlignedToACPCBfcBrainMask] [list $Temp_MushThresholdBrainMask] ] == false} {
          ## REFACTOR:  Make this a fancy erosion clean function of two filenames and ErosionRadius > 0.
          set threshMask [Brains::itk::LoadImage $Temp_MushThresholdBrainMask "Signed-16bit"]

          set erodedMask [Brains::itk::ApplyStructuringElementToMaskImage ${threshMask} Erode Ball 3]
          $threshMask Delete
          set coreMask [Brains::itk::LargestRegionFilledMask ${erodedMask} 1 1 2]
          $erodedMask Delete
          set resultMask [Brains::itk::ApplyStructuringElementToMaskImage $coreMask Dilate Ball 3]
          $coreMask Delete

          Brains::itk::SaveImage $resultMask $MushAlignedToACPCBfcBrainMask
          $resultMask Delete
        }
      } 
  }


  # Brains::AutoWorkup::STAPLEImageAndMaskFromInitialWorkup  --
  #
  #  This function, STAPLEImageAndMaskFromInitialWorkup, does Phase 3, or rather, a follow-up part of it.
  #  Finds a consensus image optimizing rater sensitivity and specificity jointly with estimation of 
  #  ground truth probability.
  #
  # Arguments:
  #  BrainMaskFileNameList                 - for individual brain masks, see the call in AutoWorkupDriverForT1T2.
  #  ScratchDirectory                      -  
  #  STAPLEAlignedToACPCBrainProbability   - probabilistic ground truth from comparing the list of masks.
  #  STAPLEAlignedToACPCBfcBrainMask       - 
  #  
  # Results:
  #  The transform mapping the RawImage to the T1RotatedBfcImage is applied to produce an image aligned to T1ACPC.

  proc STAPLEImageAndMaskFromInitialWorkup { BrainMaskFileNameList ScratchDirectory STAPLEAlignedToACPCBrainProbability STAPLEAlignedToACPCBrainMaskComponentTable STAPLEAlignedToACPCBfcBrainMask TrimmedMushAlignedToACPCBfcBrainMask {ProbabilityThreshold 0.99} {aboveThresh 0.81} } {
  
      if {[CheckOutputsNewer [list ${STAPLEAlignedToACPCBrainProbability} ${STAPLEAlignedToACPCBrainMaskComponentTable}] $BrainMaskFileNameList ] == false} {

        set tbl [Brains::itk::JointCommonMaskEstimationFromSTAPLEFilter $BrainMaskFileNameList \
                             $STAPLEAlignedToACPCBrainProbability]
        set flpt [open ${STAPLEAlignedToACPCBrainMaskComponentTable} w]
        puts $flpt "${tbl}"
        close $flpt
        
      } else {
        set flpt [open ${STAPLEAlignedToACPCBrainMaskComponentTable}]
        gets $flpt tbl
        close $flpt
      }

      foreach line ${tbl} {
        puts "${line}"
      }

      set allAbove 0
      foreach line ${tbl} {
        if {[lindex $line 3] < $aboveThresh} { set allAbove -1 }
        if {[lindex $line 5] < $aboveThresh} { set allAbove -1 }
      }
      Brains::Utils::ExitOnFailure $allAbove "checking that every sensitivity and specificity are above $aboveThresh"
      

      if {[CheckOutputsNewer [list ${STAPLEAlignedToACPCBfcBrainMask}] [list ${STAPLEAlignedToACPCBrainProbability}]] == false} {
        
        Brains::AutoWorkup::BinaryMaskImageRange ${ProbabilityThreshold} 1.0 $STAPLEAlignedToACPCBrainProbability $STAPLEAlignedToACPCBfcBrainMask "Float-Single"
        
        #STAPLEBrainMaskFromProbability_usingB2 $STAPLEAlignedToACPCBrainProbability ${ProbabilityThreshold} 0.5 $ScratchDirectory [lindex ${BrainMaskFileNameList} 0] $STAPLEAlignedToACPCBfcBrainMask

      }
      
      set MushAlignedToACPCBfcBrainMask [lindex ${BrainMaskFileNameList} 0]
      if {[CheckOutputsNewer [list ${TrimmedMushAlignedToACPCBfcBrainMask}] [list ${MushAlignedToACPCBfcBrainMask} ${STAPLEAlignedToACPCBrainProbability}]] == false} {

        TrimMushBrainFromSTAPLEProbabilityLowerBound_usingB2 $STAPLEAlignedToACPCBrainProbability ${ProbabilityThreshold} $MushAlignedToACPCBfcBrainMask $ScratchDirectory $MushAlignedToACPCBfcBrainMask $TrimmedMushAlignedToACPCBfcBrainMask 

      }
      
      return $tbl
  }
  
  
  
  
  proc STAPLEBrainMaskFromProbability_usingB2 { STAPLEAlignedToACPCBrainProbability StrongProbabilityThreshold WeakProbabilityThreshold ScratchDirectory ExampleBrainMaskFileName STAPLEAlignedToACPCBfcBrainMask } {

      package require BrainsGlue
  
      set probImg [Brains::Utils::LoadSafe Image ${STAPLEAlignedToACPCBrainProbability} data-type= float-single]
      set strongMask [b2 threshold image $probImg $StrongProbabilityThreshold]
      set weakMask [b2 threshold image $probImg $WeakProbabilityThreshold]
      Brains::Utils::ExitOnFailure [set strongMaskBounds [b2 measure bounds mask $strongMask]] "measuring the bounds on Strong-thresholded probability mask";
      Brains::Utils::ExitOnFailure [set strongMaskDims [b2 get dims mask $strongMask]] "finding the dims on Strong-thresholded probability mask";
      set yInferior [Brains::Utils::ltraceSafe 0 ${strongMaskBounds} 2 1 ]
      set yMiddle [expr [Brains::Utils::ltraceSafe 0 ${strongMaskDims} 1 ] / 2 ]
      set LowerBoundMask [b2 split mask ${weakMask} y $yInferior +]
      set LowerMask [b2 split mask ${LowerBoundMask} y $yMiddle -]
      set UpperMask [b2 split mask ${strongMask} y $yMiddle +]
      set SplicedMask [b2 or masks $LowerMask $UpperMask]
      
      set firstMaskImage [b2 sum masks ${SplicedMask}]
      set secondMaskImage [b2 itkPermuteAxes ${firstMaskImage} 0 2 1]
      set brainMaskImage [b2 itkFlipImage ${secondMaskImage} 0 1 0]

      set NonConformingSplicedBrainMask ${ScratchDirectory}/NON_COMPLIANT_[file tail ${STAPLEAlignedToACPCBfcBrainMask}]
      Brains::itk::SaveImage ${brainMaskImage} ${NonConformingSplicedBrainMask}
      ImageConformity $NonConformingSplicedBrainMask $ExampleBrainMaskFileName $STAPLEAlignedToACPCBfcBrainMask

      b2 destroy image $probImg
      b2 destroy mask $strongMask
      b2 destroy mask $weakMask
      b2 destroy mask $LowerBoundMask
      b2 destroy mask $LowerMask
      b2 destroy mask $UpperMask
      b2 destroy mask $SplicedMask
      b2 destroy image $firstMaskImage
      b2 destroy image $secondMaskImage
      b2 destroy image $brainMaskImage
      
      return 0
  }
  
  
  
  proc SaveB2MaskInB3BinaryVolume { roiMask ExampleBrainMaskFileName ScratchDirectory BinaryVolumeFileName } {
      set firstMaskImage [b2 sum masks ${roiMask}]
      set secondMaskImage [b2 itkPermuteAxes ${firstMaskImage} 0 2 1]
      set roiMaskImage [b2 itkFlipImage ${secondMaskImage} 0 1 0]

      set NonConformingROIMask ${ScratchDirectory}/NON_COMPLIANT_[file tail ${BinaryVolumeFileName}]
      Brains::itk::SaveImage ${roiMaskImage} ${NonConformingROIMask}
      ImageConformity $NonConformingROIMask $ExampleBrainMaskFileName $BinaryVolumeFileName

      b2 destroy image $firstMaskImage
      b2 destroy image $secondMaskImage
      b2 destroy image $roiMaskImage
  }

  
  
  proc TrimMushBrainFromSTAPLEProbabilityLowerBound_usingB2 { STAPLEAlignedToACPCBrainProbability StrongProbabilityThreshold MushAlignedToACPCBfcBrainMask ScratchDirectory ExampleBrainMaskFileName TrimmedMushAlignedToACPCBfcBrainMask } {

      package require BrainsGlue
  
      set probImg [Brains::Utils::LoadSafe Image ${STAPLEAlignedToACPCBrainProbability} data-type= float-single]
      set strongMask [b2 threshold image $probImg $StrongProbabilityThreshold]
      Brains::Utils::ExitOnFailure [set strongMaskBounds [b2 measure bounds mask $strongMask]] "measuring the bounds on Strong-thresholded probability mask";
      Brains::Utils::ExitOnFailure [set strongMaskDims [b2 get dims mask $strongMask]] "finding the dims on Strong-thresholded probability mask";
      set mushMaskImg [Brains::Utils::LoadSafe Image ${MushAlignedToACPCBfcBrainMask} data-type= Signed-16bit]
      set mushMask [b2 threshold image $mushMaskImg 1]
      set yInferior [Brains::Utils::ltraceSafe 0 ${strongMaskBounds} 2 1 ]
      set yMiddle [expr [Brains::Utils::ltraceSafe 0 ${strongMaskDims} 1 ] / 2 ]
      set LowerBoundMask [b2 split mask ${mushMask} y $yInferior +]
      
      set firstMaskImage [b2 sum masks ${LowerBoundMask}]
      set secondMaskImage [b2 itkPermuteAxes ${firstMaskImage} 0 2 1]
      set brainMaskImage [b2 itkFlipImage ${secondMaskImage} 0 1 0]

      set NonConformingSplicedBrainMask ${ScratchDirectory}/NON_COMPLIANT_[file tail ${TrimmedMushAlignedToACPCBfcBrainMask}]
      Brains::itk::SaveImage ${brainMaskImage} ${NonConformingSplicedBrainMask}
      ImageConformity $NonConformingSplicedBrainMask $ExampleBrainMaskFileName $TrimmedMushAlignedToACPCBfcBrainMask

      b2 destroy image $probImg
      b2 destroy mask $strongMask
      b2 destroy image $mushMaskImg
      b2 destroy mask $mushMask
      b2 destroy mask $LowerBoundMask
      b2 destroy image $firstMaskImage
      b2 destroy image $secondMaskImage
      b2 destroy image $brainMaskImage
      
      return 0
  }


  # Brains::AutoWorkup::SignedDistance --
  #
  # Arguments:
  #  Read_MaskImage            
  #  Write_MaskDistanceImage             
  #
  # Results:
  
  proc SignedDistance { Read_MaskImage Write_MaskDistanceImage } {
    global errorCode
    set command "exec SignedDistance.exe"
    append command " ${Read_MaskImage}"
    append command " ${Write_MaskDistanceImage}"
    append command " >&@stdout"
    puts "SignedDistance command: ${command}"
    set errorFlag [catch ${command} Print_typescript]
    if {$errorFlag} {
        puts "${Print_typescript}"
        error "SignedDistance sustained error ${errorFlag}"
    }
    
    return $Write_MaskDistanceImage
  }

 

  # Brains::AutoWorkup::OptimizeMushMixture --
  #
  #  This function performs a mixture weighting over 2 images
  #  so as to jointly optimize the mean and variance on the given mask.
  #
  # Arguments:
  #  T1AlignedToACPCBfcImage 
  #  T2AlignedToACPCBfcImage      - this could also be PD.
  #  AnyAlignedToACPCBrainMask    - this is whatever rough BrainMask is available.
  #  MushAlignedToACPCBfcImage
  #  desiredMean 
  #  desiredVariance 
  #
  # Results:
  #  Returns the resulting mush image filename
  
  proc OptimizeMushMixture { T1AlignedToACPCBfcImage T2AlignedToACPCBfcImage AnyAlignedToACPCBrainMask \
                              MushAlignedToACPCBfcImage \
                             { desiredMean 10000.0 } { desiredVariance 0.0 } } {
    global errorCode
    set command "exec [Brains3ExecutablePath]/MixtureStatisticOptimizer"
    append command " --inputFirstVolume ${T1AlignedToACPCBfcImage}"
    append command " --inputSecondVolume ${T2AlignedToACPCBfcImage}"
    append command " --inputMaskVolume ${AnyAlignedToACPCBrainMask}"
    append command " --desiredMean ${desiredMean}"
    append command " --desiredVariance ${desiredVariance}"
    set weightsFile [file rootname [file rootname ${MushAlignedToACPCBfcImage}]]_OptimalMixtureWeights.txt
    append command " --outputWeightsFile ${weightsFile}"
    append command " --outputMixtureVolume ${MushAlignedToACPCBfcImage} >&@stdout"
    puts "OptimizeMushMixture command: ${command}"
    set errorFlag [catch ${command} Print_typescript]
    if {$errorFlag} {
        puts "${Print_typescript}"
        error "OptimizeMushMixture sustained error ${errorFlag}"
    }
    
    return $MushAlignedToACPCBfcImage
  }

 

 

  # Brains::AutoWorkup::RigidRegistration --
  #
  #  This function performs a rigid registration between
  #  two images using the BRAINSFit program
  #
  # Arguments:
  #  Read_movingimg            Moving Image
  #  Read_fixedimg             Fixed Image
  #  Write_MovingToFixedRigid  Resulting rigid transform
  #  samples                   Number of Spatial Samples
  #  translationScale          Translation Scale
  #  iterations                Number of Iterations
  #  minimumStepSize           Minimum step size
  #
  # Results:
  #  Returns the resulting transform filename
  
  proc RigidRegistration { Read_movingimg Read_fixedimg Write_MovingToFixedRigid \
                           { samples 300000 } { translationScale 1000 } \
                           { iterations 1500 } { minimumStepSize .0005 } \
                           { forceCoronal 0 } {failureExitCode 1} } {
    global errorCode
    set command "exec [Brains3ExecutablePath]/BRAINSFit"
    append command " --failureExitCode ${failureExitCode}"
    if {${failureExitCode} == 0} {
      append command " --writeTransformOnFailure"
    }
    append command " --fixedVolume ${Read_fixedimg}"
    append command " --movingVolume ${Read_movingimg}"
    append command " --fixedVolumeTimeIndex 0"
    append command " --movingVolumeTimeIndex 0"
    append command " --minimumStepSize ${minimumStepSize}"
    append command " --numberOfSamples ${samples}"
    append command " --numberOfIterations ${iterations}"
    append command " --transformType Rigid"
    append command " --spatialScale ${translationScale}"
    if {$forceCoronal} {
      append command " --forceImageOrientation Coronal"
      #append command " --explicitOrigins"
    }
    append command " --outputTransform ${Write_MovingToFixedRigid} >&@stdout"
    puts "RigidRegistration command: ${command}"
    set errorFlag [catch ${command} Print_typescript]
    if {$errorFlag} {
        puts "${Print_typescript}"
        error "RigidRegistration sustained error ${errorFlag}"
    }
    
    return $Write_MovingToFixedRigid
  }

 

  # Brains::AutoWorkup::RigidInitializedRegistration --
  #
  #  This function performs a rigid registration between
  #  two images using the BRAINSFit program
  #
  # Arguments:
  #  Read_movingimg            Moving Image
  #  Read_fixedimg             Fixed Image
  #  Write_MovingToFixedRigid  Resulting rigid transform
  #  samples                   Number of Spatial Samples
  #  translationScale          Translation Scale
  #  iterations                Number of Iterations
  #  minimumStepSize           Minimum step size
  #
  # Results:
  #  Returns the resulting transform filename
  
  proc RigidInitializedRegistration { Read_movingimg Read_fixedimg Read_InitialTransform Write_MovingToFixedRigid \
                           { samples 300000 } { translationScale 1000 } \
                           { iterations 1500 } { minimumStepSize .0005 } \
                           { forceCoronal 0 } {failureExitCode 1} } {
    global errorCode
    set command "exec [Brains3ExecutablePath]/BRAINSFit"
    append command " --failureExitCode ${failureExitCode}"
    if {${failureExitCode} == 0} {
      append command " --writeTransformOnFailure"
    }
    append command " --fixedVolume ${Read_fixedimg}"
    append command " --movingVolume ${Read_movingimg}"
    append command " --initialTransform ${Read_InitialTransform}"
    append command " --fixedVolumeTimeIndex 0"
    append command " --movingVolumeTimeIndex 0"
    append command " --minimumStepSize ${minimumStepSize}"
    append command " --numberOfSamples ${samples}"
    append command " --numberOfIterations ${iterations}"
    append command " --transformType Rigid"
    append command " --spatialScale ${translationScale}"
    if {$forceCoronal} {
      append command " --forceImageOrientation Coronal"
      #append command " --explicitOrigins"
    }
    append command " --outputTransform ${Write_MovingToFixedRigid} >&@stdout"
    puts "RigidRegistration command: ${command}"
    set errorFlag [catch ${command} Print_typescript]
    if {$errorFlag} {
        puts "${Print_typescript}"
        error "RigidRegistration sustained error ${errorFlag}"
    }
    
    return $Write_MovingToFixedRigid
  }



  # Brains::AutoWorkup::RigidMaskedRegistration --
  #
  #  This function performs a rigid registration between
  #  two images using the BRAINSFit program
  #
  # Arguments:
  #  Read_movingimg            Moving Image
  #  Read_fixedimg             Fixed Image
  #  Write_MovingToFixedRigid  Resulting rigid transform
  #  samples                   Number of Spatial Samples
  #  translationScale          Translation Scale
  #  iterations                Number of Iterations
  #  minimumStepSize           Minimum step size
  #
  # Results:
  #  Returns the resulting transform filename
  
  proc RigidMaskedRegistration { Read_movingimg Read_fixedimg Read_movingmask Read_fixedmask Write_MovingToFixedRigid \
                           { samples 300000 } { translationScale 1000 } \
                           { iterations 1500 } { minimumStepSize .0005 } \
                           { forceCoronal 0 } {failureExitCode 1} } {
    global errorCode
    set command "exec [Brains3ExecutablePath]/BRAINSFit"
    append command " --failureExitCode ${failureExitCode}"
    if {${failureExitCode} == 0} {
      append command " --writeTransformOnFailure"
    }
    append command " --fixedVolume ${Read_fixedimg}"
    append command " --movingVolume ${Read_movingimg}"
    append command " --fixedBinaryVolume ${Read_fixedmask}"
    append command " --movingBinaryVolume ${Read_movingmask}"
    append command " --fixedVolumeTimeIndex 0"
    append command " --movingVolumeTimeIndex 0"
    append command " --minimumStepSize ${minimumStepSize}"
    append command " --numberOfSamples ${samples}"
    append command " --numberOfIterations ${iterations}"
    append command " --transformType Rigid"
    append command " --spatialScale ${translationScale}"
    if {$forceCoronal} {
      append command " --forceImageOrientation Coronal"
      #append command " --explicitOrigins"
    }
    append command " --outputTransform ${Write_MovingToFixedRigid} >&@stdout"
    puts "RigidRegistration command: ${command}"
    set errorFlag [catch ${command} Print_typescript]
    if {$errorFlag} {
        puts "${Print_typescript}"
        error "RigidRegistration sustained error ${errorFlag}"
    }
    
    return $Write_MovingToFixedRigid
  }




  # Brains::AutoWorkup::RigidMaskedInitializedRegistration --
  #
  #  This function performs a rigid registration between
  #  two images using the BRAINSFit program
  #
  # Arguments:
  #  Read_movingimg            Moving Image
  #  Read_fixedimg             Fixed Image
  #  Write_MovingToFixedRigid  Resulting rigid transform
  #  samples                   Number of Spatial Samples
  #  translationScale          Translation Scale
  #  iterations                Number of Iterations
  #  minimumStepSize           Minimum step size
  #
  # Results:
  #  Returns the resulting transform filename
  
  proc RigidMaskedInitializedRegistration { Read_movingimg Read_fixedimg Read_movingmask Read_fixedmask Read_InitialTransform Write_MovingToFixedRigid \
                           { samples 300000 } { translationScale 1000 } \
                           { iterations 1500 } { minimumStepSize .0005 } \
                           { forceCoronal 0 } {failureExitCode 1} } {
    global errorCode
    set command "exec [Brains3ExecutablePath]/BRAINSFit"
    append command " --failureExitCode ${failureExitCode}"
    if {${failureExitCode} == 0} {
      append command " --writeTransformOnFailure"
    }
    append command " --fixedVolume ${Read_fixedimg}"
    append command " --movingVolume ${Read_movingimg}"
    append command " --fixedBinaryVolume ${Read_fixedmask}"
    append command " --movingBinaryVolume ${Read_movingmask}"
    append command " --initialTransform ${Read_InitialTransform}"
    append command " --fixedVolumeTimeIndex 0"
    append command " --movingVolumeTimeIndex 0"
    append command " --minimumStepSize ${minimumStepSize}"
    append command " --numberOfSamples ${samples}"
    append command " --numberOfIterations ${iterations}"
    append command " --transformType Rigid"
    append command " --spatialScale ${translationScale}"
    if {$forceCoronal} {
      append command " --forceImageOrientation Coronal"
      #append command " --explicitOrigins"
    }
    append command " --outputTransform ${Write_MovingToFixedRigid} >&@stdout"
    puts "RigidRegistration command: ${command}"
    set errorFlag [catch ${command} Print_typescript]
    if {$errorFlag} {
        puts "${Print_typescript}"
        error "RigidRegistration sustained error ${errorFlag}"
    }
    
    return $Write_MovingToFixedRigid
  }





  # Brains::AutoWorkup::Affine9Registration --
  #
  #  This function performs an affine registration between
  #  two images using the BRAINSFit program
  #
  # Arguments:
  #  MovingImage               Moving Image filename
  #  FixedImage                Fixed Image filename
  #  InitialTransform          Initial transform filename
  #  ResultFreeScaleTransform  Resulting re-scaled affine transform filename
  #  ResultRigidTransform      Resulting rigid transform filename
  #  samples                   Number of Spatial Samples
  #  translationScale          Translation Scale
  #  iterations                Number of Iterations
  #  minimumStepSize           Minimum step size
  #
  # Results:
  #  Returns the resulting transform filename
    
  proc Affine9Registration { MovingImage FixedImage InitialTransform \
                            ResultFreeScaleTransform ResultRigidTransform \
                            {samples 1000000 } {translationScale 1000 } {iterations 500 } \
                            {minimumStepSize .0005 } {failureExitCode 1} } {

      global errorCode
      set command "exec [Brains3ExecutablePath]/BRAINSFit"
      append command " --failureExitCode ${failureExitCode}"
      if {${failureExitCode} == 0} {
        append command " --writeTransformOnFailure"
      }
      append command " --fixedVolume $FixedImage"
      append command " --movingVolume $MovingImage"
      append command " --fixedVolumeTimeIndex 0"
      append command " --movingVolumeTimeIndex 0"
      append command " --minimumStepSize ${minimumStepSize}"
      append command " --numberOfSamples ${samples}"
      append command " --numberOfIterations ${iterations}"
      append command " --transformType ScaleVersor3D"
      append command " --spatialScale ${translationScale}"
      if {[string length $InitialTransform] > 0} {
          append command " --initialTransform $InitialTransform"
      }
      append command " --strippedOutputTransform $ResultRigidTransform"
      append command " --outputTransform $ResultFreeScaleTransform >&@stdout"
      puts "Affine9Registration  command: ${command}"
      set errorFlag [catch ${command} Print_typescript]
      if {$errorFlag} {
          puts "${Print_typescript}"
          error "Affine9Registration sustained error ${errorFlag}"
      }
      
      return $ResultFreeScaleTransform
  }


  # Brains::AutoWorkup::Affine9MaskedRegistration --
  #
  #  This function performs an affine registration between
  #  two images using the BRAINSFit program
  #
  # Arguments:
  #  MovingImage               Moving Image filename
  #  FixedImage                Fixed Image filename
  #  MovingMaskImage           Moving Mask Image filename
  #  FixedMaskImage            Fixed Mask Image filename
  #  InitialTransform          Initial transform filename
  #  ResultFreeScaleTransform  Resulting re-scaled affine transform filename
  #  ResultRigidTransform      Resulting rigid transform filename
  #  samples                   Number of Spatial Samples
  #  translationScale          Translation Scale
  #  iterations                Number of Iterations
  #  minimumStepSize           Minimum step size
  #
  # Results:
  #  Returns the resulting transform filename
    
  proc Affine9MaskedRegistration { MovingImage FixedImage MovingMaskImage FixedMaskImage InitialTransform \
                            ResultFreeScaleTransform ResultRigidTransform \
                            {samples 1000000 } {translationScale 1000 } {iterations 500 } \
                            {minimumStepSize .0005 } {failureExitCode 1} } {

      global errorCode
      set command "exec [Brains3ExecutablePath]/BRAINSFit"
      append command " --failureExitCode ${failureExitCode}"
      if {${failureExitCode} == 0} {
        append command " --writeTransformOnFailure"
      }
      append command " --fixedVolume $FixedImage"
      append command " --movingVolume $MovingImage"
      append command " --fixedBinaryVolume $FixedMaskImage"
      append command " --movingBinaryVolume $MovingMaskImage"
      append command " --fixedVolumeTimeIndex 0"
      append command " --movingVolumeTimeIndex 0"
      append command " --minimumStepSize ${minimumStepSize}"
      append command " --numberOfSamples ${samples}"
      append command " --numberOfIterations ${iterations}"
      append command " --transformType ScaleVersor3D"
      append command " --spatialScale ${translationScale}"
      if {[string length $InitialTransform] > 0} {
          append command " --initialTransform $InitialTransform"
      }
      append command " --strippedOutputTransform $ResultRigidTransform"
      append command " --outputTransform $ResultFreeScaleTransform >&@stdout"
      puts "Affine9Registration  command: ${command}"
      set errorFlag [catch ${command} Print_typescript]
      if {$errorFlag} {
          puts "${Print_typescript}"
          error "Affine9Registration sustained error ${errorFlag}"
      }
      
      return $ResultFreeScaleTransform
  }




  # Brains::AutoWorkup::NineParameterImageToTemplateMIRegistration --
  #
  #  This function performs a 9 parameter 
  #  mutualinformation registration by bootstrapping with 
  #  rigid, then performaning AffineRegistration
  #  !  Now changed to permit testing of whether to actually use the masks.
  #
  # Arguments:
  #       MovingImage 
  #       FixedImage 
  #       MovingMaskImage 
  #       FixedMaskImage 
  #       Write_MovingToFixedBootRotation 
  #       Write_MovingToFixedFreeScale 
  #       Write_MovingToFixedRigid 
  #       s (1000000) samples per MutualInformation comparison
  #       ts (1000) translation scale
  #       n (500) maximum number of iterations in gradient descent
  #       min (.0005) smallest step size, a criterion for convergence
            
  # Results:
  #  The input file is successfully copied

  proc NineParameterImageToTemplateMIRegistration { MovingImage FixedImage \
               MovingMaskImage FixedMaskImage \
               Write_MovingToFixedBootRotation Write_MovingToFixedFreeScale \
               Write_MovingToFixedRigid { s 1000000 } { ts 1000 } { n 500 } { min .0005 } } {

    global env;
    if {[info exists env(AffineRegistrationPoints)] == 0} {
      set numPoints $s;
    } else {
      set numPoints ${env(AffineRegistrationPoints)};
    }

if 0 {
    ##  Not doing masked fits.
    
    set outputList [list ${Write_MovingToFixedBootRotation} ]
    set inputList [list ${MovingImage} ${FixedImage} ]
    if {[CheckOutputsNewer $outputList $inputList ] == false} {
      Brains::AutoWorkup::RigidMaskedRegistration  ${MovingImage}  \
                          ${FixedImage} \
                          ${MovingMaskImage}  \
                          ${FixedMaskImage} \
                          ${Write_MovingToFixedBootRotation} \
                          $numPoints $ts $n $min
    }

    set outputList [list ${Write_MovingToFixedFreeScale} ${Write_MovingToFixedRigid} ]
    set inputList [list ${MovingImage} ${FixedImage} ${Write_MovingToFixedBootRotation} ]
    if {[CheckOutputsNewer $outputList $inputList ] == false} {
      Brains::AutoWorkup::Affine9MaskedRegistration ${MovingImage}  \
                          ${FixedImage}  \
                          ${MovingMaskImage}  \
                          ${FixedMaskImage} \
                          ${Write_MovingToFixedBootRotation}  \
                          ${Write_MovingToFixedFreeScale} \
                          ${Write_MovingToFixedRigid} \
                          ${numPoints} $ts $n $min;
    }

} else {
    ## Not doing masked fits.
    
    set outputList [list ${Write_MovingToFixedBootRotation} ]
    set inputList [list ${MovingImage} ${FixedImage} ]
    if {[CheckOutputsNewer $outputList $inputList ] == false} {
      Brains::AutoWorkup::RigidRegistration  ${MovingImage}  \
                          ${FixedImage} \
                          ${Write_MovingToFixedBootRotation} \
                          $numPoints $ts $n $min
    }

    set outputList [list ${Write_MovingToFixedFreeScale} ${Write_MovingToFixedRigid} ]
    set inputList [list ${MovingImage} ${FixedImage} ${Write_MovingToFixedBootRotation} ]
    if {[CheckOutputsNewer $outputList $inputList ] == false} {
      Brains::AutoWorkup::Affine9Registration ${MovingImage}  \
                          ${FixedImage}  \
                          ${Write_MovingToFixedBootRotation}  \
                          ${Write_MovingToFixedFreeScale} \
                          ${Write_MovingToFixedRigid} \
                          ${numPoints} $ts $n $min;
    }


}

  } 




  
  # Brains::AutoWorkup::ClipImage16 --
  #
  #  Little proc to clip 16 bit images. This
  #  works on filenames.
  #
  # Arguments:
  #  OrigImageFN         Input image filename
  #  OrigMaskFN          Input mask filename
  #  OutputImageFN       Output clipped image filename
  #
  # Results:
  #  The OutputImageFN on successful completion
  
  proc ClipImage16 { OrigImageFN OrigMaskFN OutputImageFN {OutsideValue 0} } {
  
      set origimg [Brains::itk::LoadImage $OrigImageFN Signed-16bit]
      set origmask [Brains::itk::LoadImage $OrigMaskFN Signed-16bit]
      set output [Brains::itk::MaskImage $origimg $origmask $OutsideValue ];
      Brains::itk::SaveImage $output $OutputImageFN
      $origimg Delete
      $origmask Delete
      $output Delete

      return $OutputImageFN
  }


  proc WriteLabelImageStatisticsToFile { T1RawBfc T1RawBayesianLabelMap StatsFile {DataType Signed-16bit} } {
      set T1BfcImage [Brains::itk::LoadImage ${T1RawBfc} ${DataType}]
      set T1RawBayesianLabelMapImage [Brains::itk::LoadImage ${T1RawBayesianLabelMap} ${DataType}]
      set statisticsTable [Brains::itk::measureLabelImageStatistics ${T1RawBayesianLabelMapImage} ${T1BfcImage}]
      set flpt [open ${StatsFile} w]
      puts $flpt "${statisticsTable}"
      close $flpt
      ${T1BfcImage} Delete
      ${T1RawBayesianLabelMapImage} Delete

      return ${StatsFile}
  }




  # Brains::AutoWorkup::FindYDimFloorClippingPlane --
  #
  #  The 41 in this function assumes that the AC point is 
  #  centered in the image and that the brain takes up about 
  #  the middle 1/3 of the image space.
  #  DEBUG: This computation could be improved by using an 
  #         estimate of the brain image mask size for clipping purposes.
  #
  # Arguments:
  #  Image          Input Image
  #  DesiredMM      Desired mm clipping of the image
  #
  # Results:
  #  Returns the resulting clipped image

  proc FindYDimFloorClippingPlane { Image { DesiredMM 41} } {
    set resolutions [Brains::Utils::GetImageSpacing $Image]
    return [expr $DesiredMM / [lindex $resolutions 1] ]
  }
  
  

  # Brains::AutoWorkup::YDimFloorClipImage --
  #
  #  The image that should be floor clipped
  #  DEBUG: This computation could be improved by using 
  #  an estimate of the brain image mask size for clipping 
  #  purposes.
  #
  # Arguments:
  #  ImageToFloorClip          Input Image
  #
  # Results:
  #  Returns the resulting clipped image

  proc YDimFloorClipImage { ImageToFloorClip } {
    set TissueImageMaskFromThreshold [brains::itk::ThresholdImage $ImageToFloorClip 1 255]
    
    ###VAM - Is there an ITK function for split mask ????
    set LowerBoundMask [b2 split mask ${TissueImageMaskFromThreshold} y [FindYDimFloorClippingPlane  ${ImageToFloorClip}] +];
    
    set FinalImage [brains::itk::MaskImage $ImageToFloorClip $LowerBoundMask]

    Brains::Utils::ExitOnFailure [ b2 destroy mask $LowerBoundMask ] "destroying LowerBoundMask"
    Brains::Utils::ExitOnFailure [ b2 destroy mask $TissueImageMaskFromThreshold ] "destroying TissueImageMaskFromThreshold"
    return ${FinalImage}
  }



  # Brains::AutoWorkup::ComputeMaskBoundingBoxScaleTransformAndSave --
  #
  proc ComputeMaskBoundingBoxScaleTransformAndSave { Temp_AtlasBrainMask Temp_InitialOrientedBrainMask AtlasScalingTransform } {
        set AtlasBrainScalingToSubjectTransform [ ComputeMaskBoundingBoxScaleTransform ${Temp_AtlasBrainMask} ${Temp_InitialOrientedBrainMask} ]
        ## We already employed a GetPointer around the return value, inside ComputeMaskBoundingBoxScaleTransform.
        Brains::itkUtils::WriteItkTransform ${AtlasBrainScalingToSubjectTransform} ${AtlasScalingTransform}
        puts "Wrote transform ${AtlasScalingTransform}"
  }


  # Brains::AutoWorkup::ComputeMaskBoundingBoxScaleTransform --
  #
  #  Create scaling from the center of the image such 
  #  that a transform is created that matches the global 
  #  scale of the two bounding boxes.
  #
  #  Requirement: this proc only works when the fixed 
  #  mask and the moving mask have the same resolutions.
  #
  # Arguments:
  #  ReadFrom_file       Input file to copy
  #  WriteOut_file       Output destination file
  #
  # Results:
  #  The input file is successfully copied

  proc ComputeMaskBoundingBoxScaleTransform { MovingMaskImageName FixedMaskImageName  } {

    package require BrainsGlue

    puts "ComputeMaskBoundingBoxScaleTransform"
    #puts "    MovingMask filename:  ${MovingMaskImageName}"
    #puts "    FixedMask filename:  ${FixedMaskImageName}"
    set MovingMaskImage [Brains::Utils::LoadSafe Image ${MovingMaskImageName} data-type= unsigned-8bit];
    set FixedMaskImage [Brains::Utils::LoadSafe Image ${FixedMaskImageName} data-type= unsigned-8bit];
    set MovingMaskOrigin [Brains::Utils::GetImageOrigin ${MovingMaskImage}] 
    set FixedMaskOrigin [Brains::Utils::GetImageOrigin ${FixedMaskImage}] 
    set MovingMask [b2 threshold image ${MovingMaskImage} 1];
    set FixedMask [b2 threshold image ${FixedMaskImage} 1];
    b2 destroy image ${MovingMaskImage};
    b2 destroy image ${FixedMaskImage};
    
    set FixedMaskdims [b2 get dims mask ${FixedMask}];
    set FixedMaskres [b2 get res mask ${FixedMask}];
    #puts "    FixedMask stats:  ${FixedMaskdims}  ${FixedMaskres}"
    Brains::Utils::ExitOnFailure [set FixedMaskbounds [b2 measure bounds mask $FixedMask]] "measuring the bounds on fixed mask";
    set FixedMaskright [ expr [ lindex ${FixedMaskres} 0 ] * [Brains::Utils::ltraceSafe 0 ${FixedMaskbounds} 0 1 ]];
    set FixedMaskleft  [ expr [ lindex ${FixedMaskres} 0 ] * [Brains::Utils::ltraceSafe 0 ${FixedMaskbounds} 1 1 ]];
    set FixedMaskinf   [ expr [ lindex ${FixedMaskres} 1 ] * [Brains::Utils::ltraceSafe 0 ${FixedMaskbounds} 2 1 ]];
    set FixedMasksup   [ expr [ lindex ${FixedMaskres} 1 ] * [Brains::Utils::ltraceSafe 0 ${FixedMaskbounds} 3 1 ]];
    set FixedMaskpost  [ expr [ lindex ${FixedMaskres} 2 ] * [Brains::Utils::ltraceSafe 0 ${FixedMaskbounds} 4 1 ]];
    set FixedMaskant   [ expr [ lindex ${FixedMaskres} 2 ] * [Brains::Utils::ltraceSafe 0 ${FixedMaskbounds} 5 1 ]];
    puts "    FixedMask positions:  right ${FixedMaskright} left ${FixedMaskleft}"
    puts "    FixedMask positions:  inf ${FixedMaskinf} sup ${FixedMasksup}"
    puts "    FixedMask positions:  post ${FixedMaskpost} ant ${FixedMaskant}"
   

    set MovingMaskdims [b2 get dims mask ${MovingMask}];
    set MovingMaskres [b2 get res mask ${MovingMask}];
    #puts "    MovingMask stats:  ${MovingMaskdims}  ${MovingMaskres}"
    Brains::Utils::ExitOnFailure [set MovingMaskbounds [b2 measure bounds mask $MovingMask]] "measuring the bounds on moving mask";
    set MovingMaskright [ expr [lindex $MovingMaskres 0 ] * [Brains::Utils::ltraceSafe 0 ${MovingMaskbounds} 0 1 ] ];
    set MovingMaskleft  [ expr [lindex $MovingMaskres 0 ] * [Brains::Utils::ltraceSafe 0 ${MovingMaskbounds} 1 1 ] ];
    set MovingMaskinf   [ expr [lindex $MovingMaskres 1 ] * [Brains::Utils::ltraceSafe 0 ${MovingMaskbounds} 2 1 ] ];
    set MovingMasksup   [ expr [lindex $MovingMaskres 1 ] * [Brains::Utils::ltraceSafe 0 ${MovingMaskbounds} 3 1 ] ];
    set MovingMaskpost  [ expr [lindex $MovingMaskres 2 ] * [Brains::Utils::ltraceSafe 0 ${MovingMaskbounds} 4 1 ] ];
    set MovingMaskant   [ expr [lindex $MovingMaskres 2 ] * [Brains::Utils::ltraceSafe 0 ${MovingMaskbounds} 5 1 ] ];
    puts "    MovingMask positions:  right ${MovingMaskright} left ${MovingMaskleft}"
    puts "    MovingMask positions:  inf ${MovingMaskinf} sup ${MovingMasksup}"
    puts "    MovingMask positions:  post ${MovingMaskpost} ant ${MovingMaskant}"

    b2 destroy mask ${MovingMask};
    b2 destroy mask ${FixedMask};

    foreach i {0 1 2} {
      if { [lindex ${FixedMaskdims} ${i}] != [lindex ${MovingMaskdims} ${i}] } {
        Brains::Utils::ExitOnFailure -1 "${i}th dims of Fixed and Moving masks differ: ${FixedMaskdims} != ${MovingMaskdims}";
      }
      if { [lindex ${FixedMaskres} ${i}] != [lindex ${MovingMaskres} ${i}] } {
        Brains::Utils::ExitOnFailure -1 "${i}th res of Fixed and Moving masks differ: ${FixedMaskres} != ${MovingMaskres}";
      }
    }
    
    set midpointsIndex [ list \
      [expr [lindex $FixedMaskdims 0 ] * 0.5 ] \
      [expr [lindex $FixedMaskdims 1 ] * 0.5 ] \
      [expr [lindex $FixedMaskdims 2 ] * 0.5 ] \
      ]
    set MidpointRealCenter [Brains::Utils::ConvertFromIndexToMMLocation  ${midpointsIndex} ${FixedMaskres} ${FixedMaskOrigin} ] ;
    #puts "MidpointRealCenter ${MidpointRealCenter}"
    
    ## NOTE 1.0 is needed to force floating point computation
    set sx [expr ($MovingMaskleft - $MovingMaskright) * 1.0 / ($FixedMaskleft - $FixedMaskright) ];
    set sy [expr ($MovingMasksup - $MovingMaskinf) * 1.0 / ($FixedMasksup - $FixedMaskinf) ];
    set sz [expr ($MovingMaskant - $MovingMaskpost) * 1.0 / ($FixedMaskant - $FixedMaskpost) ];

    ## NOTE negating dy seems arbitrary, but so is complementing s[xyz] against 1.0 
    #  and we lived with that in the brains2 AutoWorkup code thru v020.  
    #  Translation code has been eliminated now that images are centered by 
    #  an origin shift that is negative, not zero.
#    set dx [ expr   [lindex ${MidpointRealCenter} 0 ] * (1 - $sx ) ];
#    set dy [ expr   [lindex ${MidpointRealCenter} 1 ] * (1 - $sy ) ];
#    set dz [ expr   [lindex ${MidpointRealCenter} 2 ] * (1 - $sz ) ];
    
#puts "> > >HERE 1< < <"
    set scaleVector [itkVectorD3]
#puts "> > >HERE 2 scaleVector == ${scaleVector} sx == ${sx}"
    ${scaleVector} SetElement 0 ${sx}
#puts "> > >HERE 3< < <"
    ${scaleVector} SetElement 1 ${sy}
    ${scaleVector} SetElement 2 ${sz}

#    set translateVector [itkVectorD3]
#    $translateVector SetElement 0 $dx
#    $translateVector SetElement 1 $dy
#    $translateVector SetElement 2 $dz

    puts "Scale the atlas space by: $sx $sy $sz"
#    puts "Shift the atlas space by: $dx $dy $dz"

    set MovingMaskScalingToSubjectSizeTransform [itkAffineTransformD3_New]
    $MovingMaskScalingToSubjectSizeTransform SetIdentity
    ## Note: the pre=0 argument is defaulted in C++, but required for Tcl wrapped code.
    set ScalingPreFlag 0
    $MovingMaskScalingToSubjectSizeTransform Scale $scaleVector $ScalingPreFlag
#    set TranslationPreFlag 0
#    $MovingMaskScalingToSubjectSizeTransform Translate $translateVector $TranslationPreFlag

    ## For consistency with Read/Write routines, we need a GetPointer around the return value.
    return [${MovingMaskScalingToSubjectSizeTransform} GetPointer];
  }


  # Brains::AutoWorkup::ShiftToPredefinedRawSpaceACPCLocations --
  #
  #  This procedure will shift the center of  
  #     based on manually selected points from the raw data 
  #  space.
  #
  # Arguments:
  #  ACPC_RawSpace_TextFile
  #  InitialT1RawRotationTransform
  #  RawT1ImageRes
  #  RawT1ImageDims
  #  ACPCImageRes
  #  ACPCImageDims
  #  T1RawRotationTransform
  #
  # Results:
  #  The T1RawRotationTransform is a translated version of InitialT1RawRotationTransform.

  proc ShiftToPredefinedRawSpaceACPCLocations { ACPC_RawSpace_TextFile InitialT1RawRotationTransform \
                                                 T1RawBfc ScaledAtlasTemplateAvg \
                                                 T1RawRotationTransform } {
    package require BrainsGlue

    set atlasTemplateImage [Brains::itk::LoadImage ${ScaledAtlasTemplateAvg} "Signed-16bit"]
    set T1RawBfcImage [Brains::itk::LoadImage ${T1RawBfc} "Signed-16bit"]

    set RawT1ImageRes [Brains::Utils::GetImageSpacing ${T1RawBfcImage}] 
    set RawT1ImageDims [Brains::Utils::GetImageSize ${T1RawBfcImage}] 
    set RawT1ImageOrigin [Brains::Utils::GetImageOrigin ${T1RawBfcImage}] 
    set ACPCImageRes [Brains::Utils::GetImageSpacing ${atlasTemplateImage}] 
    set ACPCImageDims [Brains::Utils::GetImageSize ${atlasTemplateImage}]
    set ACPCImageOrigin [Brains::Utils::GetImageOrigin ${atlasTemplateImage}] 

    ${atlasTemplateImage} Delete
    ${T1RawBfcImage} Delete

    #set XTranslator [expr [lindex ${ACPCImageOrigin} 0] - [lindex ${RawT1ImageOrigin} 0] ];
    #set YTranslator [expr [lindex ${ACPCImageOrigin} 1] - [lindex ${RawT1ImageOrigin} 1] ];
    #set ZTranslator [expr [lindex ${ACPCImageOrigin} 2] - [lindex ${RawT1ImageOrigin} 2] ];
    puts " ACPCImageOrigin  ${ACPCImageOrigin} "
    puts " RawT1ImageOrigin  ${RawT1ImageOrigin} "
    #puts " ${XTranslator}  ${YTranslator}  ${ZTranslator}  -- CHANGE IN ORIGINS"
    #set ChangeOfOrigins [list ${XTranslator}  ${YTranslator}  ${ZTranslator} ]

    ##  The minus ones are hotly contested on grounds of inelegance, but making a stringent 
    #   FreeScale fit indicated that the centers of the 0..255 cube should all be 127, 127, 127,
    #   to nail the v3 average template Atlas AC point.
    set T1ACPCCenterIndex [ list \
                            [expr ([lindex ${ACPCImageDims} 0] - 1) * 0.5 ] \
                            [expr ([lindex ${ACPCImageDims} 1] - 1) * 0.5 ] \
                            [expr ([lindex ${ACPCImageDims} 2] - 1) * 0.5 ] \
                          ];

    set T1ACPCCenterLocationMM [ Brains::Utils::ConvertFromIndexToMMLocation ${T1ACPCCenterIndex} ${ACPCImageRes} ${ACPCImageOrigin} ] ;
    #set T1ACPCCenterLocationMM [ Brains::Utils::ConvertFromIndexToMMLocation ${T1ACPCCenterIndex} ${ACPCImageRes} ] ;
    puts " Atlas AC point as midpoint, T1ACPCCenterLocationMM: ${T1ACPCCenterLocationMM} "
    
    set AC_Pt_in_TemplateInitSpaceMM [ GetACPCPointInMMFromCustomLandmark ${ACPC_RawSpace_TextFile} AC ${RawT1ImageOrigin} ];
    #set AC_Pt_in_TemplateInitSpaceMM [ GetACPCPointInMMFromCustomLandmark ${ACPC_RawSpace_TextFile} AC ];
    puts " T1Raw AC point picked manually, AC_Pt_in_TemplateInitSpaceMM: ${AC_Pt_in_TemplateInitSpaceMM} "


    set OriginalToDeformedTxfm [Brains::itkUtils::readItkTransform ${InitialT1RawRotationTransform} ]
    set InverseOriginalToDeformedTxfm [itkAffineTransformD3_New]
    $OriginalToDeformedTxfm GetInverse [$InverseOriginalToDeformedTxfm GetPointer]



    set originalPoint [itkPointD3]
    $originalPoint SetElement 0 [expr [lindex $T1ACPCCenterLocationMM 0] ]
    $originalPoint SetElement 1 [expr [lindex $T1ACPCCenterLocationMM 1] ]
    $originalPoint SetElement 2 [expr [lindex $T1ACPCCenterLocationMM 2] ]
    
    set transformedPoint [$OriginalToDeformedTxfm TransformPoint $originalPoint]
    
    set RawT1ACPointInAtlasSpaceMM [list [$transformedPoint GetElement 0] \
                                          [$transformedPoint GetElement 1] \
                                          [$transformedPoint GetElement 2]]
    puts "\nT1ACPCCenterLocationMM Transformed = RawT1ACPointInAtlasSpaceMM: ${RawT1ACPointInAtlasSpaceMM} "



    set XTranslation [expr [lindex ${AC_Pt_in_TemplateInitSpaceMM} 0] - [lindex ${RawT1ACPointInAtlasSpaceMM} 0]];
    set YTranslation [expr [lindex ${AC_Pt_in_TemplateInitSpaceMM} 1] - [lindex ${RawT1ACPointInAtlasSpaceMM} 1]];
    set ZTranslation [expr [lindex ${AC_Pt_in_TemplateInitSpaceMM} 2] - [lindex ${RawT1ACPointInAtlasSpaceMM} 2]];
    puts " AC_Pt_in_TemplateInitSpaceMM ${AC_Pt_in_TemplateInitSpaceMM} "
    puts " - RawT1ACPointInAtlasSpaceMM ${RawT1ACPointInAtlasSpaceMM} "
#    puts " + ChangeOfOrigins ${ChangeOfOrigins} "
    puts " = ${XTranslation}  ${YTranslation}  ${ZTranslation}  -- PRE"

    set translationPRE [itkVectorD3]
    $translationPRE SetElement 0 $XTranslation
    $translationPRE SetElement 1 $YTranslation
    $translationPRE SetElement 2 $ZTranslation



    set originalPoint [itkPointD3]
    $originalPoint SetElement 0 [expr [lindex $AC_Pt_in_TemplateInitSpaceMM 0] ]
    $originalPoint SetElement 1 [expr [lindex $AC_Pt_in_TemplateInitSpaceMM 1] ]
    $originalPoint SetElement 2 [expr [lindex $AC_Pt_in_TemplateInitSpaceMM 2] ]
    
    set transformedPoint [$InverseOriginalToDeformedTxfm TransformPoint $originalPoint]
    
    set PreferredCenterInAtlasSpaceMM [list [$transformedPoint GetElement 0] \
                                             [$transformedPoint GetElement 1] \
                                             [$transformedPoint GetElement 2]]
    puts "\nAC_Pt_in_TemplateInitSpaceMM InverseTransformed = PreferredCenterInAtlasSpaceMM: ${PreferredCenterInAtlasSpaceMM} "



    set XTranslation [expr [lindex ${PreferredCenterInAtlasSpaceMM} 0] - [lindex ${T1ACPCCenterLocationMM} 0]];
    set YTranslation [expr [lindex ${PreferredCenterInAtlasSpaceMM} 1] - [lindex ${T1ACPCCenterLocationMM} 1]];
    set ZTranslation [expr [lindex ${PreferredCenterInAtlasSpaceMM} 2] - [lindex ${T1ACPCCenterLocationMM} 2]];
    puts " PreferredCenterInAtlasSpaceMM ${PreferredCenterInAtlasSpaceMM} "
    puts " - T1ACPCCenterLocationMM ${T1ACPCCenterLocationMM} "
#    puts " + ChangeOfOrigins ${ChangeOfOrigins} "
    puts " = ${XTranslation}  ${YTranslation}  ${ZTranslation}  -- POST"

    set translationPOST [itkVectorD3]
    $translationPOST SetElement 0 $XTranslation
    $translationPOST SetElement 1 $YTranslation
    $translationPOST SetElement 2 $ZTranslation


    $InverseOriginalToDeformedTxfm Delete
    $OriginalToDeformedTxfm Delete



    set T1RawToACPCNotCenteredTransform [Brains::itkUtils::readItkTransform ${InitialT1RawRotationTransform} ];
    ###VAM - Pre or Post Multiply????
    if 1 {
        set PreMultiplyFlag 0
        $T1RawToACPCNotCenteredTransform Translate $translationPOST $PreMultiplyFlag
    } else {
        set PreMultiplyFlag 1
        $T1RawToACPCNotCenteredTransform Translate $translationPRE $PreMultiplyFlag
    }
    
    Brains::Utils::ExitOnFailure [ Brains::itkUtils::WriteItkTransform $T1RawToACPCNotCenteredTransform ${T1RawRotationTransform} ] "writing re-shifted transform to file ${T1RawRotationTransform}"
    $T1RawToACPCNotCenteredTransform Delete
  }


  # Brains::AutoWorkup::GetACPCPointInMMFromCustomLandmark --
  #
  #  This will read in the position of the AC and PC points defined
  #  in a raw text file.
  #
  # Arguments:
  #  ReadFrom_file       Input file to copy
  #  WriteOut_file       Output destination file
  #
  # Results:
  #  The input file is successfully copied
  
  proc GetACPCPointInMMFromCustomLandmark { ReadFrom_OriginalSpaceACPCPoints ACorPC {Origin {0.0 0.0 0.0}} } {

    if { [ file exists ${ReadFrom_OriginalSpaceACPCPoints} ]  } {
      set filestatus 0;
    } else {
      set filestatus -1;
    }
    Brains::Utils::ExitOnFailure ${filestatus} "Test whether the required ACPC in raw space txt file exists."

    ##Multiply to get back to pixels
    set ACPC_Original_file [open ${ReadFrom_OriginalSpaceACPCPoints}]
    gets ${ACPC_Original_file} AC_Pt_in_T1OriginalSpace
    gets ${ACPC_Original_file} PC_Pt_in_T1OriginalSpace
    close ${ACPC_Original_file}
    
    if {[string equal $ACorPC AC] == 1} {
      set result [list [expr [lindex ${AC_Pt_in_T1OriginalSpace} 0] + [lindex $Origin 0]] [expr [lindex ${AC_Pt_in_T1OriginalSpace} 1] + [lindex $Origin 1]] [expr [lindex ${AC_Pt_in_T1OriginalSpace} 2] + [lindex $Origin 2]]]
      puts " AC point in T1OriginalSpace ${AC_Pt_in_T1OriginalSpace} "
      puts " subtracted origin ${result} "
      return ${result}
    } else {
      set result [list [expr [lindex ${PC_Pt_in_T1OriginalSpace} 0] + [lindex $Origin 0]] [expr [lindex ${PC_Pt_in_T1OriginalSpace} 1] + [lindex $Origin 1]] [expr [lindex ${PC_Pt_in_T1OriginalSpace} 2] + [lindex $Origin 2]]]
      puts " PC point in T1OriginalSpace ${PC_Pt_in_T1OriginalSpace} "
      puts " subtracted origin ${result} "
      return ${result}
    }
    
  }



  # Brains::AutoWorkup::GetDeformedACPointInMMFromCustomLandmark --
  #
  #  This will read in the position of the AC and PC points defined
  #  in a raw text file.
  #
  # Arguments:
  #  ReadFrom_file       Input file to copy
  #  WriteOut_file       Output destination file
  #
  # Results:
  #  The input file is successfully copied
  
  proc GetDeformedACPointInMMFromCustomLandmark { ReadFrom_OriginalSpaceACPCPoints ReadFrom_OriginalToDeformedTxfm T1RawSpacing } {

    if { [ file exists ${ReadFrom_OriginalSpaceACPCPoints} ]  } {
      set filestatus 0;
    } else {
      set filestatus -1;
    }
    Brains::Utils::ExitOnFailure ${filestatus} "Required ACPC in raw space txt file missing."

    ##Multiply to get back to pixels
    set ACPC_Original_file [open ${ReadFrom_OriginalSpaceACPCPoints}]
    gets ${ACPC_Original_file} AC_Pt_in_T1OriginalSpace
    gets ${ACPC_Original_file} PC_Pt_in_T1OriginalSpace
    close ${ACPC_Original_file}
    puts " AC point in T1OriginalSpace ${AC_Pt_in_T1OriginalSpace} "
    
    ## Note:  Landmarks in this custom file are given in MM.
    set OriginalToDeformedTxfm [Brains::itkUtils::readItkTransform ${ReadFrom_OriginalToDeformedTxfm} ]

    set InverseOriginalToDeformedTxfm [itkAffineTransformD3_New]
    $OriginalToDeformedTxfm GetInverse [$InverseOriginalToDeformedTxfm GetPointer]

    set originalPoint [itkPointD3]
    $originalPoint SetElement 0 [expr [lindex $AC_Pt_in_T1OriginalSpace 0] / [lindex $T1RawSpacing 0]]
    $originalPoint SetElement 1 [expr [lindex $AC_Pt_in_T1OriginalSpace 1] / [lindex $T1RawSpacing 1]]
    $originalPoint SetElement 2 [expr [lindex $AC_Pt_in_T1OriginalSpace 2] / [lindex $T1RawSpacing 2]]
    
    set transformedPoint [$OriginalToDeformedTxfm TransformPoint $originalPoint]
    $OriginalToDeformedTxfm Delete
    
    set NewPoint [list  [$transformedPoint GetElement 0] \
                         [$transformedPoint GetElement 1] \
                         [$transformedPoint GetElement 2]]
    puts " AC point in Transformed ${NewPoint} "
    
    set transformedPoint [$InverseOriginalToDeformedTxfm TransformPoint $originalPoint]
    $InverseOriginalToDeformedTxfm Delete
    
    set NewPoint [list  [$transformedPoint GetElement 0] \
                         [$transformedPoint GetElement 1] \
                         [$transformedPoint GetElement 2]]
    puts " AC point in InverseTransformed ${NewPoint} "

    return $NewPoint
  }

  # Brains::AutoWorkup::GetDeformedACPCPointsInMMFromTalairach --
  #
  #  This will read in the talairach points from the specified
  #  fiel and transform then into raw space
  #
  # Arguments:
  #  talairachFile       Input file to copy
  #  transformFile       Output destination file
  #  res                 Resolution of the image
  #  origin              Origin of the image
  #
  # Results:
  #  Transformed AC point into raw space

  proc GetDeformedACPCPointsInMMFromTalairach { talairachFile transformFile \
                                  {res {1.0 1.0 1.0}} {origin {0.0 0.0 0.0}} } {
    set TalParametersInACPCSpace [Brains::Utils::LoadSafe Talairach-parameters $talairachFile ]
    set TalPointsInACPCSpace [b2 get talairach points ${TalParametersInACPCSpace}]
    set TalParRes [ b2 get res talairach-parameters ${TalParametersInACPCSpace} ]
    b2 destroy talairach-parameters ${TalParametersInACPCSpace}

    ## Note:  Landmarks in talairach file are given in voxel locations, so a conversion to MM is necessary.

    set AC_Pt_in_T1OriginalSpace [Brains::Utils::ConvertFromIndexToMMLocation \
              [list [Brains::Utils::ltraceSafe 0 ${TalPointsInACPCSpace} 0 0] \
                    [Brains::Utils::ltraceSafe 0 ${TalPointsInACPCSpace} 0 1] \
                    [Brains::Utils::ltraceSafe 0 ${TalPointsInACPCSpace} 0 2]] $res $origin]

    set PC_Pt_in_T1OriginalSpace [Brains::Utils::ConvertFromIndexToMMLocation \
              [list [Brains::Utils::ltraceSafe 0 ${TalPointsInACPCSpace} 1 0] \
                    [Brains::Utils::ltraceSafe 0 ${TalPointsInACPCSpace} 1 1] \
                    [Brains::Utils::ltraceSafe 0 ${TalPointsInACPCSpace} 1 2]] $res $origin]

    set OriginalToDeformedTxfm [Brains::itkUtils::readTransform ${ReadFrom_OriginalToDeformedTxfm} ]
    set NewPoint [ GetDeformedACPCPointsInMM ${AC_Pt_in_T1OriginalSpace} \
                   ${PC_Pt_in_T1OriginalSpace} ${OriginalToDeformedTxfm} ${WhichPoint} ];
    ${OriginalToDeformedTxfm} Delete
    return ${NewPoint};
  }

  # Brains::AutoWorkup::GetDeformedACPCPointsInMM --
  #
  #  Returns a deformed AC, PC, or COPC point.
  #  The COPC point has the same x and y coordinates as the AC, 
  #  but the PC z direction is specified as the distance 
  #  between AC and PC point.
  #
  # NOTE: Input and Output points are both specified in MM 
  #       from origin.
  #
  # Arguments:
  #  AC_Pt_in_T1OriginalSpace       Original Space AC Point
  #  PC_Pt_in_T1OriginalSpace       Original Space PC Point
  #  OriginalToDeformedTxfm         Transform to apply to points
  #  WhichPoint                     Point to deform
  #
  # Results:
  #  Transformed requested point

  proc GetDeformedACPCPointsInMM { AC_Pt_in_T1OriginalSpace PC_Pt_in_T1OriginalSpace OriginalToDeformedTxfm WhichPoint } {
    set T1OriginalRes [b2 get reslice-res transform ${OriginalToDeformedTxfm}];
    set T1OriginalDims [b2 get reslice-dims transform ${OriginalToDeformedTxfm}];

    set T1ACPCRes [b2 get standard-res transform ${OriginalToDeformedTxfm}];
    set T1ACPCDims  [b2 get standard-dims transform ${OriginalToDeformedTxfm}];

    puts "Saved raw AC Pt: ${AC_Pt_in_T1OriginalSpace}"
    set originalPoint [itkPointD3]
    $originalPoint SetElement 0 [lindex ${AC_Pt_in_T1OriginalSpace} 0]
    $originalPoint SetElement 1 [lindex ${AC_Pt_in_T1OriginalSpace} 1]
    $originalPoint SetElement 2 [lindex ${AC_Pt_in_T1OriginalSpace} 2]
    set AC_Pt_in_DeformedSpaceTemp  [$OriginalToDeformedTxfm TransformPoint $originalPoint]
    puts "Transformed AC Pt: ${AC_Pt_in_DeformedSpace}"

    puts "Saved raw PC Pt: ${PC_Pt_in_T1OriginalSpace}"
    $originalPoint SetElement 0 [lindex ${PC_Pt_in_T1OriginalSpace} 0]
    $originalPoint SetElement 1 [lindex ${PC_Pt_in_T1OriginalSpace} 1]
    $originalPoint SetElement 2 [lindex ${PC_Pt_in_T1OriginalSpace} 2]
    set PC_Pt_in_DeformedSpaceTemp  [$OriginalToDeformedTxfm TransformPoint $originalPoint]
    puts "Transformed PC Pt: ${PC_Pt_in_DeformedSpace}"

    switch  "${WhichPoint}" {
      "AC" { return ${AC_Pt_in_DeformedSpace}; }
      "PC" { return ${PC_Pt_in_DeformedSpace}; }
      "COPC" {
         ## Returns the PC point that is colinear to the AC point but at the same distance from the AC as in the original space
        set xDist [ expr pow( [lindex ${AC_Pt_in_DeformedSpace} 0]-[lindex ${PC_Pt_in_DeformedSpace} 0] ,2) ]
        set yDist [ expr pow( [lindex ${AC_Pt_in_DeformedSpace} 0]-[lindex ${PC_Pt_in_DeformedSpace} 0] ,2) ]
        set zDist [ expr pow( [lindex ${AC_Pt_in_DeformedSpace} 0]-[lindex ${PC_Pt_in_DeformedSpace} 0] ,2) ]

        set ACPCdist [ expr sqrt ( xDist + yDist + zDist ) ]
        
        set PCx [lindex ${AC_Pt_in_DeformedSpace} 0];
        set PCy [lindex ${AC_Pt_in_DeformedSpace} 1];
        set PCz [expr [lindex ${AC_Pt_in_DeformedSpace} 2] - ${ACPCdist} ];
        return [ list ${PCx} ${PCy} ${PCz} ];
        }
    }
    puts "ERROR: Invalid Point"; 
    return [ list -1 -1 -1 ${InvalidPoint} ] ;
  }



  # Brains::itk::GenerateAutoAlignmentToIntakeT1 --
  #
  #  This function reads in a raw image an average template, and 
  #  distance images associated with the template and produces an 
  #  ACPC aligned output image and it's taliarach, and the distance 
  #  image masks for whole brain, whole cerebrum, and whole cerebellum.
  #
  # Arguments:
  #  ReadFrom_rawimg                      - FileName of the intensity-remapped acquisition in its original, anisotropic voxel format.
  # \param ReadFrom_templateimg           - FileName of the template image to read in
  # \param ReadFrom_atlascortexmask       - FileName of associated mask - whole cerebrum
  # \param ReadFrom_atlasbrainmask        - FileName of associated mask - whole brain
  # \param ReadFrom_templateTalairach     - FileName of associated TalairachParameters file
  # \param UseName_id                     - substring to include in computed filenames to indicate the Subject Encounter
  # \param WorkIn_autotempdir             - DirectoryName in which we may create temporary, intermediate files without stepping on other work
  # \param WorkIn_autorawdir              - DirectoryName for raw data
  # \param WriteOut_ACPC_Talairach        - FileName of Talairach.bnd parameters based on the scaling fit
  # \param WriteOut_brainscalemask        !!!- FileName of an atlas-derived whole brain mask
  # \param WriteOut_cortexscalemask       - FileName of an atlas-derived whole cerebrum mask
  # \param WriteOut_T1RawToACPCFinalTransform - FileName of the rigid rotation transform mapping the raw data to the ACPC atlas orientation.
  # \param WriteOut_T1RawToACPCFinalRotated   - FileName of the rigidly rotated remapped raw T1 data conforming to the atlas template.
  #
  # Results:
  #  List of transform and resulting ACPC aligned image
    

  proc GenerateAutoAlignmentToIntakeT1 {ReadFrom_rawimg \
                                      ReadFrom_templateimg \
                                      ReadFrom_FadedAtlas \
                                      UseName_id WorkIn_autotempdir WorkIn_autodir WorkIn_autorawdir \
                                      ReadFrom_TmplAtlasPath Use_TemplateKind Use_TemplateVersionString \
                                      WriteOut_T1RawToACPCFinalTransform \
                                      WriteOut_T1RawToACPCFinalRotated } {
    if {[Brains::Utils::CheckOutputsNewer \
        [list ${WriteOut_T1RawToACPCFinalTransform} ${WriteOut_T1RawToACPCFinalRotated} ] \
        [list ${ReadFrom_rawimg} ${ReadFrom_templateimg} ${ReadFrom_FadedAtlas}  ]] == false} {
                
        puts -nonewline "======= EXECUTING: GenerateAutoAlignmentToAverage: "
        puts -nonewline " ${ReadFrom_rawimg}" 
        puts -nonewline " ${ReadFrom_templateimg}"
        puts -nonewline " ${ReadFrom_FadedAtlas}" 
        puts -nonewline " ${UseName_id}" 
        puts -nonewline " ${WorkIn_autotempdir}" 
        puts -nonewline " ${WorkIn_autodir}" 
        puts -nonewline " ${WriteOut_T1RawToACPCFinalTransform}" 
        puts " ${WriteOut_T1RawToACPCFinalRotated}"


        # AutoAlign_FreeScaleTmplFitT1

        set WriteTemp_T1RawToTmplBootRotation "${WorkIn_autotempdir}/${UseName_id}_T1RawToTmplBootRotation__int.xfrm"
        set WriteTemp_T1RawToTmplFreeScale "${WorkIn_autotempdir}/${UseName_id}_T1RawToTmplFreeScale__int.xfrm"
        set WriteTemp_T1RawToTmplRigidRotation "${WorkIn_autotempdir}/${UseName_id}_T1RawToTmplRigidRotation__int.xfrm"

        set WriteTemp_NoNeckMovingImage [SpliceFullLocationNameSuffix ${WorkIn_autorawdir} ${ReadFrom_rawimg} NoNk];
        set WriteTemp_SkullStripmovingimg [CreateNeckRemovedImage ${ReadFrom_rawimg} ${WriteTemp_NoNeckMovingImage} ];
        set WriteTemp_FinalTransform [T1RawImageOptimizedNineParameterImageToTmplMIRegistration \
              ${WriteTemp_SkullStripmovingimg} ${ReadFrom_rawimg} ${ReadFrom_FadedAtlas} \
              ${WriteTemp_T1RawToTmplBootRotation} ${WriteTemp_T1RawToTmplFreeScale} \
              ${WriteTemp_T1RawToTmplRigidRotation} ${ReadFrom_TmplAtlasPath} ${Use_TemplateKind} \
              ${Use_TemplateVersionString}]
# These next two lines are probably not needed.
#        set GoldTransform [b2_load_safe Transform ${WriteTemp_FinalTransform}]
#        Brains::Utils::ExitOnFailure [ b2 save transform ${WriteOut_T1RawToACPCFinalTransform} brains2 ${GoldTransform} ] "saving T1FinalTransform"
#
#        DestroyAllObjects

        ## Create the final ACPC T1 
        set T1RawToACPCImage [Brains::Utils::LoadSafe image ${ReadFrom_rawimg}]
        set T1RawToACPCFinalTransform [Brains::itkUtils::readItkTransform ${WriteOut_T1RawToACPCFinalTransform}]
        ###VAM Need to define dims and res here.
        set transformedImage [Brains::itk::ResampleImage $T1RawToACPCImage $T1RawToACPCFinalTransform \
                              "Unsigned-8bit" "Linear" $resolutions $dimensions]


        set T1FinalImage [ YDimFloorClipImage ${transformedImage} ];
        Brains::Utils::ExitOnFailure [ b2 destroy image ${T1RawToACPCImage} ] "destroying T1RawToACPCImage"
        Brains::Utils::ExitOnFailure [ b2 destroy image ${transformedImage} ] "destroying transformedImage"

        Brains::Utils::ExitOnFailure [ b2 save image ${WriteOut_T1RawToACPCFinalRotated} nifti ${T1FinalImage} data-type= unsigned-8bit] \
                   "saving T1FinalImage ${WriteOut_T1RawToACPCFinalRotated}"
        Brains::Utils::ExitOnFailure [ b2 destroy image ${T1FinalImage} ] "destroying T1FinalImage"

    }

    return [list  ${WriteOut_T1RawToACPCFinalTransform} ${WriteOut_T1RawToACPCFinalRotated} ]
  }



  # Brains::itk::GenerateSubjectAutoAlignmentToAverageACPCCenteredSpace --
  #
  #   This function reads in an unmapped, raw initial acquisition 
  #   image and, at the moment, computes a standardization of the 
  #   mean transform based on whole head mean.
  #
  # Arguments:
  #  ReadFrom_intakeT1rotated_brainmask   - FileName of the rotated T1 image that was separately fit to.
  #  ReadFrom_intakeT1rotated_talairach   - FileName of the corresponding talairach.bnds.
  #  WriteOut_T1rotated_brainmask         - FileName of T1 rotated brain mask to copy to.
  #  WriteOut_T1rotated_talairach         - FileName of the talairach bounds file to copy to.
  #
  # Results:
  ###VAM -  What is the RESULT

  proc CopyOverIntakeT1ToT1Aligned {ReadFrom_intakeT1rotated_brainmask ReadFrom_intakeT1rotated_talairach \
                  ReadFrom_cortexscalemask WriteOut_T1rotated_brainmask WriteOut_cortexscalemask \
                  WriteOut_T1Trial_talairach ReadFrom_AtlasToSubjectScaleBrainProb255 \
                  ReadFrom_intakeAvg108_ScaledToSizeOfSubject ReadFrom_intakeAvg108_TmplToSubjectXfrm \
                  WriteOut_AtlasToSubjectScaleBrainProb255 WriteTemp_Avg108_ScaledToSizeOfSubject WriteOut_TmplToSubjectXfrm} {

    if {[file exists ${ReadFrom_intakeAvg108_TmplToSubjectXfrm}] == 0 } {
        set ReadFrom_intakeAvg108_TmplToSubjectXfrm [lindex [glob -nocomplain \
              [file dirname ${ReadFrom_intakeAvg108_TmplToSubjectXfrm}]/delete/*[file tail \
                            ${ReadFrom_intakeAvg108_TmplToSubjectXfrm}]] 0]
    }
    # Copy the Atlas to image Transform
    CopyOverPairing ${ReadFrom_intakeAvg108_TmplToSubjectXfrm} ${WriteOut_TmplToSubjectXfrm}
    
    if {[file exists ${ReadFrom_intakeAvg108_ScaledToSizeOfSubject}] == 0 } {
        set ReadFrom_intakeAvg108_ScaledToSizeOfSubject [lindex [glob -nocomplain \
             [file dirname ${ReadFrom_intakeAvg108_ScaledToSizeOfSubject}]/delete/*[file tail \
                           ${ReadFrom_intakeAvg108_ScaledToSizeOfSubject}]] 0]
    }
    
    # Copy over the scaled Atlas image
    CopyOverPairing ${ReadFrom_intakeAvg108_ScaledToSizeOfSubject} ${WriteTemp_Avg108_ScaledToSizeOfSubject}
    
    if {[file exists ${ReadFrom_AtlasToSubjectScaleBrainProb255}] == 0 } {
        set ReadFrom_AtlasToSubjectScaleBrainProb255 [lindex [glob -nocomplain \
             [file dirname ${ReadFrom_AtlasToSubjectScaleBrainProb255}]/delete/*[file tail ${ReadFrom_AtlasToSubjectScaleBrainProb255}]] 0]
    }

    # Copy the brain probabiltity image
    CopyOverPairing ${ReadFrom_AtlasToSubjectScaleBrainProb255} ${WriteOut_AtlasToSubjectScaleBrainProb255}
    
    set outputList [list ${WriteOut_T1rotated_brainmask} ${WriteOut_cortexscalemask} ${WriteOut_T1Trial_talairach} ]
    set inputList [list ${ReadFrom_intakeT1rotated_brainmask} ${ReadFrom_intakeT1rotated_talairach} ${ReadFrom_cortexscalemask} ]
    if {[CheckOutputsNewer $outputList $inputList]] == false} {
        file delete -force ${WriteOut_T1rotated_brainmask}
        file copy -force ${ReadFrom_intakeT1rotated_brainmask} ${WriteOut_T1rotated_brainmask}
        Brains::Utils::touch ${WriteOut_T1rotated_brainmask} [list -r ${ReadFrom_intakeT1rotated_brainmask}]
        file delete -force ${WriteOut_T1Trial_talairach}
        file copy -force ${ReadFrom_intakeT1rotated_talairach} ${WriteOut_T1Trial_talairach}
        Brains::Utils::touch ${WriteOut_T1Trial_talairach} [list -r ${ReadFrom_intakeT1rotated_talairach}]
        file delete -force ${WriteOut_cortexscalemask}
        file copy -force ${ReadFrom_cortexscalemask} ${WriteOut_cortexscalemask}
        Brains::Utils::touch ${WriteOut_cortexscalemask} [list -r ${ReadFrom_cortexscalemask}]
    }
    return [list ${WriteOut_T1rotated_brainmask} ${WriteOut_cortexscalemask} ${WriteOut_T1Trial_talairach}]
  }


  # Brains::AutoWorkup::CopyOverPairing --
  #
  #  Copy the inout file to the output file
  #
  # Arguments:
  #  ReadFrom_file       Input file to copy
  #  WriteOut_file       Output destination file
  #
  # Results:
  #  The input file is successfully copied

  proc CopyOverPairing {ReadFrom_file WriteOut_file} {
    
    set outputList [list ${WriteOut_file}]
    set inputList [list ${ReadFrom_file}]

    if [file exists ${ReadFrom_file}] {
      if {[file exists ${WriteOut_file}] == 0} {
        ## file delete -force ${WriteOut_file}
        file copy -force ${ReadFrom_file} ${WriteOut_file} ;
        puts "\n|====| Copied ${ReadFrom_file} to ${WriteOut_file} \n\n"
      } elseif { [CheckOutputsNewer $outputList $inputList] == false } {
        ## file delete -force ${WriteOut_file}
        file copy -force ${ReadFrom_file} ${WriteOut_file} ;
        puts "\n|====| Copied ${ReadFrom_file} to ${WriteOut_file} \n\n"
      }
      if {[CheckOutputsNewer $outputList $inputList] == true} {
        Brains::Utils::touch ${WriteOut_file} [list -r ${ReadFrom_file}]
      }
    } else {
      Brains::Utils::ExitOnFailure -1 "Necessary image ${ReadFrom_file} does not exist.";
    }
  }


}

