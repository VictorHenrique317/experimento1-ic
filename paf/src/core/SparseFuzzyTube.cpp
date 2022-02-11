// Copyright 2018,2019 Loïc Cerf (lcerf@dcc.ufmg.br)

// This file is part of paf.

// paf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

// paf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

// You should have received a copy of the GNU General Public License along with paf.  If not, see <https://www.gnu.org/licenses/>.

#include "SparseFuzzyTube.h"

int SparseFuzzyTube::defaultMembership;
unsigned int SparseFuzzyTube::sizeLimit;

SparseFuzzyTube::SparseFuzzyTube(): tube()
{
}

bool SparseFuzzyTube::isFullSparseTube() const
{
  return tube.size() == sizeLimit;
}

void SparseFuzzyTube::setTuple(const vector<unsigned int>::const_iterator idIt, const int membership)
{
  tube.emplace_back(*idIt, membership);
}

DenseFuzzyTube* SparseFuzzyTube::getDenseRepresentation() const
{
  return new DenseFuzzyTube(tube, defaultMembership);
}

void SparseFuzzyTube::sortTubes()
{
  tube.shrink_to_fit();
  sort(tube.begin(), tube.end(), [](const pair<unsigned int, int>& entry1, const pair<unsigned int, int>& entry2) {return entry1.first < entry2.first;});
}

void SparseFuzzyTube::sumOnPattern(const vector<vector<unsigned int>>::const_iterator dimensionIt, int& sum) const
{
  unsigned int nbOfDefaultMemberships = 0;
  const vector<pair<unsigned int, int>>::const_iterator tubeEnd = tube.end();
  vector<pair<unsigned int, int>>::const_iterator tubeBegin = tube.begin();
  const vector<unsigned int>::const_iterator idEnd = dimensionIt->end();
  for (vector<unsigned int>::const_iterator idIt = dimensionIt->begin(); idIt != idEnd; ++idIt)
    {
      tubeBegin = lower_bound(tubeBegin, tubeEnd, *idIt, [](const pair<unsigned int, int>& entry, const unsigned int id) {return entry.first < id;});
      if (tubeBegin == tubeEnd)
	{
	  sum += (idEnd - idIt + nbOfDefaultMemberships) * defaultMembership;
	  return;
	}
      if (tubeBegin->first == *idIt)
	{
	  sum += tubeBegin->second;
	}
      else
	{
	  ++nbOfDefaultMemberships;
	}
    }
  sum += nbOfDefaultMemberships * defaultMembership;
}

void SparseFuzzyTube::sumsOnExtensions(const vector<vector<unsigned int>>::const_iterator dimensionIt, const vector<vector<int>>::iterator sumsIt) const
{
  unsigned int elementId = 0;
  vector<int>::iterator sumIt = sumsIt->begin();
  for (const pair<unsigned int, int>& entry : tube)
    {
      while (entry.first != elementId++)
	{
	  if (*sumIt != numeric_limits<int>::min())
	    {
	      *sumIt += defaultMembership;
	    }
	  ++sumIt;
	}
      if (*sumIt != numeric_limits<int>::min())
	{
	  *sumIt += entry.second;
	}
      ++sumIt;
    }
  for (const vector<int>::iterator sumEnd = sumsIt->end(); sumIt != sumEnd; ++sumIt)
    {
      if (*sumIt != numeric_limits<int>::min())
	{
	  *sumIt += defaultMembership;
	}
    }
}

void SparseFuzzyTube::setDefaultMembershipAndSizeLimit(const int defaultMembershipParam, const unsigned int sizeLimitParam)
{
  defaultMembership = defaultMembershipParam;
  sizeLimit = sizeLimitParam;
}
