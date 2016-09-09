#!/usr/bin/env python
# coding=utf-8

# The MIT License (MIT)
#
# Copyright (c) 2013-2016 Alberto Pettarin (alberto@albertopettarin.it)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Export annotations and highlights from a Kobo SQLite file.
"""

from __future__ import absolute_import
from __future__ import print_function
import argparse
import csv
import io
import os
import sqlite3
import sys

__author__ = "Alberto Pettarin"
__email__ = "alberto@albertopettarin.it"
__copyright__ = "Copyright 2016, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__status__ = "Production"
__version__ = "2.0.0"


PY2 = (sys.version_info[0] == 2)


class CommandLineTool(object):

    # overload in the actual subclass
    #
    AP_PROGRAM = sys.argv[0]
    AP_DESCRIPTION = u"Generic Command Line Tool"
    AP_ARGUMENTS = [
        # required args
        # {"name": "foo", "nargs": 1, "type": str, "default": "baz", "help": "Foo help"},
        #
        # optional args
        # {"name": "--bar", "nargs": "?", "type": str,, "default": "foofoofoo", "help": "Bar help"},
        # {"name": "--quiet", "action": "store_true", "help": "Do not output to stdout"},
    ]

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog=self.AP_PROGRAM,
            description=self.AP_DESCRIPTION
        )
        self.vargs = None
        for arg in self.AP_ARGUMENTS:
            if "action" in arg:
                self.parser.add_argument(
                    arg["name"],
                    action=arg["action"],
                    help=arg["help"]
                )
            else:
                self.parser.add_argument(
                    arg["name"],
                    nargs=arg["nargs"],
                    type=arg["type"],
                    default=arg["default"],
                    help=arg["help"]
                )

    def run(self):
        self.vargs = vars(self.parser.parse_args())
        self.actual_command()
        sys.exit(0)

    # overload this in your actual subclass
    def actual_command(self):
        self.print_stdout(u"This script does nothing. Invoke another .py")

    def error(self, message):
        self.print_stderr(u"ERROR: %s" % message)
        sys.exit(1)

    def print_stdout(self, *args, **kwargs):
        print(*args, **kwargs)

    def print_stderr(self, *args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)


class Item(object):

    ANNOTATION = "annotation"
    BOOKMARK = "bookmark"
    HIGHLIGHT = "highlight"

    def __init__(self, values):
        self.volumeid = values[0]
        self.text = values[1]
        self.annotation = values[2]
        self.extraannotationdata = values[3]
        self.datecreated = values[4]
        self.datemodified = values[5]
        self.booktitle = values[6]
        self.title = values[7]
        self.kind = self.BOOKMARK
        if (self.text is not None) and (self.text != "") and (self.annotation is not None) and (self.annotation != ""):
            self.kind = self.ANNOTATION
        elif (self.text is not None) and (self.text != ""):
            self.kind = self.HIGHLIGHT

    def csv_tuple(self):
        return (self.kind, self.title, self.datecreated, self.datemodified, self.annotation, self.text)

    def __repr__(self):
        return u"(%s, %s, %s, %s, %s, %s)" % self.csv_tuple()

    def __str__(self):
        acc = []
        sep = u"\n=== === ===\n"
        if self.kind == self.ANNOTATION:
            acc.append(u"Type:           %s" % (self.kind))
            acc.append(u"Title:          %s" % (self.title))
            acc.append(u"Date created:   %s" % (self.datecreated))
            acc.append(u"Annotation:%s%s%s" % (sep, self.annotation, sep))
            acc.append(u"Reference text:%s%s%s" % (sep, self.text, sep))
        if self.kind == self.HIGHLIGHT:
            acc.append(u"Type:           %s" % (self.kind))
            acc.append(u"Title:          %s" % (self.title))
            acc.append(u"Date created:   %s" % (self.datecreated))
            acc.append(u"Reference text:%s%s%s" % (sep, self.text, sep))
        return u"\n".join(acc)


class Book(object):

    def __init__(self, values):
        self.volumeid = values[0]
        self.booktitle = values[1]
        self.title = values[2]

    def __repr__(self):
        return u"(%s, %s, %s)" % (self.volumeid, self.booktitle, self.title)

    def __str__(self):
        return self.__repr__()


class ExportKobo(CommandLineTool):

    AP_PROGRAM = u"export-kobo"
    AP_DESCRIPTION = u"Export annotations and highlights from a Kobo SQLite file."
    AP_ARGUMENTS = [
        {
            "name": "db",
            "nargs": None,
            "type": str,
            "default": None,
            "help": "Path of the input KoboReader.sqlite file"
        },
        {
            "name": "--output",
            "nargs": "?",
            "type": str,
            "default": None,
            "help": "Output to file instead of using the standard output"
        },
        {
            "name": "--csv",
            "action": "store_true",
            "help": "Output in CSV format instead of human-readable format"
        },
        {
            "name": "--list",
            "action": "store_true",
            "help": "List the titles of books with annotations or highlights"
        },
        {
            "name": "--book",
            "nargs": "?",
            "type": str,
            "default": None,
            "help": "Output annotations and highlights only from the book with the given title"
        },
        {
            "name": "--bookid",
            "nargs": "?",
            "type": str,
            "default": None,
            "help": "Output annotations and highlights only from the book with the given ID"
        },
        {
            "name": "--annotations-only",
            "action": "store_true",
            "help": "Outputs annotations only, excluding highlights"
        },
        {
            "name": "--highlights-only",
            "action": "store_true",
            "help": "Outputs highlights only, excluding annotations"
        },
        {
            "name": "--info",
            "action": "store_true",
            "help": "Print information about the number of annotations and highlights"
        },
    ]

    QUERY_ITEMS = (
        "SELECT "
        "Bookmark.VolumeID, "
        "Bookmark.Text, "
        "Bookmark.Annotation, "
        "Bookmark.ExtraAnnotationData, "
        "Bookmark.DateCreated, "
        "Bookmark.DateModified, "
        "content.BookTitle, "
        "content.Title "
        "FROM Bookmark INNER JOIN content "
        "ON Bookmark.VolumeID = content.ContentID;"
    )

    QUERY_BOOKS = (
        "SELECT DISTINCT "
        "Bookmark.VolumeID, "
        "content.BookTitle, "
        "content.Title "
        "FROM Bookmark INNER JOIN content "
        "ON Bookmark.VolumeID = content.ContentID "
        "ORDER BY content.Title;"
    )

    def __init__(self):
        super(ExportKobo, self).__init__()
        self.items = []

    def actual_command(self):
        if self.vargs["db"] is None:
            self.error(u"You must specify the path to your KoboReader.sqlite file.")

        books = self.enumerate_books()
        if self.vargs["list"]:
            # export list of books
            acc = []
            acc.append((u"ID", u"TITLE"))
            for (i, b) in books:
                acc.append((i, b.title))
            if self.vargs["csv"]:
                acc = self.list_to_csv(acc)
            else:
                acc = u"\n".join([(u"%s\t%s" % (a, b)) for (a, b) in acc])
        else:
            # export annotations and/or highlights
            items = self.read_items()
            if self.vargs["csv"]:
                acc = self.list_to_csv([i.csv_tuple() for i in items])
            else:
                template = u"%s\n"
                acc = u"\n".join([(template % i) for i in items])

        if self.vargs["output"] is not None:
            # write to file
            try:
                with io.open(self.vargs["output"], "w", encoding="utf-8") as f:
                    f.write(acc)
            except IOError:
                self.error(u"Unable to write output file. Please check that the path is correct and that you have write permission on it.")
        else:
            # write to stdout
            try:
                self.print_stdout(acc)
            except UnicodeEncodeError:
                self.print_stdout(acc.encode("ascii", errors="replace"))

        if self.vargs["info"]:
            self.print_stdout(u"")
            self.print_stdout(u"Books with annotations or highlights: %d" % len(books))
            if not self.vargs["list"]:
                self.print_stdout(u"Annotations and/or highlights:        %d" % len(items))

    def list_to_csv(self, data):
        if PY2:
            # PY2
            output = io.BytesIO()
        else:
            # PY3
            output = io.StringIO()
        writer = csv.writer(output)
        for d in data:
            try:
                writer.writerow(d)
            except UnicodeEncodeError:
                writer.writerow(tuple([v.encode("ascii", errors="replace") for v in d]))
        if PY2:
            # PY2
            return output.getvalue().decode("utf-8")
        else:
            # PY3
            return output.getvalue()

    def enumerate_books(self):
        books = [Book(d) for d in self.query(self.QUERY_BOOKS)]
        return list(enumerate(books, start=1))

    def volumeid_from_bookid(self):
        enum = self.enumerate_books()
        bookid = self.vargs["bookid"]
        try:
            return enum[int(bookid) - 1][1].volumeid
        except:
            self.error(u"The bookid value must be an integer between 1 and %d" % (len(enum)))

    def read_items(self):
        items = [Item(d) for d in self.query(self.QUERY_ITEMS)]
        if len(items) == 0:
            return items
        if (self.vargs["bookid"] is not None) and (self.vargs["book"] is not None):
            self.error(u"You cannot specify both --book and --bookid.")
        if self.vargs["bookid"] is not None:
            items = [i for i in items if i.volumeid == self.volumeid_from_bookid()]
        if self.vargs["book"] is not None:
            items = [i for i in items if i.title == self.vargs["book"]]
        if self.vargs["highlights_only"]:
            items = [i for i in items if i.kind == Item.HIGHLIGHT]
        if self.vargs["annotations_only"]:
            items = [i for i in items if i.kind == Item.ANNOTATION]
        return items

    def query(self, query):
        db_path = self.vargs["db"]
        if not os.path.exists(db_path):
            self.error(u"Unable to read the KoboReader.sqlite file. Please check that the path is correct and that you have read permission on it.")
        try:
            sql_connection = sqlite3.connect(db_path)
            sql_cursor = sql_connection.cursor()
            sql_cursor.execute(query)
            data = sql_cursor.fetchall()
            sql_cursor.close()
            sql_connection.close()
        except Exception as exc:
            self.error(u"Unexpected error reading your KoboReader.sqlite file: %s" % (exc))
        # NOTE the values are Unicode strings (unicode on PY2, str on PY3)
        #      hence data is a list of tuples of Unicode strings
        return data


def main():
    ExportKobo().run()


if __name__ == "__main__":
    main()
