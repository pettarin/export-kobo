#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__     = 'GPLv3'
__author__      = 'Alberto Pettarin (pettarin gmail.com)'
__copyright__   = '2012-2015 Alberto Pettarin (pettarin gmail.com)'
__version__     = 'v1.0.3'
__date__        = '2015-01-23'
__description__ = 'Extract highlights and annotations from KoboReader.sqlite'


### BEGIN changelog ###
#
# 1.0.3 2015-01-23 Added options -l and -b (suggested by Pierre-Arnaud Rabier)
# 1.0.2 2013-05-11 Better usage text
# 1.0.1 2013-04-30 Initial release
#
### END changelog ###

import getopt, os, sqlite3, sys 

ANNOTATION="annotation"
BOOKMARK="bookmark"
HIGHLIGHT="highlight"


### BEGIN read_command_line_parameters ###
# read_command_line_parameters(argv)
# read the command line parameters given in argv, and return a suitable dict()
def read_command_line_parameters(argv):

    try:
        optlist, free = getopt.getopt(argv[1:], 'chtb:f:o:', ['book=', 'file=', 'output=', 'csv', 'help', 'titles'])
    #Python2#    except getopt.GetoptError, err:
    #Python3#
    except getopt.GetoptError as err:
        print_error(str(err))

    return dict(optlist)
### END read_command_line_parameters ###


### BEGIN usage ###
# usage()
# print script usage
def usage():
    #Python2#    e = "python"
    #Python2#    s = sys.argv[0] 
    #Python3#
    e = "python3"
    #Python3#
    s = sys.argv[0]
    print_("")
    print_("$ %s %s [ARGUMENTS]" % (e, s))
    print_("")
    print_("Arguments:")
    print_(" -b, --book <title>  : output annotations only for book <title>")
    print_(" -c, --csv           : output CSV values, instead of human-readable strings")
    print_(" -f, --file <file>   : <file> is the path to KoboReader.sqlite")
    print_(" -h, --help          : print this usage message and exit")
    print_(" -t, --titles        : output a list of book titles with annotations")
    print_(" -o, --output <file> : write output to <file>")
    print_("")
    print_("Exit codes:")
    print_("")
    print_(" 0 = no error")
    print_(" 1 = invalid argument(s) error")
    print_(" 2 = file KoboReader.sqlite not found")
    print_(" 4 = provided file is not a valid KoboReader.sqlite db")
    print_(" 8 = output file cannot be written")
    print_("")
    print_("Examples:")
    print_("")
    print_(" 1. Print this usage message")
    print_("    $ %s %s -h" % (e, s))
    print_("")
    print_(" 2. Print annotations and highlit passages in human-readable form")
    print_("    $ %s %s -f KoboReader.sqlite" % (e, s))
    print_("")
    print_(" 3. As above, but output to file output.txt")
    print_("    $ %s %s -f KoboReader.sqlite -o output.txt " % (e, s))
    print_("")
    print_(" 4. As above, but output in CSV form")
    print_("    $ %s %s -c -f KoboReader.sqlite" % (e, s))
    print_("")
    print_(" 5. As above, but output to output.csv")
    print_("    $ %s %s -c -f KoboReader.sqlite -o output.csv" % (e, s))
    print_("")
    print_(" 6. Print the list of book titles with annotations or highlit passages")
    print_("    $ %s %s -t -f KoboReader.sqlite" % (e, s))
    print_("")
    print_(" 7. Print annotations and highlit passages for 'The Art of War'")
    print_("    $ %s %s -f KoboReader.sqlite -b 'The Art of War'" % (e, s))
    print_("")
    print_(" 8. As above, but output to output.csv")
    print_("    $ %s %s -c -f KoboReader.sqlite -b 'The Art of War' -o output.csv" % (e, s))
    print_("")
### END usage ###


### BEGIN print_error ###
# print_error(error, displayusage=True)
# print the given error, call usage, and exit
# optional displayusage to skip usage
def print_error(error, displayusage = True, exitcode = 1):
    sys.stderr.write("[ERROR] " + error + " Aborting.\n")
    if displayusage :
        usage()
    sys.exit(exitcode)
### END print_error ###


### BEGIN print_info ###
# print_info(info, quiet)
# print the given info string
def print_info(info, quiet):
    if (not quiet):
        print("[INFO] " + info)
### END print_info ###


### BEGIN print_ ###
# print_(info)
# print the given string
def print_(info):
    print(info)
### END print_ ###


### BEGIN escape ###
# escape(s)
# escape ASCII sequences
def escape(s):
    if ((s == None) or (len(s) < 1)):
        return ""

    repl = [
            ["\0", "\\0"],
            ["\a", "\\a"],
            ["\b", "\\b"],
            ["\t", " "],
            ["\n", "\\n"],
            ["\v", "\\v"],
            ["\f", "\\f"],
            ["\r", "\\r"]
            ]
    for r in repl:
        s = s.replace(r[0], r[1])
    return s
### END escape ###


### BEGIN print_titles ###
# print_titles(data)
# data = [ [f_type, booktitle, text, annotation, date_created, date_modified] ]
# print list of titles
def print_titles(data):
    acc = ""
    tit = []
    fil = dict()

    for d in data:
        [f_type, booktitle, text, annotation, date_created, date_modified] = d
        if (not booktitle in fil):
            tit.append(booktitle)
            fil[booktitle] = True
    
    tit = sorted(tit)
    for t in tit:
        acc += "'%s'\n" % (t)
    
    return acc.strip()
