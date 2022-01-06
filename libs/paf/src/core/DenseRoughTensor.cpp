// Copyright 2018-2021 Loïc Cerf (lcerf@dcc.ufmg.br)

// This file is part of paf.

// paf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

// paf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

// You should have received a copy of the GNU General Public License along with paf.  If not, see <https://www.gnu.org/licenses/>.

#include "DenseRoughTensor.h"

DenseRoughTensor::DenseRoughTensor(const char* tensorFileName, const char* inputDimensionSeparator, const char* inputElementSeparator, const bool isVerbose): shift(), memberships()
{
  vector<FuzzyTuple> fuzzyTuples = getFuzzyTuples(tensorFileName, inputDimensionSeparator, inputElementSeparator, isVerbose);
  Trie::is01 = false;
  shift = new ExpectationShift(fuzzyTuples, ids2Labels);
  init(fuzzyTuples);
}

DenseRoughTensor::DenseRoughTensor(vector<FuzzyTuple>& fuzzyTuples, const float constantShift): shift(new ConstantShift(constantShift)), memberships()
{
  init(fuzzyTuples);
  if (Trie::is01)
    {
      SparseCrispTube::setDefaultMembership(unit * -constantShift);
    }
}

DenseRoughTensor::~DenseRoughTensor()
{
  delete shift;
}

void DenseRoughTensor::init(vector<FuzzyTuple>& fuzzyTuples)
{
  nullModelQuadraticError = 0;
  // Initialize tuple and positive/negative memberships of the elements
  unsigned long long nbOfTuples = 1;
  vector<unsigned int> tuple;
  tuple.reserve(ids2Labels.size());
  vector<vector<pair<float, unsigned int>>> elementPositiveMemberships;
  elementPositiveMemberships.reserve(ids2Labels.size());
  vector<vector<float>> elementNegativeMemberships;
  elementNegativeMemberships.reserve(ids2Labels.size());
  for (const vector<string>& labelsInDimension : ids2Labels)
    {
      const unsigned int nbOfElements = labelsInDimension.size();
      nbOfTuples *= nbOfElements;
      tuple.push_back(nbOfElements - 1);
      vector<pair<float, unsigned int>> elementPositiveMembershipsInDimension;
      elementPositiveMembershipsInDimension.reserve(nbOfElements);
      for (unsigned int id = 0; id != nbOfElements; ++id)
	{
	  elementPositiveMembershipsInDimension.emplace_back(0, id);
	}
      elementPositiveMemberships.emplace_back(std::move(elementPositiveMembershipsInDimension));
      elementNegativeMemberships.emplace_back(nbOfElements);
    }
  vector<float> shiftedMemberships(nbOfTuples);
  vector<float>::reverse_iterator shiftedMembershipIt = shiftedMemberships.rbegin(); // filled backwards, so that in lexicographic order of the tuples
  const vector<FuzzyTuple>::const_iterator end = --fuzzyTuples.end();
  vector<FuzzyTuple>::const_iterator fuzzyTupleIt = fuzzyTuples.begin();
  for (; fuzzyTupleIt != end; ++fuzzyTupleIt)
    {
      while (different(fuzzyTupleIt->getTuple(), tuple))
	{
	  *shiftedMembershipIt++ = updateNullModelQuadraticErrorAndElementMembershipsAndAdvance(tuple, -shift->getShift(tuple), elementPositiveMemberships, elementNegativeMemberships);
	}
      *shiftedMembershipIt++ = updateNullModelQuadraticErrorAndElementMembershipsAndAdvance(tuple, fuzzyTupleIt->getMembership() - shift->getShift(tuple), elementPositiveMemberships, elementNegativeMemberships);
    }
  // fuzzyTupleIt->getTuple() is necessarily a vector of zero (first fuzzy tuple that was read): no more tuple
  *shiftedMembershipIt = fuzzyTupleIt->getMembership() - shift->getShift(tuple);
  updateNullModelQuadraticErrorAndElementMemberships(tuple, *shiftedMembershipIt, elementPositiveMemberships, elementNegativeMemberships);
  fuzzyTuples.clear();
  fuzzyTuples.shrink_to_fit();
  // Compute new ids, in increasing order of element membership, set unit, cardinalities and external2InternalDimensionOrder
  setMetadata(elementPositiveMemberships, elementNegativeMemberships);
  // Inform the shift of the new dimension order
  shift->setNewDimensionOrderAndNewIds(external2InternalDimensionOrder, elementPositiveMemberships);
  // Compute the offsets to access shiftedMemberships and init tuple to the last one
  vector<unsigned int>::iterator tupleIt = tuple.begin();
  vector<unsigned int>::const_iterator cardinalityIt = cardinalities.begin();
  vector<vector<string>>::const_reverse_iterator labelsInDimensionIt = ids2Labels.rbegin();
  unsigned int offset = 1;
  vector<unsigned int> offsets(ids2Labels.size());
  const vector<unsigned int>::reverse_iterator rend = offsets.rend();
  for (vector<unsigned int>::reverse_iterator offsetIt = offsets.rbegin(); offsetIt != rend; ++offsetIt)
    {
      *offsetIt = offset;
      offset *= labelsInDimensionIt->size();
      ++labelsInDimensionIt;
      *tupleIt++ = *cardinalityIt++ - 1;
    }
  // Compute memberships, reodering of shiftedMemberships according to external2InternalDimensionOrder
  memberships.resize(nbOfTuples);
  for (vector<float>::reverse_iterator membershipIt = memberships.rbegin(); ; ++membershipIt) // filled backwards, so that in lexicographic order of the tuples
    {
      unsigned long long membershipIndex = 0;
      vector<unsigned int>::const_iterator offsetIt = offsets.begin();
      vector<vector<pair<float, unsigned int>>>::const_iterator elementPositiveMembershipsInDimensionIt = elementPositiveMemberships.begin();
      for (const unsigned int internalDimensionId : external2InternalDimensionOrder)
	{
	  membershipIndex += (*elementPositiveMembershipsInDimensionIt)[tuple[internalDimensionId]].second * *offsetIt;
	  ++offsetIt;
	  ++elementPositiveMembershipsInDimensionIt;
	}
      *membershipIt = shiftedMemberships[membershipIndex];
      if (--nbOfTuples == 0)
	{
	  break;
	}
      vector<unsigned int>::reverse_iterator elementIt = tuple.rbegin();
      for (vector<unsigned int>::const_reverse_iterator cardinalityIt = cardinalities.rbegin(); *elementIt == 0; ++cardinalityIt)
	{
	  *elementIt++ = *cardinalityIt - 1;
	}
      --*elementIt;
    }
}

