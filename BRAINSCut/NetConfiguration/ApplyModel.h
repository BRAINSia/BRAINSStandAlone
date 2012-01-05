#ifndef ApplyModel_h
#define ApplyModel_h
#include "StringValue.h"
#include "IntValue.h"
#include "FloatValue.h"
#include "XMLElementParser.h"

class ApplyModelType : public XMLElementParser
{
public:
  typedef XMLElementParser SuperClass;
  virtual int PrintSelf(std::ostream & os, int indent) const
  {
    indent += SuperClass::PrintSelf(os, indent);
    os << this->PrintSpaces(indent) << "=== ApplyModelType ===" << std::endl;
    return indent + 2;
  }

  ApplyModelType() : XMLElementParser("ApplyModel")
  {
    this->Add(new FloatValue("MaskThresh", 0.5), "MaskThresh");
    this->Add(new StringValue("LevelSetImageType", ""), "LevelSetImageType");
  }

};

#endif // ApplyModel_h
