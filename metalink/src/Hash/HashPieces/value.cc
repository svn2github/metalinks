/*
	This file is part of the metalink program
	Copyright (C) 2008  A. Bram Neijt <bneijt@gmail.com>

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/



#include "HashPieces.ih"
std::string const &HashPieces::value() const
{
	static std::string value;
	//assert(false);
	ostringstream ost;
	for(vector<Hash>::size_type i(0);
		i < d_pieces.size();
		++i)
	{
		if(i > 0)
			ost << ":";
		ost << d_pieces[i]->value();
	}
	value = ost.str();
	return value;
}
