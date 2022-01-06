// Copyright 2018,2019 Loïc Cerf (lcerf@dcc.ufmg.br)

// This file is part of paf.

// paf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

// paf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

// You should have received a copy of the GNU General Public License along with paf.  If not, see <https://www.gnu.org/licenses/>.

#include "Trie.h"

bool Trie::is01;

Trie::Trie(): hyperplanes()
{
}

Trie::Trie(Trie&& otherTrie): hyperplanes(std::move(otherTrie.hyperplanes))
{
}

Trie::Trie(const vector<unsigned int>::const_iterator cardinalityIt, const vector<unsigned int>::const_iterator cardinalityEnd): hyperplanes()
{
  unsigned int cardinality = *cardinalityIt;
  hyperplanes.reserve(cardinality);
  if (cardinalityIt + 2 == cardinalityEnd)
    {
      if (is01)
	{
	  do
	    {
	      hyperplanes.push_back(new SparseCrispTube());
	    }
	  while (--cardinality);
	  return;
	}
      do
	{
	  hyperplanes.push_back(new SparseFuzzyTube());
	}
      while (--cardinality);
      return;
    }
  const vector<unsigned int>::const_iterator nextCardinalityIt = cardinalityIt + 1;
  do
    {
      hyperplanes.push_back(new Trie(nextCardinalityIt, cardinalityEnd));
    }
  while (--cardinality);
}

Trie::Trie(vector<float>::const_iterator& membershipIt, const vector<unsigned int>::const_iterator cardinalityIt, const vector<unsigned int>::const_iterator cardinalityEnd): hyperplanes()
{
  unsigned int cardinality = *cardinalityIt;
  hyperplanes.reserve(cardinality);
  if (cardinalityIt + 2 == cardinalityEnd)
    {
      do
	{
	  hyperplanes.push_back(new DenseCrispTube(membershipIt));
	}
      while (--cardinality);
      return;
    }
  const vector<unsigned int>::const_iterator nextCardinalityIt = cardinalityIt + 1;
  do
    {
      hyperplanes.push_back(new Trie(membershipIt, nextCardinalityIt, cardinalityEnd));
    }
  while (--cardinality);
}

Trie::Trie(vector<float>::const_iterator& membershipIt, const int unit, const vector<unsigned int>::const_iterator cardinalityIt, const vector<unsigned int>::const_iterator cardinalityEnd): hyperplanes()
{
  unsigned int cardinality = *cardinalityIt;
  hyperplanes.reserve(cardinality);
  if (cardinalityIt + 2 == cardinalityEnd)
    {
      do
	{
	  hyperplanes.push_back(new DenseFuzzyTube(membershipIt, unit));
	}
      while (--cardinality);
      return;
    }
  const vector<unsigned int>::const_iterator nextCardinalityIt = cardinalityIt + 1;
  do
    {
      hyperplanes.push_back(new Trie(membershipIt, unit, nextCardinalityIt, cardinalityEnd));
    }
  while (--cardinality);
}

Trie::~Trie()
{
  for (AbstractData* hyperplane : hyperplanes)
    {
      delete hyperplane;
    }
}

Trie& Trie::operator=(Trie&& otherTrie)
{
  hyperplanes = std::move(otherTrie.hyperplanes);
  return *this;
}

void Trie::setTuple(const vector<unsigned int>::const_iterator idIt)
{
  AbstractData*& hyperplane = hyperplanes[*idIt];
  if (hyperplane->isFullSparseTube())
    {
      DenseCrispTube* newHyperplane = static_cast<SparseCrispTube*>(hyperplane)->getDenseRepresentation();
      delete hyperplane;
      hyperplane = newHyperplane;
    }
  hyperplane->setTuple(idIt + 1);
}

void Trie::setTuple(const vector<unsigned int>::const_iterator idIt, const int membership)
{
  AbstractData*& hyperplane = hyperplanes[*idIt];
  if (hyperplane->isFullSparseTube())
    {
      DenseFuzzyTube* newHyperplane = static_cast<SparseFuzzyTube*>(hyperplane)->getDenseRepresentation();
      delete hyperplane;
      hyperplane = newHyperplane;
    }
  hyperplane->setTuple(idIt + 1, membership);
}

void Trie::sortTubes()
{
  for (AbstractData* hyperplane : hyperplanes)
    {
      hyperplane->sortTubes();
    }
}

void Trie::clearAndFree()
{
  hyperplanes.clear();
  hyperplanes.shrink_to_fit();
}

