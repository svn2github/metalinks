#!/usr/bin/env python
########################################################################
#
# Project: Metalink Checker
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2007-2012, Neil McNab
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
import proxy

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
    localelang = locale.getdefaultlocale()[0]
    if localelang == None:
        localelang = "LC_ALL"
    t = gettext.translation(base, localedir, [localelang], None, 'en')
    return t.ugettext

_ = translate()

def run():
    '''
    Start a console version of this application.
    '''
    # Command line parser options.
    usage = "usage: %prog [-c|-d|-j|--convert|--rconvert] [options] arg1 arg2 ..."
    parser = optparse.OptionParser(version=checker.ABOUT, usage=usage)
    parser.add_option("--download", "-d", action="store_true", dest="download", help=_("Actually download the file(s) in the metalink"))
    parser.add_option("--check", "-c", action="store_true", dest="check", help=_("Check the metalink file URLs"))
    #parser.add_option("--file", "-f", dest="filevar", metavar="FILE", help=_("Metalink file to check or file to download"))
    parser.add_option("--timeout", "-t", dest="timeout", metavar="TIMEOUT", help=_("Set timeout in seconds to wait for response (default=10)"))
    parser.add_option("--os", "-o", dest="os", metavar="OS", help=_("Operating System preference"))
    parser.add_option("--no-segmented", "-s", action="store_true", dest="nosegmented", help=_("Do not use the segmented download method"))
    parser.add_option("--lang", "-l", dest="language", metavar="LANG", help=_("Language preference (ISO-639/3166)"))
    parser.add_option("--country", dest="country", metavar="LOC", help=_("Two letter country preference (ISO 3166-1 alpha-2)"))
    parser.add_option("--pgp-keys", "-k", dest="pgpdir", metavar="DIR", help=_("Directory with the PGP keys that you trust (default: working directory)"))
    parser.add_option("--pgp-store", "-p", dest="pgpstore", metavar="FILE", help=_("File with the PGP keys that you trust (default: ~/.gnupg/pubring.gpg)"))
    parser.add_option("--gpg-binary", "-g", dest="gpg", help=_("(optional) Location of gpg binary path if not in the default search path"))
    parser.add_option("--convert-jigdo", "-j", action="store_true", dest="jigdo", help=_("Convert Jigdo format file to Metalink"))
    parser.add_option("--port", dest="port", help=_("Streaming server port to use (default: No streaming server)"))
    parser.add_option("--html", dest="html", help=_("Extract links from HTML webpage"))
    parser.add_option("--convert", dest="convert", action="store_true", help="Conversion from 3 to 4 (IETF RFC)")
    parser.add_option("--rconvert", dest="rev", action="store_true", help="Reverses conversion from 4 (IETF RFC) to 3")
    parser.add_option("--output", dest="output", metavar="OUTFILE", help=_("Output conversion result to this file instead of screen"))
    parser.add_option("--rss", "-r", action="store_true", dest="rss", help=_("RSS/Atom Feed Mode, implies -d"))
    parser.add_option("--testable", action="store_true", dest="only_testable", help=_("Limit tests to only the URL types we can test (HTTP/HTTPS/FTP)"))
    parser.add_option("-w", dest="writedir", default=os.getcwd(), help=_("Directory to write output files to (default: current directory)"))
    (options, args) = parser.parse_args()
    
    #if options.filevar != None:
    #   args.append(options.filevar)

    if len(args) == 0:
        parser.print_help()
        return

    socket.setdefaulttimeout(10)
    proxy.set_proxies()
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
    if options.port != None:
        download.PORT = int(options.port)
    if options.gpg != None:
        GPG.DEFAULT_PATH.insert(0, options.gpg)
        
    if options.timeout != None:
        socket.setdefaulttimeout(int(options.timeout))

    if options.country != None and len(options.country) != 2:
        print _("Invalid country length, must be 2 letter code")
        return

    if options.jigdo:
        print download.convert_jigdo(args[0])
        return
        
    if options.convert:
        text = download.parse_metalink(args[0], ver=4).generate()
        if options.output:
            handle = open(options.output, "w")
            handle.write(text)
            handle.close()
        else:
            print text
        return
        
    if options.rev:
        text = download.parse_metalink(args[0], ver=3).generate()
        if options.output:
            handle = open(options.output, "w")
            handle.write(text)
            handle.close()
        else:
            print text
        return

    if options.html:
        handle = download.urlopen(options.html)
        text = handle.read()
        handle.close()

        page = checker.Webpage()
        page.set_url(options.html)
        page.feed(text)
        
        for item in page.urls:
            if item.endswith(".metalink"):
                print "=" * 79
                print item
                mcheck = checker.Checker()
                mcheck.check_metalink(item)
                results = mcheck.get_results()
                print_totals(results)
        return

    if options.check:
        failure = False
        for item in args:
            print "=" * 79
            print item
            mcheck = checker.Checker(options.only_testable)
            mcheck.check_metalink(item)
            results = mcheck.get_results()
            result = print_totals(results)
            failure |= result
        sys.exit(int(failure))
            
    if options.download:
        for item in args:
            progress = ProgressBar()
            result = download.get(item, options.writedir, handlers={"status": progress.download_update, "bitrate": progress.set_bitrate, "time": progress.set_time}, segmented = not options.nosegmented)
            progress.download_end()
            if not result:
                sys.exit(-1)
                
    if options.rss:
        for feed in args:
            progress = ProgressBar()
            result = download.download_rss(feed, options.writedir, handlers={"status": progress.download_update, "bitrate": progress.set_bitrate, "time": progress.set_time}, segmented = not options.nosegmented)
            progress.download_end()
            if not result:
                sys.exit(-1)
                        
    sys.exit(0)
    
