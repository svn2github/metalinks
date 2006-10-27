/*
	This file is part of the metalink program
	Copyright (C) 2005  A. Bram Neijt <bneijt@gmail.com>

	This program is free software; you can redistribute it and/or
	modify it under the terms of the GNU General Public License
	as published by the Free Software Foundation; either version 2
	of the License, or (at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

*/

#ifndef _Mirror_HH_INCLUDED_
#define	_Mirror_HH_INCLUDED_

#include <string>

namespace bneijt{

///Internal representation of the mirror information
class Mirror
{
		std::string d_path;
		unsigned int d_preference;
		std::string d_location;
		std::string d_type;
		
	public:
		Mirror(std::string const &path,
				std::string const &preference = "",
				std::string const &location = "",
				std::string const &type = "");

		std::string asXMLWithFile(std::string const &file) const;
};
}
#endif

