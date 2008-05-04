from distutils.core import setup
import sys
import os.path
import shutil
import glob

APP_NAME = 'Metalink Checker'
VERSION = '0.7.4'
LICENSE = 'GPL'
DESC = 'A metalink checker and download client.'
AUTHOR_NAME = 'Neil McNab'
EMAIL = 'webmaster@nabber.org'
URL = 'http://www.nabber.org/projects/'

#main is first
modules = ['console', 'xmlutils', 'GPG', 'download', 'checker']
outputfile = "metalink.py"

readhandle = open("header.txt")
header = readhandle.read()
readhandle.close()

def merge(header, modules, outputfile):
    modules.reverse()
    modulelist = []
    imports = ""
    redef = {}

    for module in modules:
        imports += readfile(module, True, modules)

        exec("import " + module)
        moduleobj = eval(module)
        listing = dir(moduleobj)
        for stritem in listing:
            item = getattr(moduleobj, stritem)

            if not stritem.startswith("__") and type(item) != type(sys):
                try:
                    redef[module] += module + "." + stritem + " = " + stritem + "\n"
                except KeyError:
                    redef[module] = module + "." + stritem + " = " + stritem + "\n"

    writehandle = open(outputfile, "w")
    writehandle.write(header)
    
    writehandle.write(imports + "class Dummy:\n    pass\n")
    
    for modulename in modules:
        filestring = readfile(modulename)
        writehandle.write(filestring)
        writehandle.write(modulename + " = Dummy()\n" + redef[modulename])
        
    writehandle.close()
    return

def readfile(modulename, imports=False, ignore=[]):
    filestring = ""
    filehandle = open(modulename + ".py")
    line = filehandle.readline()
    while line:
        if imports == line.strip().startswith("import ") and line.strip()[7:] not in ignore:
            filestring += line
        line = filehandle.readline()
    filehandle.close()
    return filestring

def clean():
    ignore = []
    
    filelist = []
    filelist.extend(glob.glob("*metalink*.txt"))
    filelist.extend(rec_search(".exe"))
    filelist.extend(rec_search(".zip"))
    filelist.extend(rec_search(".pyc"))
    filelist.extend(rec_search(".pyo"))
    filelist.extend(rec_search(".mo"))
    filelist.extend(rec_search(".pot"))
    
    try:
        shutil.rmtree("build")
    except WindowsError: pass
    try:
        shutil.rmtree("dist")
    except WindowsError: pass
    try:
        shutil.rmtree("buildMetalink")
    except WindowsError: pass

    try:
        shutil.rmtree("tests_temp")
    except WindowsError: pass
    
    for filename in filelist:
        if filename not in ignore:
            try:
                os.remove(filename)
            except WindowsError: pass

def localegen():
    localedir = "locale"
    ignore = ("setup.py", "test.py")

    files = rec_search(".py")
    for pyfile in files:
        if os.path.basename(pyfile) not in ignore:
            potdir = os.path.join(os.path.dirname(pyfile), localedir, os.path.basename(pyfile))[:-3]
            print potdir
            try:
                os.makedirs(os.path.join(os.path.dirname(pyfile), localedir))
            except: pass

            command = os.path.join(sys.prefix, "Tools/i18n/pygettext.py") + " --no-location -d \"%s\" \"%s\"" % (potdir, pyfile)
            print(command)
            result = os.system(command)
            if result != 0:
                raise AssertionError, "Generation of .pot file failed for %s." % pyfile


def localecompile():
    files = rec_search(".po")

    for pofile in files:
        command = os.path.join(sys.prefix, "Tools/i18n/msgfmt.py") + " \"%s\"" % pofile
        print(command)
        result = os.system(command)
        if result != 0:
            raise AssertionError, "Generation of .mo file failed for %s." % pofile
            
def rec_search(end, abspath = True):
    start = os.path.dirname(__file__)
    mylist = []
    for root, dirs, files in os.walk(start):
        for filename in files:
            if filename.endswith(end):
                if abspath:
                    mylist.append(os.path.join(root, filename))
                else:
                    mylist.append(os.path.join(root[len(start):], filename))
                    
    return mylist

if sys.argv[1] == 'merge':
    merge(header, modules, outputfile)

elif sys.argv[1] == 'translate':
    localegen()
    localecompile()

elif sys.argv[1] == 'clean':
    clean()

elif sys.argv[1] == 'py2exe':
    merge(header, modules, outputfile)
        
    import py2exe

    #localegen()
    #localecompile()
    
    setup(console = ["metalink.py"],
        zipfile = None,
      name = APP_NAME,
      version = VERSION,
      license = LICENSE,
      description = DESC,
      author = AUTHOR_NAME,
      author_email = EMAIL,
      url = URL
      )