void Trie::sumOnPattern(const vector<vector<unsigned int>>::const_iterator dimensionIt, int& sum) const
{
  const vector<vector<unsigned int>>::const_iterator nextDimensionIt = dimensionIt + 1;
  for (const unsigned int id : *dimensionIt)
    {
      hyperplanes[id]->sumOnPattern(nextDimensionIt, sum);
    }
}

long long Trie::membershipSum(const vector<vector<unsigned int>>& nSet) const
{
  unsigned long long sum = 0;
  const vector<vector<unsigned int>>::const_iterator secondDimensionIt = ++nSet.begin();
  for (const unsigned int id : nSet.front())
    {
      int sumOnSlice = 0;
      hyperplanes[id]->sumOnPattern(secondDimensionIt, sumOnSlice);
      sum += sumOnSlice;
    }
  return sum;
}

long long Trie::nbOfPresentTuples(const vector<vector<unsigned int>>& nSet) const
{
  int nb = 0;
  sumOnPattern(nSet.begin(), nb);
  return nb;
}

vector<vector<int>> Trie::sumsOnExtensions(const vector<vector<unsigned int>>::const_iterator nSetBegin, const vector<unsigned int>& cardinalities) const
{
  vector<vector<unsigned int>>::const_iterator dimensionIt = nSetBegin;
  vector<vector<int>> sums;
  sums.reserve(cardinalities.size());
  for (const unsigned int cardinality : cardinalities)
    {
      vector<int> sumsInDimension(cardinality);
      for (const unsigned int presentElementId : *dimensionIt)
	{
	  sumsInDimension[presentElementId] = numeric_limits<int>::min();
	}
      sums.emplace_back(std::move(sumsInDimension));
      ++dimensionIt;
    }
  sumsOnExtensions(nSetBegin, sums.begin());
  return sums;
}

void Trie::sumsOnExtensions(const vector<vector<unsigned int>>::const_iterator dimensionIt, const vector<vector<int>>::iterator sumsIt) const
{
  const vector<vector<unsigned int>>::const_iterator nextDimensionIt = dimensionIt + 1;
  const vector<vector<int>>::iterator nextSumsIt = sumsIt + 1;
  vector<AbstractData*>::const_iterator hyperplaneIt = hyperplanes.begin();
  for (int& sum : *sumsIt)
    {
      if (sum == numeric_limits<int>::min())
	{
	  (*hyperplaneIt)->sumsOnExtensions(nextDimensionIt, nextSumsIt);
	}
      else
	{
	  (*hyperplaneIt)->sumOnPattern(nextDimensionIt, sum);
	}
      ++hyperplaneIt;
    }
}

void Trie::updateSumsOnExtensionsAfterExtension(const vector<vector<unsigned int>>::const_iterator dimensionIt, const vector<vector<int>>::iterator sumsIt, const vector<vector<int>>::iterator sumsInExtendedDimensionIt) const
{
  const vector<vector<unsigned int>>::const_iterator nextDimensionIt = dimensionIt + 1;
  const vector<vector<int>>::iterator nextSumsIt = sumsIt + 1;
  if (sumsIt == sumsInExtendedDimensionIt)
    {
      hyperplanes[dimensionIt->front()]->sumsOnExtensions(nextDimensionIt, nextSumsIt);
      return;
    }
  vector<AbstractData*>::const_iterator hyperplaneIt = hyperplanes.begin();
  for (int& sum : *sumsIt)
    {
      if (sum == numeric_limits<int>::min())
	{
	  (*hyperplaneIt)->updateSumsOnExtensionsAfterExtension(nextDimensionIt, nextSumsIt, sumsInExtendedDimensionIt);
	}
      else
	{
	  (*hyperplaneIt)->sumOnPattern(nextDimensionIt, sum);
	}
      ++hyperplaneIt;
    }
}

vector<int>::const_iterator Trie::maxExtension(const vector<int>& extensionsInDimension)
{
  // Find the greatest iterator (to favor elements with larger membership sums) with the largest number of present tuples in extensionInDimension
  vector<int>::const_iterator maxExtensionInDimensionIt = extensionsInDimension.begin();
  const vector<int>::const_iterator extensionInDimensionEnd = extensionsInDimension.end();
  for (vector<int>::const_iterator extensionInDimensionIt = maxExtensionInDimensionIt; ++extensionInDimensionIt != extensionInDimensionEnd; )
    {
      if (*extensionInDimensionIt >= *maxExtensionInDimensionIt)
	{
	  maxExtensionInDimensionIt = extensionInDimensionIt;
	}
    }
  return maxExtensionInDimensionIt;
}
