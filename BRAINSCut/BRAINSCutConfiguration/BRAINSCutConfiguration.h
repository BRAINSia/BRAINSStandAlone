#ifndef BRAINSCutConfiguration_h
#define BRAINSCutConfiguration_h

#include <SubjectDataSet.h>
#include <RegistrationConfigurationParser.h>
#include <ProbabilityMapParser.h>
#include <list>
#include <SpatialLocationType.h>

class BRAINSCutConfiguration : public XMLElementParser
{
public:
  typedef XMLElementParser SuperClass;
  BRAINSCutConfiguration();

  virtual int PrintSelf(std::ostream & os, int indent) const
  {
    indent += SuperClass::PrintSelf(os, indent);
    return indent + 2;
  }

  typedef std::list<SubjectDataSet *> TrainDataSetListType;
  typedef std::list<SubjectDataSet *> ApplyDataSetListType;

  void AddDataSet(SubjectDataSet *newSet);

  SubjectDataSet * GetAtlasDataSet() const;

  TrainDataSetListType GetTrainDataSets() const;

  ApplyDataSetListType GetApplyDataSets() const;

  const SubjectDataSet::StringVectorType GetImageTypes() const;

  // Set/Get Functions
  //
  void SetImageTypeToUse( std::string imageTypeToUse );
  std::string GetImageTypeToUse();

  void SetRegistrationID( std::string registrationID );
  std::string GetRegistrationID();

private:
  std::string ImageTypeToUse;
  std::string RegistrationID;

};

#endif // BRAINSCutConfiguration_h
