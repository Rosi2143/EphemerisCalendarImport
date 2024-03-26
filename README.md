# EphemerisCalendarImport
Make the the school holiday calendar of [schulferien.org](https://www.schulferien.org/deutschland/ferien/)
available as a [JollyDay](https://github.com/svendiedrichsen/jollyday) XML file, e.g. for use in [OpenHab Ephemeris](https://www.openhab.org/docs/configuration/actions.html#ephemeris).

The script imports the data from the school calendar files for your state into a xml-file readable by the Ephemeris action.
## get the calendars
Calendars for German school holidays are centrally provided by [schulferien.org](https://www.schulferien.org/deutschland/ferien/).

Just download the calendar for your state **[from here](https://www.schulferien.org/deutschland/ical/)** and store it. 
You can download as many calendars as you want.

## advantages of this fork
This fork has the following changes:
* ported to Pythos 3
* added the actual *year* to the generated calendar entry (this was missing causing errors and eoverlapping entries when used with multiple years)

## Preconditions

### python 3
install [python 3](https://www.python.org/downloads/)

### install icalendar
The script depends on the [icalendar package](https://pypi.org/project/icalendar/)
Run this command to install it

```
pip install icalendar
```
or
```
python2 -m pip install icalendar
```

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
