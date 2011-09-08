#include "itkIO.h"
#include "itkImageRegionIterator.h"
#include <iostream>
int
main(int argc, char **argv)
{
  if(argc < 3)
    {
    std::cerr << "Usage: ImageCompare imagea imageb" << std::endl;
    exit(1);
    }

  std::string input1Name(argv[1]), input2Name(argv[2]);

  typedef itk::Image<short,3> ImageType;

  ImageType::Pointer image1, image2;

  try
    {
    image1 = itkUtil::ReadImage<ImageType>(input1Name);
    }
  catch(...)
    {
    std::cerr << "Error reading " << input1Name << std::endl;
    exit(1);
    }
  try
    {
    image2 = itkUtil::ReadImage<ImageType>(input2Name);
    }
  catch(...)
    {
    std::cerr << "Error reading " << input2Name << std::endl;
    exit(1);
    }
  if(image1.IsNull())
    {
    std::cerr << "Error reading " << input1Name << std::endl;
    exit(1);
    }
  if(image2.IsNull())
    {
    std::cerr << "Error reading " << input2Name << std::endl;
    exit(1);
    }

  typedef itk::ImageRegionIterator<ImageType> ImageIteratorType;
  ImageIteratorType it1(image1,image1->GetLargestPossibleRegion());
  ImageIteratorType it2(image2,image2->GetLargestPossibleRegion());


  while(!it1.IsAtEnd() && !it2.IsAtEnd())
    {
    short diff = it1.Value() - it2.Value();
    if(diff < 0)
      {
      diff = -diff;
      }
    if(diff > 1)
      {
      std::cerr << "Mismatch between " << input1Name
                << " and " << input2Name << std::endl;
      break;
      }
    ++it1; ++it2;
    }
  if(!it1.IsAtEnd() && !it2.IsAtEnd())
    {
    exit(1);
    }
  exit(0);
}
