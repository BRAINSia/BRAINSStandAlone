//
//A test driver to append the
//itk image processing test
//commands to an
//the SEM compatibile program
//

#ifdef WIN32
#define MODULE_IMPORT __declspec(dllimport)
#else
#define MODULE_IMPORT
#endif

extern "C" MODULE_IMPORT int ModuleEntryPoint(int, char* []);

int CreateMaskTest(int argc, char* argv[])
{
  return ModuleEntryPoint(argc, argv);
}

