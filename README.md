# EphemerisCalendarImport
import the school holiday calendar of [schulferien.org](https://www.schulferien.org/deutschland/ferien/)

The script imports the data from the school calendar files for your state into a xml-file readable by the Ephemeris action.
## get the calendars
Calendars for German school holidays are centrally provided by [schulferien.org](https://www.schulferien.org/deutschland/ferien/).

Just download the calendar for your state and store it. You can download as many calendars as you want.

## usage
* put all calendar files into one folder
  * default is **$OPENHAB_CONF/scripts**
* start the scripts
  * if the parameter "-o / --outFile" is not used the file **$OPENHAB_CONF/services/holidays.xml** will be created

```
usage: ephemeris.py [-h] [-v] [-i INPATH] [-o OUTFILE]

read school holidays from https://www.schulferien.org/deutschland/ical/

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         activate logging
  -i INPATH, --inPath INPATH
                        set path where the ics files are
  -o OUTFILE, --outFile OUTFILE
                        set the out file
```
