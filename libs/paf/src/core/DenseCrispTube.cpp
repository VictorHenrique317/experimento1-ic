// Copyright 2018,2019 Loïc Cerf (lcerf@dcc.ufmg.br)

// This file is part of paf.

// paf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

// paf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

// You should have received a copy of the GNU General Public License along with paf.  If not, see <https://www.gnu.org/licenses/>.

#include "DenseCrispTube.h"

unsigned int DenseCrispTube::size;

DenseCrispTube::DenseCrispTube(vector<float>::const_iterator& membershipIt): tube(size)
{
  for (unsigned int elementId = 0; elementId != size; ++elementId)
    {
      if (*membershipIt > 0)
	{
	  tube.set(elementId);
	}
      ++membershipIt;
    }
}

DenseCrispTube::DenseCrispTube(const vector<unsigned int>& sparseTube): tube(size)
{
  for (const unsigned int elementId : sparseTube)
    {
      tube.set(elementId);
    }
}

void DenseCrispTube::setTuple(const vector<unsigned int>::const_iterator idIt)
{
  tube.set(*idIt);
}

void DenseCrispTube::sumOnPattern(const vector<vector<unsigned int>>::const_iterator dimensionIt, int& nbOfPresentTuples) const
{
  for (const unsigned int id : *dimensionIt)
    {
      if (tube[id])
	{
	  ++nbOfPresentTuples;
	}
    }
}

void DenseCrispTube::setSize(const unsigned int sizeParam)
{
  size = sizeParam;
}

void DenseCrispTube::sumsOnExtensions(const vector<vector<unsigned int>>::const_iterator dimensionIt, const vector<vector<int>>::iterator numbersOfPresentTuplesIt) const
{
  for (dynamic_bitset<>::size_type elementId = tube.find_first(); elementId != dynamic_bitset<>::npos; elementId = tube.find_next(elementId))
    {
      int& currentNumberOfPresentTuples = (*numbersOfPresentTuplesIt)[elementId];
      if (currentNumberOfPresentTuples != numeric_limits<int>::min())
	{
	  ++currentNumberOfPresentTuples;
	}
    }
}
