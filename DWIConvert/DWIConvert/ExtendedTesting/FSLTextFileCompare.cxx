#include "DWIConvertUtils.h"


int main(int argc, char *argv[])
{
  if(argc < 5)
    {
    std::cerr << argv[0]
              << " Usage: FSLTestCompare bvecfile1 bvecfile2 bvalfile1 bvalfile2"
              << std::endl;
    return EXIT_FAILURE;
    }
  std::string bvecfile1(argv[1]);
  std::string bvecfile2(argv[2]);
  std::string bvalfile1(argv[3]);
  std::string bvalfile2(argv[4]);

  unsigned int bVecCount1;
  std::vector< std::vector<double> > bvecs1;
  if(ReadBVecs(bvecs1,bVecCount1,bvecfile1) != EXIT_SUCCESS)
    {
    std::cerr << "Can't read " << bvecfile1 << std::endl;
    return EXIT_FAILURE;
    }
  unsigned int bVecCount2;
  std::vector< std::vector<double> > bvecs2;
  if(ReadBVecs(bvecs2,bVecCount2,bvecfile2) != EXIT_SUCCESS)
    {
    std::cerr << "Can't read " << bvecfile2 << std::endl;
    return EXIT_FAILURE;
    }
  if(bVecCount1 != bVecCount2)
    {
    std::cerr << "Size mismatch: " << bvecfile1 << " (" << bVecCount1
              << ") " << bvecfile2 << " (" << bVecCount2 << ")"
              << std::endl;
    return EXIT_FAILURE;
    }

  unsigned int bValCount1;
  double maxBValue1;
  std::vector<double> bvals1;
  if(ReadBVals(bvals1,bValCount1,bvalfile1,maxBValue1) != EXIT_SUCCESS)
    {
    std::cerr << "Can't read " << bvalfile1 << std::endl;
    return EXIT_FAILURE;
    }
  unsigned int bValCount2;
  double maxBValue2;
  std::vector<double> bvals2;
  if(ReadBVals(bvals2,bValCount2,bvalfile2,maxBValue2) != EXIT_SUCCESS)
    {
    std::cerr << "Can't read " << bvalfile2 << std::endl;
    return EXIT_FAILURE;
    }

  if(bValCount1 != bValCount2)
    {
    std::cerr << "Size mismatch: " << bvalfile1 << " (" << bValCount1
              << ") " << bvalfile2 << " (" << bValCount2 << ")"
              << std::endl;
    return EXIT_FAILURE;
    }

  if(!CloseEnough(bvecs1,bvecs2))
    {
    PrintVec(bvecs1);
    PrintVec(bvecs2);
    return EXIT_FAILURE;
    }

  if(!CloseEnough(bvals1,bvals2,1000.0))
    {
    PrintVec(bvals1);
    PrintVec(bvals2);
    return EXIT_FAILURE;
    }
}
