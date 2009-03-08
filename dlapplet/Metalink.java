/*######################################################################
#
# Project: DLApplet
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2009, Neil McNab
# License: GNU General Public License Version 2
#   (http://www.gnu.org/copyleft/gpl.html)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# Filename: $URL$
# Last Updated: $Date$
# Author(s): Neil McNab
#
# Description:
#   Class to handle files according to the Metalink spec.
######################################################################*/

import org.xml.sax.*;
import org.xml.sax.helpers.*;
import java.util.jar.Attributes;
import java.util.ArrayList;

public class Metalink extends DefaultHandler {
  ArrayList <MetalinkFile> files = new ArrayList <MetalinkFile> ();
  String dataString;
  
  //public Metalink() {
  //}
   
  public void startElement(String namespaceUri, String localName, String qualifiedName, Attributes attributes)
      throws SAXException {
	  System.out.println("in sax start");
    /*if (qualifiedName.equals("file")) {
	    files.add(new MetalinkFile(attributes));
	} else if (qualifiedName.equals("url")) {
    }*/
  }

  public void endElement(String namespaceUri, String localName, String qualifiedName)
      throws SAXException {
    if (qualifiedName.equals("file")) {
    } else if (qualifiedName.equals("url")) {
	    System.out.println("in sax end "+ qualifiedName);
      	//MetalinkFile fileobj = files.get(files.size() - 1);
		//fileobj.add_url(dataString);
    }
  }


  public void characters(char[] chars, int startIndex, int endIndex) {

      String dataString = new String(chars, startIndex, endIndex).trim();
  }
  
  public ArrayList <MetalinkFile> get_files() {
      return files;
  }
}