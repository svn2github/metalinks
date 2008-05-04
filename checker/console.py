#!/usr/bin/env python
########################################################################
#
# Project: Metalink Checker
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2007-2008, Neil McNab
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
# Version: $Rev$
# Author(s): Neil McNab
#
# Description:
#   Command line application that checks or downloads metalink files.  Requires
# Python 2.5 or newer.
#
# Instructions:
#   1. You need to have Python installed.
#   2. Run on the command line using: python checker.py
#
########################################################################

import optparse
import socket
import sys
import os

import download
import checker
import GPG

# DO NOT CHANGE
VERSION="Metalink Checker Version 3.8"

import os.path
import locale
import gettext

def translate():
    '''
    Setup translation path
    '''
    if __name__=="__main__":
        try:
            base = os.path.basename(__file__)[:-3]
            localedir = os.path.join(os.path.dirname(__file__), "locale")
        except NameError:
            base = os.path.basename(sys.executable)[:-4]
            localedir = os.path.join(os.path.dirname(sys.executable), "locale")
    else:
        temp = __name__.split(".")
        base = temp[-1]
        localedir = os.path.join("/".join(["%s" % k for k in temp[:-1]]), "locale")

    #print base, localedir
    t = gettext.translation(base, localedir, [locale.getdefaultlocale()[0]], None, 'en')
    return t.lgettext

_ = translate()

def run():
    '''
    Start a console version of this application.
    '''
    # Command line parser options.
    parser = optparse.OptionParser(version=VERSION)
    parser.add_option("--download", "-d", action="store_true", dest="download", help=_("Actually download the file(s) in the metalink"))
    parser.add_option("--file", "-f", dest="filevar", metavar="FILE", help=_("Metalink file to check"))
    parser.add_option("--timeout", "-t", dest="timeout", metavar="TIMEOUT", help=_("Set timeout in seconds to wait for response (default=10)"))
    parser.add_option("--os", "-o", dest="os", metavar="OS", help=_("Operating System preference"))
    parser.add_option("--no-segmented", "-s", action="store_true", dest="nosegmented", help=_("Do not use the segmented download method"))
    parser.add_option("--lang", "-l", dest="language", metavar="LANG", help=_("Language preference (ISO-639/3166)"))
    parser.add_option("--country", "-c", dest="country", metavar="LOC", help=_("Two letter country preference (ISO 3166-1 alpha-2)"))
    parser.add_option("--pgp-keys", "-k", dest="pgpdir", metavar="DIR", help=_("Directory with the PGP keys that you trust (default: working directory)"))
    parser.add_option("--pgp-store", "-p", dest="pgpstore", metavar="FILE", help=_("File with the PGP keys that you trust (default: ~/.gnupg/pubring.gpg)"))
    parser.add_option("--gpg-binary", "-g", dest="gpg", help=_("(optional) Location of gpg binary path if not in the default search path"))
    (options, args) = parser.parse_args()

    if options.filevar == None:
        parser.print_help()
        return

    socket.setdefaulttimeout(10)
    download.set_proxies()
    if options.os != None:
        download.OS = options.os
    if options.language != None:
        download.LANG = [].extend(options.language.lower().split(","))
    if options.country != None:
        download.COUNTRY = options.country
    if options.pgpdir != None:
        download.PGP_KEY_DIR = options.pgpdir
    if options.pgpstore != None:
        download.PGP_KEY_STORE = options.pgpstore
    if options.gpg != None:
        GPG.DEFAULT_PATH.insert(0, options.gpg)
        
    if options.timeout != None:
        socket.setdefaulttimeout(int(options.timeout))

    if options.country != None and len(options.country) != 2:
        print _("Invalid country length, must be 2 letter code")
        return
    
    if options.download:
        download.SEGMENTED = True
        if options.nosegmented:
            download.SEGMENTED = False

        progress = ProgressBar(55)
        result = download.get(options.filevar, os.getcwd(), handler=progress.download_update)
        #result = download.download_metalink(options.filevar, os.getcwd(), handler=progress.download_update)
        progress.download_end()
        if not result:
            sys.exit(-1)
    else:
        results = checker.check_metalink(options.filevar)
        print_totals(results)

def print_totals(results):
    for key in results.keys():
        print "=" * 79
        print _("Summary for") + ":", key

        status_count = 0
        size_count = 0
        error_count = 0
        total = len(results[key])
        for subkey in results[key].keys():
            status = results[key][subkey][0]
            status_bool = False
            if status != "OK" and status != "?":
                status_bool = True

            size = results[key][subkey][1]
            size_bool = False
            if size == "FAIL":
                size_bool = True

            if size_bool:
                size_count += 1
            if status_bool:
                status_count += 1
            if size_bool or status_bool:
                error_count += 1

        print _("Download errors") + ": %s/%s" % (status_count, total)
        print _("Size check failures") + ": %s/%s" % (size_count, total)
        print _("Overall failures") + ": %s/%s" % (error_count, total)

##def print_summary(results):
##    for key in results.keys():
##        print "=" * 79
##        print "Summary for:", key
##        print "-" * 79
##        print "Response Code\tSize Check\tURL"
##        print "-" * 79
##        for subkey in results[key].keys():
##            print "%s\t\t%s\t\t%s" % (results[key][subkey][0], results[key][subkey][1], subkey)

##def confirm_prompt(noprompt):
##    invalue = "invalid"
##
##    if noprompt:
##        return True
##    
##    while (invalue != "" and invalue[0] != "n" and invalue[0] != "N" and invalue[0] != "Y" and invalue[0] != "y"):
##        invalue = raw_input("Do you want to continue? [Y/n] ")
##
##    try:
##        if invalue[0] == "n" or invalue[0] == "N":
##            return False
##    except IndexError:
##        pass
##    
##    return True


class ProgressBar:
    def __init__(self, length = 68):
        self.length = length
        #print ""
        #self.update(0, 0)
        self.total_size = 0

    def download_update(self, block_count, block_size, total_size):
        self.total_size = total_size
        
        current_bytes = float(block_count * block_size) / 1024 / 1024
        total_bytes = float(total_size) / 1024 / 1024
            
        try:
            percent = 100 * current_bytes / total_bytes
        except ZeroDivisionError:
            percent = 0
            
        if percent > 100:
            percent = 100

        if total_bytes < 0:
            return

        size = int(percent * self.length / 100)
        bar = ("#" * size) + ("-" * (self.length - size))
        output = "[%s] %.0f%% %.2f/%.2f MB" % (bar, percent, current_bytes, total_bytes)
        
        self.line_reset()
        sys.stdout.write(output)

    def update(self, count, total):
        if count > total:
            count = total
            
        try:
            percent = 100 * float(count) / total
        except ZeroDivisionError:
            percent = 0

        if total < 0:
            return

        size = int(percent * self.length / 100)
        bar = ("#" * size) + ("-" * (self.length - size))
        output = "[%s] %.0f%%" % (bar, percent)
        
        self.line_reset()
        sys.stdout.write(output)

    def line_reset(self):
        sys.stdout.write("\b" * 80)
        if os.name != 'nt':
            sys.stdout.write("\n")
        
    def end(self):
        self.update(1, 1)
        print ""

    def download_end(self):
        self.download_update(1, self.total_size, self.total_size)
        print ""

if __name__ == "__main__":
    run()