# supreme-fiesta
gentoo portage browser

The goal here is to create a nice gentoo command line portage browser. Just display the descriptions of the packages available. I've been wanting one of these for a long time, just never sat down to write one. There's no reason that it can't pull more info from the ebuild files, like USE flags, but EIX already does that.

The initial commit just creates a database of the top level categories - with the directory names and descriptions from the metadata.xml file located in those directories.

~~Next step is to iterate through those tld's and grab the DESCRIPTION and populate a new package table.~~

~~The database is now populated. Now comes the hard part - creating an app that can browse the db.~~

The start of a curses gui app. This is undoubtedly going to change significantly.
If you run portwalk.py with a package name - it will display the description of all packages with that exact name. If you run it without a package name - it starts the gui. Right now, it just displays the categories in /usr/portage - along with the description shown in the status line. Ctrl-x to exit.

# To do: 
* ~~Populate the packages table~~
* ~~Add config file (for language, database name, etc.)~~
* ~~Add argparse for single packages/categories~~
* ~~Command line client to work with the database. ATM the only function it has is generate new database~~
* ~~(The big one) Front end curses application~~
* Get the curses app to display the contents of the sub-directories, the actual packages themselves.

All of the command line switches can be set in the config file as well!
# Usage:
```bash

 portwalk.py [-h] [-L LOG_LEVEL] [-l LANGUAGE] [-d DIRECTORY]
                   [-n DATABASE] [-t DBDIR] [-g] [-H]
                   [package]

A command line portage browser

positional arguments:
  package               Specify package name

optional arguments:
  -h, --help            show this help message and exit
  -L LOG_LEVEL, --log-level LOG_LEVEL
                        Set log level (CRITICAL, ERROR, WARNING, INFO, DEBUG)
  -l LANGUAGE, --language LANGUAGE
                        Choose the language you want to use
  -d DIRECTORY, --directory DIRECTORY
                        Set base directory to search
  -n DATABASE, --database DATABASE
                        Set the name of the database
  -t DBDIR, --dbDir DBDIR
                        Set the target location of the database
  -g, --generate        Generate a new database.
  -H, --homepage        Show homepage in results.
```
  
So - say you're in /usr/portage/net-analyzer and want to see the description for nagios
```$ portwalk nagios
dev-ruby/nagios:   Nagios-rb is a compact framework for writing Nagios plugins
net-analyzer/nagios:   The Nagios metapackage
```
You'll see all exact results for packages named nagios. I may implement fuzzy searches in the future, but that's not what I want  today. With the -H option, it will also print the home page of the project. You can change the configs to generate a new db every time it's run.

Note: I made a symlink in /usr/local/bin and made portwalk.py executable. Also - the path to the portwalk.py directory is hard coded:
```python
    # THIS NEEDS TO BE IMPROVED!
    installDir = os.environ['HOME']+"/work/supreme-fiesta/portageWalker/"
```
