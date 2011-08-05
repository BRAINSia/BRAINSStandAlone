/*=========================================================================

 Program:   GTRACT (Guided Tensor Restore Anatomical Connectivity Tractography)
 Module:    $RCSfile: $
 Language:  C++
 Date:      $Date: 2006/03/29 14:53:40 $
 Version:   $Revision: 1.9 $

   Copyright (c) University of Iowa Department of Radiology. All rights reserved.
   See GTRACT-Copyright.txt or http://mri.radiology.uiowa.edu/copyright/GTRACT-Copyright.txt
   for details.

      This software is distributed WITHOUT ANY WARRANTY; without even
      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
      PURPOSE.  See the above copyright notices for more information.

=========================================================================*/

#ifndef __itkVTKImageExportBase_h
#define __itkVTKImageExportBase_h

#include "itkProcessObject.h"
#include "gtractCommonWin32.h"

namespace itk
{
/** \class VTKImageExportBase
 * \brief Superclass for VTKImageExport instantiations.
 *
 * VTKImageExportBase provides the functions that serve as callbacks
 * given to vtkImageImport to connect the end of an ITK pipeline to
 * the beginning of a VTK pipeline.
 *
 * \ingroup IOFilters
 * \sa VTKImageExport
 */
class GTRACT_COMMON_EXPORT VTKImageExportBase : public ProcessObject
{
public:
  /** Standard class typedefs. */
  typedef VTKImageExportBase       Self;
  typedef ProcessObject            Superclass;
  typedef SmartPointer<Self>       Pointer;
  typedef SmartPointer<const Self> ConstPointer;

  /** Run-time type information (and related methods). */
  itkTypeMacro(VTKImageExportBase, ProcessObject);

  /** Returns the user data to set for the vtkImageImport callbacks. */
  void * GetCallbackUserData();

  /** The function pointer type vcl_expected for a callback. */
  typedef void ( *        UpdateInformationCallbackType )(void *);
  typedef int ( *         PipelineModifiedCallbackType )(void *);
  typedef int * ( *       WholeExtentCallbackType )(void *);
  typedef double * ( *    SpacingCallbackType )(void *);
  typedef double * ( *    OriginCallbackType )(void *);
  typedef const char * ( *ScalarTypeCallbackType )(void *);
  typedef int ( *         NumberOfComponentsCallbackType )(void *);
  typedef void ( *        PropagateUpdateExtentCallbackType )(void *, int *);
  typedef void ( *        UpdateDataCallbackType )(void *);
  typedef int * ( *       DataExtentCallbackType )(void *);
  typedef void * ( *      BufferPointerCallbackType )(void *);

  /** Compatibility for VTK older than 4.4.  */
  typedef float * ( *FloatSpacingCallbackType )(void *);
  typedef float * ( *FloatOriginCallbackType )(void *);

  /** Provide compatibility between VTK 4.4 and earlier versions.  */
  class CallbackTypeProxy
  {
public:
    typedef double * ( *DoubleCallbackType )(void *);
    typedef float * ( * FloatCallbackType )(void *);
    operator DoubleCallbackType()
      {
      return m_DoubleCallback;
      }

    operator FloatCallbackType()
      {
      return m_FloatCallback;
      }
    CallbackTypeProxy(DoubleCallbackType d, FloatCallbackType f) :
      m_DoubleCallback(d), m_FloatCallback(f)
    {
    }
private:
    DoubleCallbackType m_DoubleCallback;
    FloatCallbackType  m_FloatCallback;
  };

  /** Get a pointer to function to set as a callback in vtkImageImport. */
  UpdateInformationCallbackType     GetUpdateInformationCallback() const;

  PipelineModifiedCallbackType      GetPipelineModifiedCallback() const;

  WholeExtentCallbackType           GetWholeExtentCallback() const;

  CallbackTypeProxy                 GetSpacingCallback() const;

  CallbackTypeProxy                 GetOriginCallback() const;

  ScalarTypeCallbackType            GetScalarTypeCallback() const;

  NumberOfComponentsCallbackType    GetNumberOfComponentsCallback() const;

  PropagateUpdateExtentCallbackType GetPropagateUpdateExtentCallback() const;

  UpdateDataCallbackType            GetUpdateDataCallback() const;

  DataExtentCallbackType            GetDataExtentCallback() const;

  BufferPointerCallbackType         GetBufferPointerCallback() const;

protected:
  VTKImageExportBase();
  ~VTKImageExportBase()
  {
  }
  void PrintSelf(std::ostream & os, Indent indent) const;

  typedef DataObject::Pointer DataObjectPointer;

  virtual void UpdateInformationCallback();

  virtual int PipelineModifiedCallback();

  virtual void UpdateDataCallback();

  /** These callbacks are image-type specific, and are implemented
   * in VTKImageExport. */
  virtual int * WholeExtentCallback() = 0;

  virtual double * SpacingCallback() = 0;

  virtual double * OriginCallback() = 0;

  virtual float * FloatSpacingCallback() = 0;

  virtual float * FloatOriginCallback() = 0;

  virtual const char * ScalarTypeCallback() = 0;

  virtual int NumberOfComponentsCallback() = 0;

  virtual void PropagateUpdateExtentCallback(int *) = 0;

  virtual int * DataExtentCallback() = 0;

  virtual void * BufferPointerCallback() = 0;

private:
  VTKImageExportBase(const Self &); // purposely not implemented
  void operator=(const Self &);     // purposely not implemented

  /** Actual function sent to VTK as a callback.  Casts the user data
   * to a VTKImageExportBase pointer and invokes the corresponding
   * virtual method in that instance. */
  static void UpdateInformationCallbackFunction(void *);

  static int PipelineModifiedCallbackFunction(void *);

  static int * WholeExtentCallbackFunction(void *);

  static double * SpacingCallbackFunction(void *);

  static double * OriginCallbackFunction(void *);

  static float * FloatSpacingCallbackFunction(void *);

  static float * FloatOriginCallbackFunction(void *);

  static const char * ScalarTypeCallbackFunction(void *);

  static int NumberOfComponentsCallbackFunction(void *);

  static void PropagateUpdateExtentCallbackFunction(void *, int *);

  static void UpdateDataCallbackFunction(void *);

  static int * DataExtentCallbackFunction(void *);

  static void * BufferPointerCallbackFunction(void *);

private:
  /** PipelineMTime from the last call to PipelineModifiedCallback. */
  unsigned long m_LastPipelineMTime;
};
} // end namespace itk

#endif
