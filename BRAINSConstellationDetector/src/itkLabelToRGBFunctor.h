/*=========================================================================

  Program:   Insight Segmentation & Registration Toolkit
  Module:    $RCSfile: itkLabelToRGBFunctor.h,v $
  Language:  C++
  Date:      $Date: 2009-07-07 12:27:34 $
  Version:   $Revision: 1.11 $

  Copyright (c) Insight Software Consortium. All rights reserved.
  See ITKCopyright.txt or http://www.itk.org/HTML/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notices for more information.

=========================================================================*/

#ifndef __itkLabelToRGBFunctor_h
#define __itkLabelToRGBFunctor_h

namespace itk
{
namespace Functor
{
/** \class LabelToRGBFunctor
 *  \brief Functor for converting labels into RGB triplets.
 *
 * This functor class used internally by LabelToRGBImageFilter
 *
 * \author Gaetan Lehmann. Biologie du Developpement et de la Reproduction,
 * INRA de Jouy-en-Josas, France.
 *
 * \author Richard Beare. Department of
 * Medicine, Monash University, Melbourne, Australia.
 *
 * \sa LabelToRGBImageFilter
 *
 **/
template <class TLabel, class TRGBPixel>
class LabelToRGBFunctor
{
public:

  typedef LabelToRGBFunctor Self;

  LabelToRGBFunctor()
  {
    TRGBPixel rgbPixel;

    typedef typename TRGBPixel::ValueType ValueType;

    // the following colors are from "R", and named:
    // "red"             "green3"          "blue"            "cyan"
    // "magenta"         "darkorange1"     "darkgreen"       "blueviolet"
    // "brown4"          "navy"            "yellow4"         "violetred1"
    // "salmon4"         "turquoise4"      "sienna3"         "darkorchid1"
    // "springgreen4"    "mediumvioletred" "orangered3"      "lightseagreen"
    // "slateblue"       "deeppink1"       "aquamarine4"     "royalblue1"
    // "tomato3"         "mediumblue"      "violetred4"      "darkmagenta"
    // "violet"          "red4"
    // They are a good selection of distinct colours for plotting and
    // overlays.

    AddColor(255, 0, 0);
    AddColor(0, 205, 0);
    AddColor(0, 0, 255);
    AddColor(0, 255, 255);
    AddColor(255, 0, 255);
    AddColor(255, 127, 0);
    AddColor(0, 100, 0);
    AddColor(138, 43, 226);
    AddColor(139, 35, 35);
    AddColor(0, 0, 128);
    AddColor(139, 139, 0);
    AddColor(255, 62, 150);
    AddColor(139, 76, 57);
    AddColor(0, 134, 139);
    AddColor(205, 104, 57);
    AddColor(191, 62, 255);
    AddColor(0, 139, 69);
    AddColor(199, 21, 133);
    AddColor(205, 55, 0);
    AddColor(32, 178, 170);
    AddColor(106, 90, 205);
    AddColor(255, 20, 147);
    AddColor(69, 139, 116);
    AddColor(72, 118, 255);
    AddColor(205, 79, 57);
    AddColor(0, 0, 205);
    AddColor(139, 34, 82);
    AddColor(139, 0, 139);
    AddColor(238, 130, 238);
    AddColor(139, 0, 0);

    // provide some default value for external use (outside
    // LabelToRGBImageFilter)
    // Inside LabelToRGBImageFilter, the values are always initialized
    m_BackgroundColor.Fill(NumericTraits<ValueType>::Zero);
    m_BackgroundValue = NumericTraits<TLabel>::Zero;
  }

  inline TRGBPixel operator()(const TLabel & p) const
  {
    // value is background
    // return a gray pixel with the same intensity than the label pixel
    if( p == m_BackgroundValue )
      {
      return m_BackgroundColor;
      }

    // else, return a colored pixel from the color table
    return m_Colors[p % m_Colors.size()];
  }

  void AddColor(unsigned char r, unsigned char g, unsigned char b)
  {
    TRGBPixel rgbPixel;

    typedef typename TRGBPixel::ValueType ValueType;

    ValueType m = NumericTraits<ValueType>::max();

    rgbPixel.Set( static_cast<ValueType>( static_cast<double>( r ) / 255 * m ),
                  static_cast<ValueType>( static_cast<double>( g ) / 255 * m ),
                  static_cast<ValueType>( static_cast<double>( b ) / 255 * m ) );
    m_Colors.push_back(rgbPixel);
  }

  // Empty the color LUT
  void ResetColors()
  {
    m_Colors.clear();
  }

  // Get number of colors in the LUT
  unsigned int GetNumberOfColors() const
  {
    return m_Colors.size();
  }

  bool operator!=(const Self & l) const
  {
    const bool areDifferent = m_BackgroundColor != l.m_BackgroundColor
      || m_BackgroundValue != l.m_BackgroundValue;

    return areDifferent;
  }

  bool operator==(const Self & other) const
  {
    return !( *this != other );
  }

  void SetBackgroundValue(TLabel v)
  {
    m_BackgroundValue = v;
  }

  void SetBackgroundColor(TRGBPixel rgb)
  {
    m_BackgroundColor = rgb;
  }

  ~LabelToRGBFunctor()
  {
  }

  std::vector<TRGBPixel> m_Colors;

  TRGBPixel m_BackgroundColor;

  TLabel m_BackgroundValue;
};
}  // end namespace functor
}  // end namespace itk

#endif
