#ifndef NeuralParams_h
#define NeuralParams_h
#include "StringValue.h"
#include "IntValue.h"
#include "FloatValue.h"
#include "ElementParser.h"

class NeuralParams : public ElementParser
{
public:
  typedef ElementParser SuperClass;
  virtual int PrintSelf(std::ostream & os, int indent) const
  {
    indent += SuperClass::PrintSelf(os, indent);
    os << this->PrintSpaces(indent) << "=== NeuralParams ===" << std::endl;
    return indent + 2;
  }

  NeuralParams() : ElementParser("NeuralParams")
  {
    this->Add(new FloatValue("MaskSmoothingValue", 0.0), "MaskSmoothingValue");
    this->Add(new IntValue("GradientProfileSize", 1), "GradientProfileSize");
    this->Add(new StringValue("TrainingVectorFilename", ""), "TrainingVectorFilename");
    this->Add(new StringValue("TestVectorFilename", ""), "TestVectorFilename");
    this->Add(new StringValue("TrainingModelFilename", ""), "TrainingModelFilename");
    this->Add(new StringValue("Normalization", ""), "Normalization");
  }

};

#endif // NeuralParams_h
