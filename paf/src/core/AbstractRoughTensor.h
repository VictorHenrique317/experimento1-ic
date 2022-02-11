// Copyright 2018-2020 Loïc Cerf (lcerf@dcc.ufmg.br)

// This file is part of paf.

// paf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

// paf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

// You should have received a copy of the GNU General Public License along with paf.  If not, see <https://www.gnu.org/licenses/>.

#ifndef ABSTRACT_ROUGH_TENSOR_H_
#define ABSTRACT_ROUGH_TENSOR_H_

#include <cmath>
#include <iostream>

#include "../utilities/NoOutputException.h"
#include "../utilities/UsageException.h"
#include "FuzzyTupleFileReader.h"
#include "Trie.h"
#include "TrieWithPrediction.h"

#if defined TIME || defined DETAILED_TIME
#include <chrono>

using namespace std::chrono;
#endif

class AbstractRoughTensor
{
 public:
  virtual ~AbstractRoughTensor();

  virtual void setNoSelection() = 0;
  virtual Trie getTensor() const = 0;
  virtual bool isDirectOutput() const = 0;
  virtual TrieWithPrediction projectTensor(const unsigned int nbOfPatternsHavingAllElements) = 0;
  virtual float getAverageShift(const vector<vector<unsigned int>>& nSet) const = 0;

  void printPattern(const vector<vector<unsigned int>>& nSet, const float density, ostream& out) const;
  void output(const vector<vector<unsigned int>>& nSet, const float density) const;
  void output(const vector<vector<unsigned int>>& nSet, const float density, const vector<unsigned int>& children) const;

  static AbstractRoughTensor* makeRoughTensor(const char* tensorFileName, const char* inputDimensionSeparator, const char* inputElementSeparator, const float densityThreshold, const bool isVerbose);
  static AbstractRoughTensor* makeRoughTensor(const char* tensorFileName, const char* inputDimensionSeparator, const char* inputElementSeparator, const float densityThreshold, const float shift, const bool isVerbose);

  static void setOutput(const char* outputFileName, const char* outputDimensionSeparator, const char* outputElementSeparator, const char* hierarchyPrefix, const char* hierarchySeparator, const char* sizePrefix, const char* sizeSeparator, const char* areaPrefix, const bool isPrintLambda, const bool isSizePrinted, const bool isAreaPrinted);
  static int getUnit();
  static const vector<unsigned int>& getCardinalities();
  static const vector<vector<string>>& getIds2Labels();
  static const vector<unsigned int>& getExternal2InternalDimensionOrder();
  static void moveAsCandidateVariable(vector<vector<unsigned int>>& nSet);
  static void reserveAdditionalCandidateVariables(const unsigned int nbOfAdditionalCandidateVariables);
  static vector<vector<vector<unsigned int>>>& getCandidateVariables();
  static double getNullModelQuadraticError();

#if defined DEBUG_GROW || defined DEBUG_AGGLOMERATE
  static unsigned int externalDimensionId(const unsigned int dimensionId);
  static void printElement(const unsigned int dimensionId, const unsigned int elementId, ostream& out);
#endif
#ifdef TIME
  static void printCurrentDuration();
#endif

 protected:
  static vector<vector<string>> ids2Labels;
  static double nullModelQuadraticError;
  static vector<unsigned int> cardinalities;
  static int unit;
  static vector<unsigned int> external2InternalDimensionOrder;

  static void setUnit(const int unit);
  static vector<FuzzyTuple> getFuzzyTuples(const char* tensorFileName, const char* inputDimensionSeparator, const char* inputElementSeparator, const bool isVerbose);
  static unsigned long long getTensorArea();
  static void setMetadata(vector<FuzzyTuple>& fuzzyTuples, const float shift);
  static void setMetadata(vector<vector<pair<float, unsigned int>>>& elementPositiveMemberships, const vector<vector<float>>& elementNegativeMemberships); /* the inner vectors of elementPositiveMemberships are reordered by increasing element membership, hence a mapping from new ids (the index) and old ids (the second component of the pairs) */
  static vector<vector<unsigned int>> projectMetadata(const unsigned int nbOfPatternsHavingAllElements, const bool isReturningOld2New);

 private:
  static ofstream outputFile;
  static string outputDimensionSeparator;
  static string outputElementSeparator;
  static string hierarchyPrefix;
  static string hierarchySeparator;
  static string sizePrefix;
  static string sizeSeparator;
  static string areaPrefix;
  static bool isPrintLambda;
  static bool isSizePrinted;
  static bool isAreaPrinted;
  static vector<vector<vector<unsigned int>>> candidateVariables;

#if defined TIME || defined DETAILED_TIME
  static steady_clock::time_point overallBeginning;
#ifdef DETAILED_TIME
  static steady_clock::time_point shiftingBeginning;
#endif
#endif

  static AbstractRoughTensor* makeRoughTensor(vector<FuzzyTuple>& fuzzyTuples, const float densityThreshold, const float shift);
};

#endif /*ABSTRACT_ROUGH_TENSOR_H_*/
