#!/usr/bin/python3
# see https://pypi.org/project/icalendar/
# get calendars for Germany from https://www.schulferien.org/deutschland/ical/

from datetime import timedelta
import glob
import argparse
import os
from icalendar import Calendar

OpenHabConf = "/etc/openhab/"
try:
    OpenHabConf = os.environ["OPENHAB_CONF"]
except KeyError:
    print("No variable OPENHAB_CONF found")

count = 0

parser = argparse.ArgumentParser(
    description="Convert school holidays ICS files, e.g. from https://www.schulferien.org/deutschland/ical/"
)

parser.add_argument(
    "-v", "--verbose", default=0, action="store_const", const=1, help="activate logging"
)
parser.add_argument(
    "-i",
    "--inPath",
    default=os.path.join(OpenHabConf, "scripts/"),
    help="set path where the ics files are",
)
parser.add_argument(
    "-o",
    "--outFile",
    default=os.path.join(OpenHabConf, "services/holidays.xml"),
    help="set the out file",
)

args = parser.parse_args()

FileNameFilter = "*.ics"

MONTHS = {
    1: "JANUARY",
    2: "FEBRUARY",
    3: "MARCH",
    4: "APRIL",
    5: "MAY",
    6: "JUNE",
    7: "JULY",
    8: "AUGUST",
    9: "SEPTEMBER",
    10: "OCTOBER",
    11: "NOVEMBER",
    12: "DECEMBER",
}

xmlFileContent = """\
<?xml version="1.0" encoding="UTF-8"?>
<tns:Configuration hierarchy="de" description="Germany"
\txmlns:tns="http://www.example.org/Holiday" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
\txsi:schemaLocation="http://www.example.org/Holiday /Holiday.xsd">
\t<tns:Holidays>
"""


def daterange(start_date, end_date):
    """
    Generate a range of dates between the start_date and end_date. Args:
        start_date (datetime.date): The start date of the range.
        end_date (datetime.date): The end date of the range.
    Yields:
        datetime.date: The dates in the range.
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


for filename in glob.glob(os.path.join(args.inPath, FileNameFilter)):
    if args.verbose > 0:
        print(f"parsing file {filename}")
    file = open(filename, "rb")
    cal = Calendar.from_ical(file.read())

    if args.verbose > 1:
        print(cal)
    xmlFileContent += f"\t<!-- filename = {filename} -->\n"

    for component in cal.walk():
        if component.name == "VEVENT":
            summary = component.get("summary")
            description = component.get("description")
            location = component.get("location")
            startdt = component.get("dtstart").dt
            enddt = component.get("dtend").dt
            exdate = component.get("exdate")
            if component.get("rrule"):
                reoccur = component.get("rrule").to_ical().decode("utf-8")
                for item in parse_recurrences(reoccur, startdt, exdate):
                    if args.verbose > 0:
                        print(f"\t{item} {summary}: {description} - {location}")
            else:
                if args.verbose > 0:
                    print(
                        f"\t{0}-{1} {2}: {3} - {4}".format(
                            startdt.strftime("%D %H:%M UTC"),
                            enddt.strftime("%D %H:%M UTC"),
                            summary,
                            description,
                            location,
                        )
                    )
                xmlFileContent += f"\t\t<!-- reason = {summary} -->\n"
                for single_date in daterange(startdt, enddt):
                    if args.verbose > 0:
                        print(single_date.strftime("%Y-%m-%d"))
                    if args.verbose > 1:
                        print(int(single_date.strftime("%m")))
                        month = MONTHS[int(single_date.strftime("%m"))]
                        print(month)
                        addString = f"""\t\t<tns:Fixed month=\"{month}\" """
                        print(addString)
                    addString = """\t\t<tns:Fixed month=\"{_month}\" day=\"{_day}\" descriptionPropertiesKey=\"{_summary}\" validFrom=\"{_from}\" validTo=\"{_to}\" />\n""".format(
                        _month=MONTHS[int(single_date.strftime("%m"))],
                        _day=single_date.strftime("%d"),
                        _summary=summary,
                        _from=single_date.strftime("%Y"),
                        _to=single_date.strftime("%Y"),
                    )
                    if args.verbose > 0:
                        print(addString)
                    xmlFileContent += addString
                    count = count + 1

xmlFileContent += "\t</tns:Holidays>"
xmlFileContent += "</tns:Configuration>"

filehandle = open(args.outFile, mode="w", encoding="utf-8")
filehandle.write(xmlFileContent)
filehandle.close

print("Added %d items to file %s" % (count, args.outFile))
