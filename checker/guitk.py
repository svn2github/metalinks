#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Project: Metalink Checker
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2007-2010, Neil McNab
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
# Filename: $URL: https://metalinks.svn.sourceforge.net/svnroot/metalinks/checker/checker.py $
# Last Updated: $Date: 2010-04-21 22:05:23 -0700 (Wed, 21 Apr 2010) $
# Version: $Rev: 653 $
# Author(s): Neil McNab
#
# Description:
#   GUI for checking metalink files.
#
########################################################################

import Tkinter
import tkFileDialog
import tkMessageBox
import os
import gettext
import locale
import time
import webbrowser
import threading
import sys

import checker

def translate():
    '''
    Setup translation path
    '''
    global PATH
    if __name__=="__main__":
        try:
            base = os.path.basename(__file__)[:-3]
            PATH = os.path.dirname(__file__)
            localedir = os.path.join(PATH, "locale")
        except NameError:
            base = os.path.basename(sys.executable)[:-4]
            PATH = os.path.dirname(sys.executable)
            localedir = os.path.join(PATH, "locale")
    else:
        temp = __name__.split(".")
        base = temp[-1]
        PATH = "/".join(["%s" % k for k in temp[:-1]])
        localedir = os.path.join(PATH, "locale")

    #print base, localedir
    t = gettext.translation(base, localedir, [locale.getdefaultlocale()[0]], None, 'en')
    return t.ugettext

_ = translate()

class Table(Tkinter.Frame):
    def __init__(self, *args):
        Tkinter.Frame.__init__(self, *args)
        Tkinter.Frame.grid_rowconfigure(self, 0, weight=1)
        Tkinter.Frame.grid_columnconfigure(self, 0, weight=1)
        
        self.vscrollbar = AutoScrollbar(self, orient=Tkinter.VERTICAL)
        self.vscrollbar.grid(row=0, column=1, sticky="NS")

        self.hscrollbar = AutoScrollbar(self, orient=Tkinter.HORIZONTAL)
        self.hscrollbar.grid(row=1, column=0, sticky="WE")
        
        self.canvas = Tkinter.Canvas(self, yscrollcommand=self.vscrollbar.set, xscrollcommand=self.hscrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="NEWS")

        self.vscrollbar.config(command=self.canvas.yview)
        self.hscrollbar.config(command=self.canvas.xview)
        
        self.container = Tkinter.Frame(self.canvas)
        self.container.grid(sticky="NEWS")

        self.update(0)

        self.canvas.create_window(0,0,window=self.container, anchor=Tkinter.NW)
        
        self.subelements = []

    def update(self, height=1000, width=1000):
        self.canvas["scrollregion"] = (0, 0, width, height)

    def data(self, datalist):
        self.clear()
        
        row = 1
        for datarow in datalist:
            column = 1
            for datacolumn in datarow:
                color = ""
                if column in (3, 4, 5) and row != 1:
                    if datacolumn == "OK":
                        color = "green"
                    elif datacolumn[0] == "3":
                        color = "yellow"
                    elif datacolumn[0] == "?":
                        pass
                    else:
                        color = "red"                     
                if color != "":
                    label = Tkinter.Label(self.container, text=datacolumn, bg=color)
                else:
                    label = Tkinter.Label(self.container, text=datacolumn)
                label.config(anchor="w")
                label.grid(column=column, row=row, sticky="NEWS")
                self.subelements.append(label)
                column += 1
            row += 1

        self.update(len(self.subelements) * 5)

    def clear(self):
        self.update(0)

        #self.container = Tkinter.Frame(self.canvas)
        #self.container.grid(sticky="NEWS")
        
        for element in self.subelements:
            #element.grid_remove()
            element.config(text="")
            #del(element)
        self.subelements = []

class AutoScrollbar(Tkinter.Scrollbar):
       # a scrollbar that hides itself if it's not needed.  only
       # works if you use the grid geometry manager.
       def set(self, lo, hi):
           if float(lo) <= 0.0 and float(hi) >= 1.0:
               # grid_remove is currently missing from Tkinter!
               self.tk.call("grid", "remove", self)
           else:
               self.grid()
           Tkinter.Scrollbar.set(self, lo, hi)
       def pack(self, **kw):
           raise Tkinter.TclError, "cannot use pack with this widget"
       def place(self, **kw):
           raise Tkinter.TclError, "cannot use place with this widget"

        