float DenseRoughTensor::updateNullModelQuadraticErrorAndElementMembershipsAndAdvance(vector<unsigned int>& tuple, const float shiftedMembership, vector<vector<pair<float, unsigned int>>>& elementPositiveMemberships, vector<vector<float>>& elementNegativeMemberships)
{
  updateNullModelQuadraticErrorAndElementMemberships(tuple, shiftedMembership, elementPositiveMemberships, elementNegativeMemberships);
  // Advance tuple, big-endian-like
  vector<unsigned int>::reverse_iterator elementIt = tuple.rbegin();
  for (vector<vector<string>>::const_reverse_iterator labelsInDimensionReverseIt = ids2Labels.rbegin(); *elementIt == 0; ++labelsInDimensionReverseIt)
    {
      *elementIt++ = labelsInDimensionReverseIt->size() - 1;
    }
  --*elementIt;
  return shiftedMembership;
}

void DenseRoughTensor::updateNullModelQuadraticErrorAndElementMemberships(const vector<unsigned int>& tuple, const float shiftedMembership, vector<vector<pair<float, unsigned int>>>& elementPositiveMemberships, vector<vector<float>>& elementNegativeMemberships)
{
  nullModelQuadraticError += shiftedMembership * shiftedMembership; // the quadratic error of the null model on the tuples read so far
  if (shiftedMembership < 0)
    {
      vector<vector<float>>::iterator elementNegativeMembershipsInDimensionIt = elementNegativeMemberships.begin();
      for (const unsigned int id : tuple)
	{
	  (*elementNegativeMembershipsInDimensionIt)[id] += shiftedMembership;
	  ++elementNegativeMembershipsInDimensionIt;
	}
      return;
    }
  vector<vector<pair<float, unsigned int>>>::iterator elementPositiveMembershipsInDimensionIt = elementPositiveMemberships.begin();
  for (const unsigned int id : tuple)
    {
      (*elementPositiveMembershipsInDimensionIt)[id].first += shiftedMembership;
      ++elementPositiveMembershipsInDimensionIt;
    }
}

Trie DenseRoughTensor::getTensor() const
{
  vector<float>::const_iterator membershipIt = memberships.begin();
  if (Trie::is01)
    {
      DenseCrispTube::setSize(cardinalities.back());
      return Trie(membershipIt, cardinalities.begin(), cardinalities.end());
    }
  DenseFuzzyTube::setSize(cardinalities.back());
  return Trie(membershipIt, unit, cardinalities.begin(), cardinalities.end());
}

void DenseRoughTensor::setNoSelection()
{
  memberships.clear();
  memberships.shrink_to_fit();
}

bool DenseRoughTensor::isDirectOutput() const
{
  return memberships.empty();
}

