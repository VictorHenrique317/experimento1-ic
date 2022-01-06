// Copyright 2018,2019 Loïc Cerf (lcerf@dcc.ufmg.br)

// This file is part of paf.

// paf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

// paf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

// You should have received a copy of the GNU General Public License along with paf.  If not, see <https://www.gnu.org/licenses/>.

#include "DenseFuzzyTube.h"

unsigned int DenseFuzzyTube::size;

DenseFuzzyTube::DenseFuzzyTube(vector<float>::const_iterator& membershipIt, const int unit): tube()
{
  tube.reserve(size);
  for (const vector<float>::const_iterator tubeEnd = membershipIt + size; membershipIt != tubeEnd; ++membershipIt)
    {
      tube.push_back(unit * *membershipIt);
    }
}

DenseFuzzyTube::DenseFuzzyTube(const vector<pair<unsigned int, int>>& sparseTube, const int defaultMembership): tube(size, defaultMembership)
{
  for (const pair<unsigned int, int>& entry : sparseTube)
    {
      tube[entry.first] = entry.second;
    }
}

void DenseFuzzyTube::setTuple(const vector<unsigned int>::const_iterator idIt, const int membership)
{
  tube[*idIt] = membership;
}

void DenseFuzzyTube::sumOnPattern(const vector<vector<unsigned int>>::const_iterator dimensionIt, int& sum) const
{
  for (const unsigned int id : *dimensionIt)
    {
      sum += tube[id];
    }
}

void DenseFuzzyTube::setSize(const unsigned int sizeParam)
{
  size = sizeParam;
}

void DenseFuzzyTube::sumsOnExtensions(const vector<vector<unsigned int>>::const_iterator dimensionIt, const vector<vector<int>>::iterator sumsIt) const
{
  vector<int>::const_iterator tubeIt = tube.begin();
  for (int& sum : *sumsIt)
    {
      if (sum != numeric_limits<int>::min())
	{
	  sum += *tubeIt;
	}
      ++tubeIt;
    }
}
