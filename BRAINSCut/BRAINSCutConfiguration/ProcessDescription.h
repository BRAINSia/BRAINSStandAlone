#ifndef ProcessDescription_h
#define ProcessDescription_h
#include <CompoundObjectBase.h>
#include <SubjectDataSet.h>
#include <RegistrationParams.h>
#include <ProbabilityMap.h>
#include <list>

class ProcessDescription : public CompoundObjectBase
{
public:
  typedef CompoundObjectBase SuperClass;
  virtual int PrintSelf(std::ostream & os, int indent) const
  {
    indent += SuperClass::PrintSelf(os, indent);
    return indent + 2;
  }

  typedef std::list<SubjectDataSet *> TrainDataSetListType;
  ProcessDescription() : CompoundObjectBase("BRAINSCutProcessDescription")
  {
    this->Add(new DataSetList, "DataSetList");
    this->Add(new ProbabilityMapList, "ProbabilityMapList");
    this->Add(new RegistrationParams, "RegistrationParams");
  }

  void AddDataSet(SubjectDataSet *newSet)
  {
    DataSetList *set = this->Get<DataSetList>("DataSetList");

    set->Add( newSet,
              newSet->GetAttribute<StringValue>("Name") );
  }

  SubjectDataSet * GetAtlasDataSet() const
  {
    const DataSetList *set = this->Get<DataSetList>("DataSetList");
    for( CompoundObjectBase::const_iterator it = set->begin();
         it != set->end();
         ++it )
      {
      SubjectDataSet *current = dynamic_cast<SubjectDataSet *>( it->second );
      if( current->GetAttribute<StringValue>("Type") == "Atlas" )
        {
        return current;
        }
      }
    return 0;
  }

  TrainDataSetListType GetTrainDataSets() const
  {
    const DataSetList *set = this->Get<DataSetList>("DataSetList");

    std::list<SubjectDataSet *> rval;
    for( CompoundObjectBase::const_iterator it = set->begin();
         it != set->end();
         ++it )
      {
      SubjectDataSet *   current = dynamic_cast<SubjectDataSet *>( it->second );
      std::string type( current->GetAttribute<StringValue>("Type") );
      if( type != "Atlas" && type != "Apply" )
        {
        rval.push_back(current);
        }
      }
    return rval;
  }

  TrainDataSetListType GetApplyDataSets() const
  {
    const DataSetList *set = this->Get<DataSetList>("DataSetList");

    std::list<SubjectDataSet *> rval;
    for( CompoundObjectBase::const_iterator it = set->begin();
         it != set->end();
         ++it )
      {
      SubjectDataSet *current = dynamic_cast<SubjectDataSet *>( it->second );
      if( current->GetAttribute<StringValue>("Type") == "Apply" )
        {
        rval.push_back(current);
        }
      }
    return rval;
  }

  const SubjectDataSet::TypeVector ImageTypes() const
  {
    const DataSetList *set = this->Get<DataSetList>("DataSetList");

    if( set->size() == 0 )
      {
      return SubjectDataSet::TypeVector();
      }
    return dynamic_cast<const SubjectDataSet *>( set->begin()->second )->ImageTypes();
  }

};

#endif // ProcessDescription_h
