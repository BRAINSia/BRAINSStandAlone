set(GTRACT_Libraries BRAINSCommonLib GTRACTCommon)
set(GTRACT_TEST_OUTPUT_DIR "${GTRACT_BINARY_DIR}/Testing")
make_directory(${GTRACT_TEST_OUTPUT_DIR})
set(GTRACT_TEST_INPUT_DIR "${GTRACT_SOURCE_DIR}/Data")

message(warning "${CMAKE_BUNDLE_OUTPUT_DIRECTORY}")

# CoregBvalues
# ============
add_executable(gtractCoregBvaluesTests gtractCoregBvaluesTests.cxx)
target_link_libraries(gtractCoregBvaluesTests ${GTRACT_Libraries})
set_target_properties(gtractCoregBvaluesTests PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${GTRACT_BINARY_DIR})

add_test(NAME gtractCoregBvalues_Test COMMAND ${LAUNCH_EXE} $<TARGET_FILE:gtractCoregBvaluesTests>
  --compare ${GTRACT_SOURCE_DIR}/Data/b0_s.nhdr
            ${GTRACT_TEST_OUTPUT_DIR}/b0_s.nhdr
  --compareNumberOfPixelsTolerance 1000
  --compareIntensityTolerance 20
  gtractCoregBvaluesTest
  --fixedVolume ${GTRACT_TEST_INPUT_DIR}/dti1.nhdr
  --movingVolume ${GTRACT_TEST_INPUT_DIR}/dti2.nhdr
  --fixedVolumeIndex 0 --debugLevel 0
  --eddyCurrentCorrection --relaxationFactor 0.25 --maximumStepSize 0.1
  --outputVolume ${GTRACT_TEST_OUTPUT_DIR}/b0_s.nhdr
  --outputTransform ${GTRACT_TEST_OUTPUT_DIR}/b0_s.${XFRM_EXT}
)

# CoRegAnatomy
# ============
add_executable(gtractCoRegAnatomyTests gtractCoRegAnatomyTests.cxx)
target_link_libraries(gtractCoRegAnatomyTests ${GTRACT_Libraries})
set_target_properties(gtractCoRegAnatomyTests PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${GTRACT_BINARY_DIR})

add_test(NAME gtractCoRegAnatomy_Rigid_Test COMMAND ${LAUNCH_EXE} $<TARGET_FILE:gtractCoRegAnatomyTests>
  gtractCoRegAnatomyTest
  --inputVolume ${GTRACT_TEST_OUTPUT_DIR}/b0_s.nhdr
  --vectorIndex 0
  --inputAnatomicalVolume ${GTRACT_TEST_INPUT_DIR}/t1_002.nhdr
  --outputTransformName ${GTRACT_TEST_OUTPUT_DIR}/rigid_s.${XFRM_EXT}
  --numberOfSamples 500000
  --transformType Rigid
  --debugLevel 50
)

add_test(NAME gtractCoRegAnatomy_Bspline_Test COMMAND ${LAUNCH_EXE} $<TARGET_FILE:gtractCoRegAnatomyTests>
  gtractCoRegAnatomyTest
  --inputVolume ${GTRACT_TEST_OUTPUT_DIR}/b0_s.nhdr
  --vectorIndex 0
  --inputAnatomicalVolume ${GTRACT_TEST_INPUT_DIR}/t1_002.nhdr
  --outputTransformName ${GTRACT_TEST_OUTPUT_DIR}/bspline_s.${XFRM_EXT}
  --numberOfIterations 500
  --transformType Bspline
  --gradientTolerance 5e-6
  --inputRigidTransform ${GTRACT_TEST_OUTPUT_DIR}/rigid_s.${XFRM_EXT}
  --gridSize 18,6,18
  --spatialScale 10
  --debugLevel 50
)

# ResampleDWIInPlace
# ==================
MakeTestDriverFromSEMTool(gtractResampleDWIInPlace gtractResampleDWIInPlaceTest.cxx)

set(GTRACT_EXEC gtractResampleDWIInPlace)
set(CURRENT_TEST ${GTRACT_EXEC}_rot30LR)
ExternalData_add_test(${PROJECT_NAME}FetchData NAME ${CURRENT_TEST}
  COMMAND ${LAUNCH_EXE} $<TARGET_FILE:gtractResampleDWIInPlaceTestDriver>
  --compare DATA{${TestData_DIR}/${CURRENT_TEST}.baseline.nrrd}
            ${CMAKE_CURRENT_BINARY_DIR}/${CURRENT_TEST}.result.nrrd
  gtractResampleDWIInPlaceTest
  --inputVolume DATA{${TestData_DIR}/dwi.nrrd}
  --inputTransform DATA{${TestData_DIR}/rot30LR.mat}
  --imagePadding 18,18,15,18,18,15
  --outputVolume ${CMAKE_CURRENT_BINARY_DIR}/${CURRENT_TEST}.result.nrrd
  --debugLevel 50
)
