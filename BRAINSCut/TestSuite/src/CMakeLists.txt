
## TESTING EX.
## [BRAINSStandAlone_Build_Dir]/bin/testRandomForest  [correct_dir]/optdigits.train [correct_dir]/optdigits.test  [output_dir]/optdigitsTrainedModel.txt
add_executable(testRandomForest testRandomForest.cxx)
target_link_libraries(testRandomForest ${ITK_LIBRARIES} ${OpenCV_LIBRARIES})