### END print_titles ###

### BEGIN print_hr ###
# print_hr(data)
# data = [ [f_type, booktitle, text, annotation, date_created, date_modified] ]
# print human-readable output
def print_hr(data):

    acc = ""
    
    for d in data:
        [f_type, booktitle, text, annotation, date_created, date_modified] = d

        if (f_type == ANNOTATION):
            acc += "Type: %s\n" % (f_type)
            acc += "Title: %s\n" % (booktitle)
            acc += "Reference text: %s\n" % (text)
            acc += "Annotation: %s\n" % (annotation)
            acc += "Date created: %s\n" % (date_created)
            acc += "Date modified: %s\n" % (date_modified)
            acc += "\n"

        if (f_type == HIGHLIGHT):
            acc += "Type: %s\n" % (f_type)
            acc += "Title: %s\n" % (booktitle)
            acc += "Reference text: %s\n" % (text)
            acc += "Date created: %s\n" % (date_created)
            acc += "\n"

    return acc.strip()
### END print_hr ###


### BEGIN print_csv ###
# print_csv(data)
# data = [ [f_type, booktitle, text, annotation, date_created, date_modified] ]
# print csv output
def print_csv(data):
    
    # add header
    data2 = [ ["Type", "Book Title", "Reference Text", "Annotation", "Date Created", "Date Modified"] ] + data
    
    acc = ""

    for d in data2:
        acc += "%s\t%s\t%s\t%s\t%s\t%s\n" % (tuple(d))

    return acc.strip()
### END print_csv ###

### BEGIN main ###
def main():
    # read command line parameters
    options = read_command_line_parameters(sys.argv)

    # if help required, print usage and exit
    if (('-h' in options) or ('--help' in options)):
        usage()
        sys.exit(0)

    # look for dbFile
    dbFile = None
    if ('-f' in options):
        dbFile = options['-f']
    if ('--file' in options):
        dbFile = options['--file']
    
    if (dbFile == None):
        print_error("You should specify the path to the KoboReader.sqlite file.", exitcode=1)
    if ('-f' in options) and ('--file' in options):
        print_error("You cannot specify both '%s' and '%s' parameters." % ('-f', '--file'), exitcode=1)
    if (not os.path.isfile(dbFile)):
        print_error("File %s not found." % (dbFile), exitcode=2)

    # look for -b or --book switch
    keepOnlyBookWithTitle = None
    if ('-b' in options):
        keepOnlyBookWithTitle =  options['-b']
    if ('--book' in options):
        keepOnlyBookWithTitle =  options['--book']

    # look for CSV switch
    outputCSV = False
    if ('-c' in options) or ('--csv' in options):
        outputCSV = True

    # look for outFile
    outFile = None
    if ('-o' in options):
        outFile = options['-o']
    if ('--output' in options):
        outFile = options['--output']

    # look for -t or --titles switch
    onlyListTitles = False
    if ('-t' in options) or ('--titles' in options):
        onlyListTitles = True

    # good, we can try opening the given file
    try:
        sql_connection = sqlite3.connect(dbFile)
        sql_cursor = sql_connection.cursor()
        sql_cursor.execute('select Bookmark.ContentID,Bookmark.Text,Bookmark.Annotation,Bookmark.ExtraAnnotationData,Bookmark.DateCreated,Bookmark.DateModified,content.BookTitle,content.Title from Bookmark, content WHERE Bookmark.ContentID = content.ContentID;')
        data = sql_cursor.fetchall()
        sql_cursor.close()
        sql_connection.close()
    except:
        print_error("File %s is not a valid KoboReader.sqlite db." % (dbFile), exitcode=4)

    # get data
    acc = []
    for t in data:
        content_id = escape(t[0])
        text = escape(t[1])
        annotation = escape(t[2])
        extra_annotation_data = escape(t[3])
        date_created = escape(t[4])
        date_modified = escape(t[5])
        booktitle = escape(t[6])
        title = escape(t[7])

        f_type = BOOKMARK
        if ((text != "") and (annotation != "")):
            f_type = ANNOTATION
        elif (text != ""):
            f_type = HIGHLIGHT
       
        # filter by book title
        if (keepOnlyBookWithTitle == None) or (keepOnlyBookWithTitle == booktitle):
            acc.append([f_type, booktitle, text, annotation, date_created, date_modified])

    # output titles to stdout
    if (onlyListTitles):
        print_("List of book titles with annotations (delimited by a ' character)")
        print_("")
        output = print_titles(acc)
    else: 
        # output stuff to stdout
        if (outputCSV):
            output = print_csv(acc)
        else:
            output = print_hr(acc)

    # output to stdout or file?
    if (outFile == None):
        # stdout
        print_(output)
    else:
        # file
        try:
            f = open(outFile, 'w')
            f.write(output)
            f.close()
        except:
            print_error("File %s cannot be written." % (outFile), exitcode=8)

    # return proper exit code
    sys.exit(0)
### END main ###



if __name__ == '__main__':
    # TODO let the user specify file encoding instead
    #Python2#    reload(sys)
    #Python2#    sys.setdefaultencoding("utf-8")
    main()


