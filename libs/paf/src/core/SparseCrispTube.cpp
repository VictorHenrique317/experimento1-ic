// Copyright 2018,2019 Loïc Cerf (lcerf@dcc.ufmg.br)

// This file is part of paf.

// paf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

// paf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

// You should have received a copy of the GNU General Public License along with paf.  If not, see <https://www.gnu.org/licenses/>.

#include "SparseCrispTube.h"

long long SparseCrispTube::defaultMembership;
unsigned int SparseCrispTube::sizeLimit;

SparseCrispTube::SparseCrispTube(): tube()
{
}

bool SparseCrispTube::isFullSparseTube() const
{
  return tube.size() == sizeLimit;
}

void SparseCrispTube::setTuple(const vector<unsigned int>::const_iterator idIt)
{
  tube.push_back(*idIt);
}

DenseCrispTube* SparseCrispTube::getDenseRepresentation() const
{
  return new DenseCrispTube(tube);
}

void SparseCrispTube::sortTubes()
{
  tube.shrink_to_fit();
  sort(tube.begin(), tube.end());
}

void SparseCrispTube::sumOnPattern(const vector<vector<unsigned int>>::const_iterator dimensionIt, int& nbOfPresentTuples) const
{
  const vector<unsigned int>::const_iterator tubeEnd = tube.end();
  vector<unsigned int>::const_iterator tubeBegin = tube.begin();
  const vector<unsigned int>::const_iterator idEnd = dimensionIt->end();
  for (vector<unsigned int>::const_iterator idIt = dimensionIt->begin(); idIt != idEnd; ++idIt)
    {
      tubeBegin = lower_bound(tubeBegin, tubeEnd, *idIt);
      if (tubeBegin == tubeEnd)
	{
	  return;
	}
      if (*tubeBegin == *idIt)
	{
	  ++nbOfPresentTuples;
	}
    }
}

void SparseCrispTube::sumsOnExtensions(const vector<vector<unsigned int>>::const_iterator dimensionIt, const vector<vector<int>>::iterator numbersOfPresentTuplesIt) const
{
  for (const unsigned int elementId : tube)
    {
      int& currentNumberOfPresentTuples = (*numbersOfPresentTuplesIt)[elementId];
      if (currentNumberOfPresentTuples != numeric_limits<int>::min())
	{
	  ++currentNumberOfPresentTuples;
	}
    }
}

long long SparseCrispTube::getDefaultMembership()
{
  return defaultMembership;
}

void SparseCrispTube::setDefaultMembership(const int defaultMembershipParam)
{
  defaultMembership = defaultMembershipParam;
}

void SparseCrispTube::setDefaultMembershipAndSizeLimit(const int defaultMembershipParam, const unsigned int sizeLimitParam)
{
  defaultMembership = defaultMembershipParam;
  sizeLimit = sizeLimitParam;
}