class Application:
    def __init__(self, master):
        self.master = master
        self.checker = checker.Checker()
        self.createWidgets()

        self.quit = self.exit
        self.destroy = self.exit

    def createWidgets(self):
        # create menu
        menu = Tkinter.Menu(self.master)
        self.master.config(menu=menu)
        self.master.grid_columnconfigure(0,weight=1)
        self.master.grid_rowconfigure(0,weight=1)

        Filemenu = Tkinter.Menu(menu)
        menu.add_cascade(label=_("File"), menu=Filemenu, underline=0)
        Filemenu.add_command(label=_("Open") + "...", underline=0, command=self.open)
        Filemenu.add_separator()
        Filemenu.add_command(label=_("Exit"), underline=1, command=self.exit)

        Helpmenu = Tkinter.Menu(menu)
        menu.add_cascade(label=_("Help"), menu=Helpmenu, underline=0)
        Helpmenu.add_command(label=_("About") + "...", underline=0, command=self.about)
        Helpmenu.add_command(label=_("Website") + "...", underline=0, command=self.website)

        # main frame
        self.main_frame = Tkinter.Frame(self.master)
        self.main_frame.grid(sticky="NEWS")
        self.main_frame.grid_rowconfigure(1,weight=1)
        self.main_frame.grid_columnconfigure(0,weight=1)

        longtext = 100

        row_index = 0

        self.control_frame = Tkinter.Frame(self.main_frame)
        self.control_frame.grid(row=row_index, column=0, sticky="NW")
        
        Tkinter.Label(self.control_frame, text=_("File") + ":").grid(row=row_index)
        self.filename_txt = Tkinter.Entry(self.control_frame, width=longtext)
        self.filename_txt.grid(row=row_index, column=1)
        self.filename_txt.bind("<Return>", ThreadCallback(self.do_check))

        
        Tkinter.Button(self.control_frame, text=_("Browse") + "...", command=self.open).grid(row=row_index, column=2)
        self.check_button = Tkinter.Button(self.control_frame, text=_("Check"), command=ThreadCallback(self.do_check))
        self.check_button.grid(row=row_index, column=3)
        
        self.cancel_button = Tkinter.Button(self.control_frame, text=_("Cancel"), command=ThreadCallback(self.do_cancel))
        self.cancel_button.grid(row=row_index, column=4)
        self.cancel_button.configure(state="disabled")
 
        #tooltip = _("File to open and check.")
        #ToolTip(self.filename_txt, text=tooltip)
        row_index += 1

        self.tableframe = Table(self.main_frame)
        self.tableframe.grid(column=0, row=row_index, columnspan=5, sticky="NEWS")
        
    def do_check(self):
        #self.tableframe.clear()
        self.update()
        self.check_button.configure(state="disabled")
        self.cancel_button.configure(state="active")

        # should start new thread here
        if self.filename_txt.get() != "":
            #self.checker.check_metalink(self.filename_txt.get())
            mythread = threading.Thread(target=self.checker.check_metalink, args = [self.filename_txt.get()])
            mythread.start()
        # wait and do updates here
        value = self.checker.isAlive()
        while value:
            #self.update()
            time.sleep(1)
            value = self.checker.isAlive()
            #print value
            
        self.do_cancel()

    def do_cancel(self):
#        print "cancel"
        self.cancel_button.configure(state="disabled")

        mythread = threading.Thread(target=self.checker.stop)
        mythread.start()
        while mythread.isAlive():
            time.sleep(1)
            
        self.update()
        mythread = threading.Thread(target=self.checker.clear_results)
        mythread.start()
        while mythread.isAlive():
            time.sleep(1)
        self.check_button.configure(state="active")

    def update(self):
#        print "update"

        result = self.format_table(self.checker.get_results())
        self.tableframe.data(result)

            #count = active

    def format_table(self, datadict):
        datalist = [[_("Filename"), _("URL"), _("Response Code"), _("Size Check"), _("Checksum"), _("Redirect")]]
        for filename in datadict.keys():
            datalist.append([filename])
            urls = datadict[filename].keys()
            for url in urls:
                add = ["", url]
                #print filename, url, datadict[filename][url]
                #if datadict[filename][url] is not None:
                for item in datadict[filename][url]:
                    add.append(item)
                datalist.append(add)
        return datalist

    def open(self):
        init = ""
        if self.filename_txt.get() != "":
            init = os.path.dirname(self.filename_txt.get())
        result = tkFileDialog.askopenfilename(initialdir = init, title=_("Please select a Metalink file to open") + "...", filetypes=[('Metalink File','*.metalink')])
        if result != "":
            # do file path set here
            self.filename_txt.delete(0, Tkinter.END)
            self.filename_txt.insert(0, result)
            
    def about(self):
        tkMessageBox.showinfo(_("About") + " " + checker.NAME, checker.ABOUT)

    def website(self):
        webbrowser.open_new_tab(checker.WEBSITE)

    def exit(self):
        mythread = threading.Thread(target = self.do_cancel)
        mythread.start()
        self.master.quit()
        
def run():
    root = Tkinter.Tk()
    root.title(checker.NAME)
    root.geometry("850x500")

    app = Application(master=root)

    root.protocol("WM_DELETE_WINDOW", app.exit)
    root.mainloop()

##def call_thread(self, *args):
##    mythread = threading.Thread(target = SimpleCallback(*args))
##    mythread.setDaemon(True)
##    mythread.start()

##class SimpleCallback:
##	"""Create a callback shim. Based on code by Scott David Daniels
##	(which also handles keyword arguments).
##	"""
##	def __init__(self, callback, *firstArgs):
##		self.__callback = callback
##		self.__firstArgs = firstArgs
##	
##	def __call__(self, *args):
##		return self.__callback (*(self.__firstArgs + args))
	    
class ThreadCallback:
	"""Create a callback shim. Based on code by Scott David Daniels
	(which also handles keyword arguments).
	"""
	def __init__(self, callback, firstArgs=[]):
		self.__callback = callback
		self.__firstArgs = firstArgs

	def isAlive(self):
                return self.__thread.isAlive() 
	
	def __call__(self, *args):
                __thread = threading.Thread(target=self.__callback, args = self.__firstArgs)
                __thread.start()
		return __thread
	    

if __name__=="__main__":
    run()
