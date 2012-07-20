#-- #NOTES from http: // www.cmake.org/Wiki/CMake_Testing_With_CTest
#set(CTEST_CUSTOM_MEMCHECK_IGNORE
#    $ {CTEST_CUSTOM_MEMCHECK_IGNORE}
#    DummyExcludeMemcheckIgnoreTestSetGet
#    )

#-- #set(CTEST_CUSTOM_WARNING_MATCH
#-- #${CTEST_CUSTOM_WARNING_MATCH}
#-- #"{standard input}:[0-9][0-9]*: Warning: "
#-- #)

#-- #IF("@CMAKE_SYSTEM@" MATCHES "OSF")
#set(CTEST_CUSTOM_WARNING_EXCEPTION
#    $ {CTEST_CUSTOM_WARNING_EXCEPTION}
#    )
#-- #ENDIF("@CMAKE_SYSTEM@" MATCHES "OSF")

#-- #The following are brains2 warnings that just need to be suppressed because they are caused
#-- #by third parties, and will never be fixed.
#set(CTEST_CUSTOM_WARNING_EXCEPTION
#    "SlicerExecutionModel"
#    "VTK/Utilities/vtktiff/"
#    "Utilities/hdf5/"
#    "warning LNK4221"
#    "variable .var_args[2]*. is used before its value is set"
#    "qHullLib"
#    "bkHull.cxx:[0-9]+: warning: dereferencing type-punned pointer will break strict-aliasing rules"
#    "warning #1170: invalid redeclaration of nested class"
#    )
##Intel compiler does not like itkLegacyMacro warning #1170

#-- #Reset maximum number of warnings so that they all show up.
set(CTEST_CUSTOM_MAXIMUM_NUMBER_OF_WARNINGS 1000)

#set(CTEST_CUSTOM_COVERAGE_EXCLUDE $ {CTEST_CUSTOM_COVERAGE_EXCLUDE}
#    "./SlicerExecutionModel/"
#    "./SlicerExecutionModel/.*"
#    "./SlicerExecutionModel/.*/.*"
#    ".*SlicerExecutionModel.*"
#    "SlicerExecutionModel"
#    )

