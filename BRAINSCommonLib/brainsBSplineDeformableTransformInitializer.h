/*=========================================================================
 *
 *  Copyright Insight Software Consortium
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0.txt
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 *=========================================================================*/
#ifndef __brainsBSplineDeformableTransformInitializer_h
#define __brainsBSplineDeformableTransformInitializer_h

#include "itkObject.h"
#include "itkObjectFactory.h"

#include <iostream>

namespace itk
{
/** \class brainsBSplineDeformableTransformInitializer
 *
 * \breif HACK:  THIS IS AN EXACT DUPLICATE OF THE ITK VERSION, but without the header
 * guard for V3 compatibility.
 *
 * We know that this class has bugs, but they are not fixable in ITKv4 without breaking
 * backwards compatibility.
 */
template< class TTransform, class TImage >
class ITK_EXPORT brainsBSplineDeformableTransformInitializer:public Object
{
public:
  /** Standard class typedefs. */
  typedef brainsBSplineDeformableTransformInitializer Self;
  typedef Object                                Superclass;
  typedef SmartPointer< Self >                  Pointer;
  typedef SmartPointer< const Self >            ConstPointer;

  /** New macro for creation of through a Smart Pointer. */
  itkNewMacro(Self);

  /** Run-time type information (and related methods). */
  itkTypeMacro(brainsBSplineDeformableTransformInitializer, Object);

  /** Type of the transform to initialize */
  typedef TTransform TransformType;

  /** Types defined from transform traits */
  typedef typename TransformType::Pointer        TransformPointer;
  typedef typename TransformType::RegionType     TransformRegionType;
  typedef typename TransformRegionType::SizeType TransformSizeType;

  /** Dimension of parameters. */
  itkStaticConstMacro(SpaceDimension, unsigned int,
                      TransformType::InputSpaceDimension);

  /** Image Types to use in the initialization of the transform */
  typedef   TImage                           ImageType;
  typedef   typename ImageType::ConstPointer ImagePointer;

  /** Set the transform to be initialized */
  itkSetObjectMacro(Transform,   TransformType);

  /** Set the fixed image used in the registration process */
  itkSetConstObjectMacro(Image,  ImageType);

  /** Set the number of grid nodes that we want to place inside the image. This
   * method will override the settings of any previous call to
   * SetNumberOfGridNodesInsideTheImage().  */
  itkSetMacro(GridSizeInsideTheImage,  TransformSizeType);

  /** Set the number of grid nodes that we want to place inside the image. This
   * number of node is used along one dimension of the image.  Therefore, if
   * you pass the number 5 as argument of this method, in a 3D space, then the
   * total number of grid nodes inside the image will be \$ 5 x 5 x 5 \$ .
   * This method will override the settings of any previous call to
   * SetGridSizeInsideTheImage().  */
  void SetNumberOfGridNodesInsideTheImage(unsigned int numberOfNodes)
  {
    this->m_GridSizeInsideTheImage.Fill(numberOfNodes);
    this->Modified();
  }

  /** Initialize the transform using data from the images */
  virtual void InitializeTransform() const;

protected:
  brainsBSplineDeformableTransformInitializer();
  ~brainsBSplineDeformableTransformInitializer(){}

  void PrintSelf(std::ostream & os, Indent indent) const;

private:
  brainsBSplineDeformableTransformInitializer(const Self &); //purposely not
                                                       // implemented
  void operator=(const Self &);                        //purposely not
                                                       // implemented

  TransformPointer m_Transform;

  ImagePointer m_Image;

  TransformSizeType m_GridSizeInsideTheImage;

  unsigned int m_NumberOfGridNodesInsideTheImage;
}; //class brainsBSplineDeformableTransformInitializer
}  // namespace itk

#ifndef ITK_MANUAL_INSTANTIATION
#include "brainsBSplineDeformableTransformInitializer.hxx"
#endif

#endif /* __brainsBSplineDeformableTransformInitializer_h */