def print_totals(results):
    complete_failure = False
    for key in results.keys():
        print "=" * 79
        print _("Summary for file") + ":", key

        status_count = 0
        size_count = 0
        checksum_count = 0
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

            checksum = results[key][subkey][2]
            checksum_bool = False
            if checksum == "FAIL":
                checksum_bool = True
                
            redir = results[key][subkey][2]

            print "-" * 79
            print _("Checked") + ": %s" % subkey
            if redir != None:
                print _("Redirected") + ": %s" % redir
            print _("Response Code") + ": %s\t" % status + _("Size Check") + ": %s\t" % size + _("Checksum") + ": %s" % checksum
                
            if size_bool:
                size_count += 1
            if checksum_bool:
                checksum_count += 1
            if status_bool:
                status_count += 1
            if size_bool or status_bool or checksum_bool:
                error_count += 1

        print _("Download errors") + ": %s/%s" % (status_count, total)
        print _("Size check failures") + ": %s/%s" % (size_count, total)
        print _("Checksum failures") + ": %s/%s" % (checksum_count, total)
        print _("Overall failures") + ": %s/%s" % (error_count, total)
        if error_count == total:
            complete_failure = True
    return complete_failure

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
    def __init__(self, length = 79):
        self.length = length
        self.bitrate = None
        self.time = None
        self.show_bitrate = True
        self.show_time = True
        self.show_bytes = True
        self.show_percent = True
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


        percenttxt = ""
        if self.show_percent:
            percenttxt = " %.0f%%" % percent

        bytes = ""
        if self.show_bytes:
            bytes = " %.2f/%.2f MB" % (current_bytes, total_bytes)
            
        bitinfo = ""
        if self.bitrate != None and self.show_bitrate:
            if self.bitrate > 1000:
                bitinfo = " %.2f Mbps" % (float(self.bitrate) / float(1000))
            else:
                bitinfo = " %.0f kbps" % self.bitrate

        timeinfo = ""
        if self.time != None and self.time != "" and self.show_time:
            timeinfo += " " + self.time
                
        length = self.length - 2 - len(percenttxt) - len(bytes) - len(bitinfo) - len(timeinfo)

        size = int(percent * length / 100)            
        bar = ("#" * size) + ("-" * (length - size))
        output = "[%s]" % bar
        output += percenttxt + bytes + bitinfo + timeinfo
        
        self.line_reset()
        sys.stdout.write(output)

    def set_bitrate(self, bitrate):
        self.bitrate = bitrate
        
    def set_time(self, time):
        self.time = time

    def update(self, count, total):
        if count > total:
            count = total
            
        try:
            percent = 100 * float(count) / total
        except ZeroDivisionError:
            percent = 0

        if total < 0:
            return

        percenttxt = ""
        if self.show_percent:
            percenttxt = " %.0f%%" % percent

        length = self.length - 2 - len(percenttxt)

        size = int(percent * length / 100)
        bar = ("#" * size) + ("-" * (length - size))
        output = "[%s]" % bar
        output += percenttxt
        
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
