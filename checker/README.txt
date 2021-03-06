#!/usr/bin/env python
########################################################################
#
# Project: Metalink Checker
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2007-2011, Neil McNab
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
# Filename: $URL: https://metalinks.svn.sourceforge.net/svnroot/metalinks/checker/metalink.py $
# Last Updated: $Date: 2008-03-24 00:31:39 -0700 (Mon, 24 Mar 2008) $
# Version: $Rev: 130 $
# Author(s): Neil McNab
#
# Description:
#   Metalink Checker is a command line application that checks general 
# validity (valid XML) or downloads (executes) metalink files. It downloads 
# the files, checks their SHA1 or MD5 verification and verifies that the 
# files are working.
#
#   Command line application and Python library that checks or downloads
# metalink files.  Requires Python 2.5 or newer.
#
# Instructions:
#   1. You need to have Python installed.
#   2. To check PGP signatures you need to install gpg (http://www.gnupg.org) or gpg4win (http://www.gpg4win.org/)
#   3. Run on the command line using: python metalink.py
#
# Usage: metalinkc.py [-c|-d|-j|--convert|--rconvert] [options] arg1 arg2 ...
#
# Options:
#   --version             show program's version number and exit
#   -h, --help            show this help message and exit
#   -d, --download        Actually download the file(s) in the metalink
#   -c, --check           Check the metalink file URLs
#   -t TIMEOUT, --timeout=TIMEOUT
#                         Set timeout in seconds to wait for response
#                         (default=10)
#   -o OS, --os=OS        Operating System preference
#   -s, --no-segmented    Do not use the segmented download method
#   -l LANG, --lang=LANG  Language preference (ISO-639/3166)
#   --country=LOC         Two letter country preference (ISO 3166-1 alpha-2)
#   -k DIR, --pgp-keys=DIR
#                         Directory with the PGP keys that you trust (default:
#                         working directory)
#  -p FILE, --pgp-store=FILE
#                         File with the PGP keys that you trust (default:
#                         ~/.gnupg/pubring.gpg)
#   -g GPG, --gpg-binary=GPG
#                         (optional) Location of gpg binary path if not in the
#                         default search path
#   -j, --convert-jigdo   Convert Jigdo format file to Metalink
#   --port=PORT           Streaming server port to use (default: No streaming
#                         server)
#   --html=HTML           Extract links from HTML webpage
#   --convert             Conversion from 3 to 4 (IETF RFC)
#   --rconvert            Reverses conversion from 4 (IETF RFC) to 3
#   --output=OUTFILE      Output conversion result to this file instead of
#                         screen
#   -r, --rss             RSS/Atom Feed Mode, implies -d
#   -w WRITEDIR           Directory to write output files to (default: current
#                         directory)
#
# Library Instructions:
#   - Use as expected.
#
# import metalink
#
# files = metalink.get("file.metalink", os.getcwd())
# results = metalink.check_metalink("file.metalink")
#
# CHANGELOG:
#
# Version 6.0
# -----------
# - Support for RFC 3230 - Instance Digests in HTTP
# - Support for RFC 6249 - Metalink/HTTP: Mirrors and Hashes
#
# Version 5.1
# -----------
# - Bugfixes for segmented downloads
# - Native Jigdo download support
# - Added download time
# - Now requires Python 2.5 or newer because Metalink RFC requires SHA-256
#
# Version 5.0
# -----------
# - Added support for Metalink v4 (IETF RFC)
# - Changed executable name from metalink to metalinkc
# - Removed unneeded -f options
# - Added conversion options
#
# Version 4.4
# -----------
# - Bugfix for when HTTP 302 redirect code is issued during download
#
# Version 4.3
# -----------
# - Added custom HTTP header support
# - Added option to parse an HTML file for .metalink files to check
# - Started Debian packaging
# - Added a beta feature for media streaming
# - Added a minimal GUI for checking
# - Various bugfixes
#
# Version 4.2
# -----------
# - PGP bugfix
# - Jigdo to Metalink convertor
# - Other bugfixes
#
# Version 4.1
# -----------
# - Start of transition of how command line options are used
# - XML parsing speed and memory improvements
# - Checking function is now multithreaded for speed improvements
# - Displays download bitrates
# - Grabs proxy info from environment variables and Windows registry
# - Fix for faulty file locking, this causes corrupted downloads
#
# Version 4.0
# -----------
# - Uses gzip compression when available on server (non-segmented downloads only)
# - Fixed memory leak when computing a checksum
# - Bugfixes for download resuming
#
# Version 3.8
# -----------
# - Will now download any file type and auto-detect metalink files
# - Added option to disable segmented downloads to command line
# - Added support for metalink "Accept" HTTP header
#
# Version 3.7.4
# -------------
# - Fixed default key import directory
#
# Version 3.7.3
# -------------
# - Fixes for use with UNIX/Linux
# - bugfixes in checker code
#
# Version 3.7.2
# -------------
# - Modified to remove the pyme dependency
#
# Version 3.7.1
# -------------
# - Removed missing imports
#
# Version 3.7
# -----------
# - Added first attempt at PGP signature checking
# - Minor bugfixes
#
# Version 3.6
# -----------
# - Support for resuming segmented downloads
# - Modified for better Python 2.4 support
#
# Version 3.5
# -----------
# - Code cleanup
# - FTP close connection speed improvement
# - Added documentation for how to use as a library
# - Sort by country pref first (if set), then pref value in metalink
# 
# Version 3.4
# -----------
# - segmented download FTP size support
# - support for user specified OS and language preferences
# - finished FTP proxy support
#
# Version 3.3
# -----------
# - Bugfix for when type attr not present
# - Support for FTP segmented downloads
#
# Version 3.2
# -----------
# - If type="dynamic", client checks origin location
#
# Version 3.1
# -----------
# - Now handles all SHA hash types and MD5
# - Minor bug fixes
#
# Version 3.0
# -----------
# - Speed and bandwidth improvements for checking mode
# - Added checking of chunk checksums
# - If chunk checksums are present, downloads are resumed
# - Proxy support (experimental, HTTP should work, FTP and HTTPS not likely)
#
# Version 2.0.1
# -------------
# - Bugfix when doing size check on HTTP servers, more reliable now
#
# Version 2.0
# -----------
# - Support for segmented downloads! (HTTP urls only, falls back to old method if only FTP urls)
#
# Version 1.4
# -----------
# - Added support for checking the file size on FTP servers
#
# Version 1.3.1
# -------------
# - Made error when XML parse fails a little clearer.
#
# Version 1.3
# -----------
# - Fixed bug when no "size" attribute is present
#
# Version 1.2
# -----------
# - Added totals output
#
# Version 1.1
# -----------
# - Bugfixes for FTP handling, bad URL handling
# - rsync doesn't list as a URL Error
# - reduced timeout value
#
# Version 1.0
# -----------
# This is the initial release.
#
# TODO
# - resume download support for non-segmented downloads
# - download priority based on speed
# - use maxconnections
# - dump FTP data chunks directly to file instead of holding in memory
########################################################################
