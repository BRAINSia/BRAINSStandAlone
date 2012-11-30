#include "DWIConvertUtils.h"

typedef short PixelValueType;
typedef itk::Image< PixelValueType, 4 > VolumeType;
typedef itk::VectorImage<PixelValueType, 3> VectorVolumeType;


VolumeType::Pointer CreateVolume(VectorVolumeType::Pointer &inputVol)
{
  VectorVolumeType::SizeType inputSize =
    inputVol->GetLargestPossibleRegion().GetSize();
  VectorVolumeType::SpacingType inputSpacing = inputVol->GetSpacing();
  VectorVolumeType::PointType inputOrigin = inputVol->GetOrigin();
  VectorVolumeType::DirectionType inputDirection = inputVol->GetDirection();

  VolumeType::Pointer niftiVolume =
    VolumeType::New();
  VolumeType::SizeType volSize;
  VolumeType::SpacingType volSpacing;
  VolumeType::PointType volOrigin;
  VolumeType::DirectionType volDirection;

  for(unsigned int i = 0; i < 3; ++i)
    {
    volSize[i] = inputSize[i];
    volSpacing[i] = inputSpacing[i];
    volOrigin[i] = inputOrigin[i];
    for(unsigned int j = 0; j < 3; ++j)
      {
      volDirection[i][j] = inputDirection[i][j];
      }
    volDirection[3][i] = 0.0;
    volDirection[i][3] = 0.0;
    }
  volDirection[3][3] = 1.0;
  volSpacing[3] = 1.0;
  volOrigin[3] = 0.0;
  volSize[3] = inputVol->GetNumberOfComponentsPerPixel();

  niftiVolume->SetRegions(volSize);
  niftiVolume->SetOrigin(volOrigin);
  niftiVolume->SetSpacing(volSpacing);
  niftiVolume->SetDirection(volDirection);
  niftiVolume->Allocate();
  return niftiVolume;
}

int NrrdToFSL(const std::string &inputVolume,
              const std::string &outputVolume,
              const std::string &outputBValues,
              const std::string &outputBVectors)
{
  if(CheckArg<std::string>("Input Volume",inputVolume,"") == EXIT_FAILURE ||
     CheckArg<std::string>("Output Volume",outputVolume,"") == EXIT_FAILURE ||
     CheckArg<std::string>("B Values", outputBValues, "") == EXIT_FAILURE ||
     CheckArg<std::string>("B Vectors", outputBVectors, ""))
    {
    return EXIT_FAILURE;
    }
  VectorVolumeType::Pointer inputVol;
  if(ReadVolume<VectorVolumeType>( inputVol, inputVolume ) != EXIT_SUCCESS)
    {
    return EXIT_FAILURE;
    }
  VolumeType::Pointer niftiVolume = CreateVolume(inputVol);
  const VectorVolumeType::SizeType inputSize ( inputVol->GetLargestPossibleRegion().GetSize() );
  const VolumeType::IndexType::IndexValueType vecLength = inputVol->GetNumberOfComponentsPerPixel();

  VectorVolumeType::IndexType vecIndex;
  VolumeType::IndexType volIndex;
  // convert from vector image to 4D volume image
  for(volIndex[3] = 0; volIndex[3] < vecLength; ++volIndex[3])
    {
    for(volIndex[2] = 0; volIndex[2] < static_cast<VolumeType::IndexType::IndexValueType>( inputSize[2] ); ++volIndex[2])
      {
      vecIndex[2] = volIndex[2];
      for(volIndex[1] = 0; volIndex[1] < static_cast<VolumeType::IndexType::IndexValueType>( inputSize[1] ); ++volIndex[1])
        {
        vecIndex[1] = volIndex[1];
        for(volIndex[0] = 0; volIndex[0] < static_cast<VolumeType::IndexType::IndexValueType>( inputSize[0] ); ++volIndex[0])
          {
          vecIndex[0] = volIndex[0];
          niftiVolume->SetPixel(volIndex, inputVol->GetPixel(vecIndex)[volIndex[3]]);
          }
        }
      }
    }
  if(WriteVolume<VolumeType>(niftiVolume,outputVolume) != EXIT_SUCCESS)
    {
    return EXIT_FAILURE;
    }
  std::vector< std::vector<double> > bVectors;
  if(RecoverBVectors<VectorVolumeType>(inputVol,bVectors) != EXIT_SUCCESS)
    {
    std::cerr << "No gradient vectors found in "
              << inputVolume << std::endl;
    return EXIT_FAILURE;
    }

  if(WriteBVectors(bVectors, outputBVectors) != EXIT_SUCCESS)
    {
    std::cerr << "Failed to write " << outputBVectors << std::endl;
    return EXIT_FAILURE;
    }

  std::vector<double> bValues;
  RecoverBValues<VectorVolumeType>(inputVol,bVectors,bValues);

  if(WriteBValues(bValues, outputBValues) != EXIT_SUCCESS)
    {
    std::cerr << "Failed to write " << outputBValues << std::endl;
    return EXIT_FAILURE;
    }

  return EXIT_SUCCESS;
}
