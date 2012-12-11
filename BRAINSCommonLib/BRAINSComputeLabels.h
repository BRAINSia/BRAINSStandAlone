#ifndef BRAINSComputeLabels_h
#define BRAINSComputeLabels_h

#include <iostream>
#include <vector>
#include <itkImage.h>
#include "ExtractSingleLargestRegion.h"
// #include <itkTimeProbe.h>
// #include <itkRealTimeClock.h>
#include <vnl/vnl_vector.h>

// Labeling using maximum a posteriori, also do brain stripping using
// mathematical morphology and connected component
template <class TProbabilityImage, class TByteImage,
          typename TFloatingPrecision>
void ComputeLabels(
  std::vector<typename TProbabilityImage::Pointer> & Posteriors,
  std::vector<bool> & PriorIsForegroundPriorVector,
  vnl_vector<unsigned int> & PriorLabelCodeVector,
  typename TByteImage::Pointer & NonAirRegion,
  typename TByteImage::Pointer & DirtyLabels,
  typename TByteImage::Pointer & CleanedLabels,
  TFloatingPrecision InclusionThreshold = 0.0F)
{
//  muLogMacro(<< "ComputeLabels" << std::endl );
//  itk::TimeProbe ComputeLabelsTimer;
//  ComputeLabelsTimer.Start();

  const unsigned int numClasses = Posteriors.size();
  const typename TProbabilityImage::RegionType region = Posteriors[0]->GetLargestPossibleRegion();

  DirtyLabels = TByteImage::New();
  DirtyLabels->CopyInformation(Posteriors[0]);
  DirtyLabels->SetRegions(region);
  DirtyLabels->Allocate();
  DirtyLabels->FillBuffer(0);

  typename TByteImage::Pointer foregroundMask = TByteImage::New();
  foregroundMask->CopyInformation(Posteriors[0]);
  foregroundMask->SetRegions(region);
  foregroundMask->Allocate();
  foregroundMask->FillBuffer(0);
#if defined(LOCAL_USE_OPEN_MP) && (_OPENMP < 200805)
  typedef int LOOPITERTYPE;
#else
  typedef unsigned int LOOPITERTYPE;
#endif

  const typename TByteImage::SizeType size = DirtyLabels->GetLargestPossibleRegion().GetSize();
    {
#if defined(LOCAL_USE_OPEN_MP)
#pragma omp parallel for
#endif
    for( LOOPITERTYPE kk = 0; kk < (LOOPITERTYPE)size[2]; kk++ )
      {
      for( LOOPITERTYPE jj = 0; jj < (LOOPITERTYPE)size[1]; jj++ )
        {
        for( LOOPITERTYPE ii = 0; ii < (LOOPITERTYPE)size[0]; ii++ )
          {
          const typename TProbabilityImage::IndexType currIndex = {{ii, jj, kk}};
          if( NonAirRegion->GetPixel(currIndex) == 0 ) // If outside the tissue
                                                       // region, then set to
                                                       // zero vIndex!
            {
            // TODO:  May want to specify this explicitly in the XML file for
            // the proper background value
            DirtyLabels->SetPixel(currIndex, 0); // This is implied by the
                                                 // FillBuffer(0) above;
            continue;
            }

          TFloatingPrecision maxPosteriorClassValue = Posteriors[0]->GetPixel(currIndex);
          unsigned int      indexMaxPosteriorClassValue = 0;
          for( unsigned int iclass = 1; iclass < numClasses; iclass++ )
            {
            const TFloatingPrecision currentPosteriorClassValue = Posteriors[iclass]->GetPixel(currIndex);
            if( currentPosteriorClassValue > maxPosteriorClassValue )
              {
              maxPosteriorClassValue = currentPosteriorClassValue;
              indexMaxPosteriorClassValue = iclass;
              }
            }

            {
            bool         fgflag = PriorIsForegroundPriorVector[indexMaxPosteriorClassValue];
            unsigned int label = 99;
            if(maxPosteriorClassValue > InclusionThreshold)
              {
              label = PriorLabelCodeVector[indexMaxPosteriorClassValue];
              }

            // Only use non-zero probabilities and foreground classes
            if( !fgflag || ( maxPosteriorClassValue < 0.001 ) )
              {
              fgflag = false; // If priors are zero or negative, then set the
                              // fgflag back to false
              }
            DirtyLabels->SetPixel(currIndex, label);
            foregroundMask->SetPixel(currIndex, fgflag);
            }
          }
        }
      }
    }
  //
  // CleanedLabels=ExtractSingleLargestRegionFromMask(foregroundMask,2,2,1,DirtyLabels);
  CleanedLabels = ExtractSingleLargestRegionFromMask(foregroundMask, 0, 0, 0, DirtyLabels);
//  ComputeLabelsTimer.Stop();
//  itk::RealTimeClock::TimeStampType elapsedTime =
//    ComputeLabelsTimer.GetTotal();
//  muLogMacro(<< "Computing Labels took " << elapsedTime << " " << ComputeLabelsTimer.GetUnit() << std::endl);
}
#endif // BRAINSComputeLabels_h
