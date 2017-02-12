# export-kobo

A Python tool to export annotations and highlights from a Kobo SQLite file.

* Version: 2.1.1
* Date: 2017-02-12
* Developer: [Alberto Pettarin](http://www.albertopettarin.it/)
* License: the MIT License (MIT)
* Contact: [click here](http://www.albertopettarin.it/contact.html)

## Usage

```bash
$ # print all annotations and highlights to stdout
$ python export-kobo.py KoboReader.sqlite

$ # print the help
$ python export-kobo.py --help

$ # export to file instead of stdout
$ python export-kobo.py KoboReader.sqlite --output /path/to/out.txt

$ # export in CSV format
$ python export-kobo.py KoboReader.sqlite --csv

$ # export in CSV format to file
$ python export-kobo.py KoboReader.sqlite --csv --output /path/to/out.csv

$ # export in Kindle My Clippings format
$ python export-kobo.py KoboReader.sqlite --kindle

$ # export in Kindle My Clippings to file
$ python export-kobo.py KoboReader.sqlite --kindle --output /path/to/out.csv

$ # export annotations only
$ python export-kobo.py KoboReader.sqlite --annotations-only

$ # export highlights only
$ python export-kobo.py KoboReader.sqlite --highlights-only

$ # export as CSV to file annotations only
$ python export-kobo.py KoboReader.sqlite --csv  --annotations-only --output /path/to/out.txt

$ # print the list of books with annotations or highlights to stdout
$ python export-kobo.py KoboReader.sqlite --list

$ # as above, but export to file
$ python export-kobo.py KoboReader.sqlite --list --output /path/to/out.txt

$ # as above, but export in CSV format
$ python export-kobo.py KoboReader.sqlite --list --csv --output /path/to/out.txt

$ # export annotations and highlights for the book "Alice in Wonderland"
$ python export-kobo.py KoboReader.sqlite --book "Alice in Wonderland"

$ # as above, assuming "Alice in Wonderland" has ID "12" in the list printed by --list
$ python export-kobo.py KoboReader.sqlite --bookid 12
```


## Installation

If you are a Windows user and you need help with Python,
please follow [this step-by-step guide](https://github.com/pettarin/python-on-windows).

Installing **export-kobo** is relatively simple:

1. Install Python, 3.x (recommended), or 2.7.x,
   and make sure you have the ``python`` command available in your shell;

2. Clone this repository:
    ```bash
    $ git clone https://github.com/pettarin/export-kobo
    ```
   or manually download the ZIP file from the [Releases tab](https://github.com/pettarin/export-kobo/releases/) and unzip it somewhere;

3. Enter the directory where ``export-kobo.py`` is:
    ```bash
    $ cd export-kobo
    ```

4. Copy in the same directory the ``KoboReader.sqlite`` file
   from the ``.kobo/`` hidden directory of the USB drive
   that appears when you plug your Kobo device to the USB port of your PC.
   You might need to enable the ``View hidden files`` option
   in your file manager to see the hidden directory;

5. Now you can run the script as explained above, for example:
    ```bash
    $ python export-kobo.py KoboReader.sqlite
    ```


## Troubleshooting

### I am on Windows, but I do not know how to install Python

You can find a complete step-by-step guide to install Python
and run **export-kobo** at the following URL:
[https://github.com/pettarin/python-on-windows](https://github.com/pettarin/python-on-windows)

### I am on Windows, and I get this error: ``python is not recognized as an internal or external command, operable program or batch file``

Make sure you installed Python for your current user
(e.g., check the ``Install for all users`` option in the Python installer),
and that the directory containing the ``python.exe`` executable
is in your ``PATH`` environment variable
(e.g., check the ``Add Python to my PATH`` option in the Python installer).

If you have already installed Python, but it is not in your ``PATH``, see
[this page](https://docs.python.org/3/using/windows.html)
for directions to solve this issue.

### I got lots of question marks (``?``) in my output

If you are using Python 2.7.x, try switching to Python 3.x,
which has saner support for Unicode characters.

You might also want to use the ``--output FILE`` switch
to output to file instead of printing to standard output.

### I ran the script, but I obtained too much data

If you want to output annotations or highlights for a single book,
you can use the ``--list`` option to list all books with annotations or highlights,
and then use ``--book`` or ``--bookid`` to export only those you are interested in:

``` bash
$ python export-kobo.py KoboReader.sqlite --list
ID  Title
1   Alice in Wonderland
2   Moby Dick
3   Sonnets
...

$ python export-kobo.py KoboReader.sqlite --book "Alice in Wonderland"
...
$ python export-kobo.py KoboReader.sqlite --bookid 1
...
```

Alternatively, you can export to a CSV file with ``--csv --output FILE``
and then open the resulting output file with a spreadsheet application,
disregarding the annotations/highlights you are not interested in:

```bash
$ python export-kobo.py KoboReader.sqlite --csv --output notes.csv
$ libreoffice notes.csv
```

### I filtered my notes by book title with ``--book``, but I got no results

Check that you wrote the book title exactly as printed by ``--list``
(e.g., copy-and-paste it), or use ``--bookid`` instead.


## Notes

1. Around May 2016 Kobo changed the schema
   of their ``KoboReader.sqlite`` database with a firmware update.
   The ``export-kobo.py`` script in the main directory of this repository
   works for this **new** database schema.
   If you still have an old firmware on your Kobo,
   and hence the old database schema,
   you might want to use one of the scripts in the ``old/`` directory.
   Note, however, that those scripts are very old, possibly buggy,
   and they are no longer supported
   ([old Web page](http://www.albertopettarin.it/exportnotes.html)).

2. Since I no longer use a Kobo eReader,
   this project is maintained in "legacy mode".
   Changes to the schema of the ``KoboReader.sqlite`` database
   can be reflected on the code
   only thanks to users sending me their ``KoboReader.sqlite`` file,
   for me to study its schema.

3. Bear in mind that no official specifications are published by Kobo,
   hence the script works as far as
   my understanding of the database structure of ``KoboReader.sqlite`` is correct,
   and its schema remains the same.

4. Although the ``KoboReader.sqlite`` file is opened in read-only mode,
   it is advisable to make a copy of it on your PC
   and export your notes from this copy,
   instead of directly accessing the file on your Kobo eReader device.


## Acknowledgments

* Chris Krycho contributed a fix for a typo in month names
* Pierre-Arnaud Rabier suggested adding an option to extract the annotations and highlights for a single ebook.
* Nick Kalogirou and Andrea Moro provided me with theirs KoboReader.sqlite file with the new schema.
* Curiositry suggested adding an option to extract in Kindle My Clippings format.


## License

**export-kobo** is released under the MIT License.



