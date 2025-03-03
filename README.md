Made for transforming the data from the japanese cabinett into an easily analyzable format

Running the insert_data python file will ask for a Database.
This Database will be created and setup, so please do not choose an already existing file.

it will then ask for the website of the Kantei, which is usually a webpage, but can be set to a local path if the website is already downloaded.
pressing enter without typing anything will use the DEFAULT VALUE: https://www.kantei.go.jp/jp/rekidainaikaku/index.html

Correction Mode:
    if there are problems with the name (only first or last name existing) you will get the chance to Type in the correct version

The clean_data file will ask for an existing database to clean up.

the autosave feature can be turned on. this will save after every edit, but may slow down the process.

it will then start by working through name problems and ask for corrections (first & Last name identical)
then it will show duplicates and ask which one to keep
deleting the duplicates is a seperate check afterwards.
to finish it will ask for unreferenced datasets to delete.
