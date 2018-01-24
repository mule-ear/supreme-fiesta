# supreme-fiesta
gentoo portage browser

The goal here is to create a nice gentoo command line portage browser. Just display the descriptions of the packages available. I've been wanting one of these for a long time, just never sat down to write one.

The initial commit just creates a database of the top level categories - with the directory names and descriptions from the metadata.xml file located in those directories.

Next step is to iterate through those tld's and grab the DESCRIPTION and populate a new package table.

# To do: 
* ~~Populate the packages table~~
* Add config file (for language, database name, etc.)
* Add argparse for single packages/categories
* (The big one) Front end curses application

 
