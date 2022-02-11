// Copyright 2018-2020 Loïc Cerf (lcerf@dcc.ufmg.br)

// This file is part of paf.

// paf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

// paf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

// You should have received a copy of the GNU General Public License along with paf.  If not, see <https://www.gnu.org/licenses/>.

#ifndef DENSE_ROUGH_TENSOR_H_
#define DENSE_ROUGH_TENSOR_H_

#include "AbstractRoughTensor.h"
#include "ConstantShift.h"
#include "ExpectationShift.h"

class DenseRoughTensor final : public AbstractRoughTensor
{
 public:
  DenseRoughTensor(const DenseRoughTensor& otherDenseRoughTensor) = delete;
  DenseRoughTensor(const char* tensorFileName, const char* inputDimensionSeparator, const char* inputElementSeparator, const bool isVerbose);
  DenseRoughTensor(vector<FuzzyTuple>& fuzzyTuples, const float constantShift);
  ~DenseRoughTensor();

  DenseRoughTensor& operator=(const DenseRoughTensor& otherDenseRoughTensor) const = delete;

  Trie getTensor() const;
  void setNoSelection();
  bool isDirectOutput() const;
  TrieWithPrediction projectTensor(const unsigned int nbOfPatternsHavingAllElements);

  float getAverageShift(const vector<vector<unsigned int>>& nSet) const;

 private:
  AbstractShift* shift;
  vector<float> memberships; /* non-empty if only if patterns are to be selected */
  /* PERF: a specific class for a 0/1 tensor where memberships are stored in a dynamic_bitset */

  void init(vector<FuzzyTuple>& fuzzyTuples);
  float updateNullModelQuadraticErrorAndElementMembershipsAndAdvance(vector<unsigned int>& tuple, const float shiftedMembership, vector<vector<pair<float, unsigned int>>>& elementPositiveMemberships, vector<vector<float>>& elementNegativeMemberships);
  void updateNullModelQuadraticErrorAndElementMemberships(const vector<unsigned int>& tuple, const float shiftedMembership, vector<vector<pair<float, unsigned int>>>& elementPositiveMemberships, vector<vector<float>>& elementNegativeMemberships);

  static bool different(const vector<unsigned int>& tuple1, const vector<unsigned int>& tuple2);
};

#endif /*DENSE_ROUGH_TENSOR_H_*/