TrieWithPrediction DenseRoughTensor::projectTensor(const unsigned int nbOfPatternsHavingAllElements)
{
  // Compute the offsets to access memberships from the non-updated cardinalities
  unsigned int offset = 1;
  vector<unsigned int>::const_reverse_iterator cardinalityIt = cardinalities.rbegin();
  vector<unsigned int> offsets(cardinalities.size() - 1);
  const vector<unsigned int>::reverse_iterator rend = offsets.rend();
  for (vector<unsigned int>::reverse_iterator offsetIt = offsets.rbegin(); offsetIt != rend; ++offsetIt)
    {
      offset *= *cardinalityIt++;
      *offsetIt = offset;
    }
  // Update cardinalities, ids2Labels and candidateVariables
  const vector<vector<unsigned int>> newIds2OldIds = projectMetadata(nbOfPatternsHavingAllElements, false);
  // Inform the shift of the new ids
  shift->setNewIds(newIds2OldIds);
  // Compute last tuple and nb of tuples, according to new cardinalities
  vector<unsigned int> tuple;
  tuple.reserve(cardinalities.size());
  unsigned long long nbOfSelectedTuples = 1;
  for (const unsigned int cardinality : cardinalities)
    {
      nbOfSelectedTuples *= cardinality;
      tuple.push_back(cardinality - 1);
    }
  // Select memberships in reduced tensor, compute negative/positive memberships of elements in first dimension and the quadratic error of the null model
  float unitDenominator = 0;
  vector<float> elementNegativeMemberships(cardinalities.front());
  vector<float> elementPositiveMemberships(cardinalities.front());
  vector<float> selectedMemberships(nbOfSelectedTuples);
  for (vector<float>::reverse_iterator selectedMembershipIt = selectedMemberships.rbegin(); ; ++selectedMembershipIt) // filled backwards, so that in lexicographic order of the tuples
    {
      unsigned long long membershipIndex = 0;
      vector<vector<unsigned int>>::const_iterator newIds2OldIdsIt = newIds2OldIds.begin();
      vector<unsigned int>::const_iterator idIt = tuple.begin();
      for (const unsigned int offset : offsets)
	{
	  membershipIndex += offset * (*newIds2OldIdsIt)[*idIt];
	  ++newIds2OldIdsIt;
	  ++idIt;
	}
      const float membership = memberships[membershipIndex + (*newIds2OldIdsIt)[*idIt]];
      *selectedMembershipIt = membership;
      if (membership < 0)
	{
	  elementNegativeMemberships[tuple.front()] -= membership;
	}
      else
	{
	  elementPositiveMemberships[tuple.front()] += membership;
	}
      unitDenominator += membership * membership;
      if (--nbOfSelectedTuples == 0)
	{
	  break;
	}
      vector<unsigned int>::reverse_iterator elementIt = tuple.rbegin();
      for (vector<unsigned int>::const_reverse_iterator cardinalityIt = cardinalities.rbegin(); *elementIt == 0; ++cardinalityIt)
	{
	  *elementIt++ = *cardinalityIt - 1;
	}
      --*elementIt;
    }
  setNoSelection();
  // Compute unit
#if defined NUMERIC_PRECISION && defined GNUPLOT
  cout << '\t' << max(sqrt(unitDenominator), max(*max_element(elementNegativeMemberships.begin(), elementNegativeMemberships.end()), *max_element(elementPositiveMemberships.begin(), elementPositiveMemberships.end()))) / numeric_limits<int>::max();
#endif
  setUnit(static_cast<float>(numeric_limits<int>::max()) / max(sqrt(unitDenominator), max(*max_element(elementNegativeMemberships.begin(), elementNegativeMemberships.end()), *max_element(elementPositiveMemberships.begin(), elementPositiveMemberships.end()))));
  // Construct TrieWithPrediction
  vector<float>::const_iterator selectedMembershipIt = selectedMemberships.begin();
  return TrieWithPrediction(selectedMembershipIt, unit, cardinalities.begin(), cardinalities.end());
}

float DenseRoughTensor::getAverageShift(const vector<vector<unsigned int>>& nSet) const
{
  return shift->getAverageShift(nSet);
}

bool DenseRoughTensor::different(const vector<unsigned int>& tuple1, const vector<unsigned int>& tuple2)
{
  // Comparing in the reverse order because the last ids are more likely to be different
  const vector<unsigned int>::const_reverse_iterator tuple1End = tuple1.rend();
  vector<unsigned int>::const_reverse_iterator tuple1It = tuple1.rbegin();
  for (vector<unsigned int>::const_reverse_iterator tuple2It = tuple2.rbegin(); tuple1It != tuple1End && *tuple1It++ == *tuple2It++; )
    {
    }
  return tuple1It != tuple1End;
}
