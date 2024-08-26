#!/usr/bin/python3
""" see https://pypi.org/project/icalendar/
get calendars for Germany from https://www.schulferien.org/deutschland/ical/
"""

from datetime import timedelta, timezone, datetime
import glob
import argparse
import os
from icalendar import Calendar
from dateutil.rrule import rruleset, rrulestr

OPENHAB_CONF = "/etc/openhab/"
try:
    OPENHAB_CONF = os.environ["OPENHAB_CONF"]
except KeyError:
    print("No variable OPENHAB_CONF found")

parser = argparse.ArgumentParser(
    description="Convert school holidays ICS files, e.g. from https://www.schulferien.org/deutschland/ical/"
)

parser.add_argument(
    "-v", "--verbose", default=0, action="store_const", const=1, help="activate logging"
)
parser.add_argument(
    "-i",
    "--inPath",
    default=os.path.join(OPENHAB_CONF, "scripts/"),
    help="set path where the ics files are",
)
parser.add_argument(
    "-o",
    "--outFile",
    default=os.path.join(OPENHAB_CONF, "services/holidays.xml"),
    help="set the out file",
)

args = parser.parse_args()

FILE_NAME_FILTER = "*.ics"

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

XML_FILE_CONTENT = """\
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


def parse_recurrences(recur_rule, start, exclusions):
    """Find all reoccuring events"""
    rules = rruleset()
    first_rule = rrulestr(recur_rule, dtstart=start)
    rules.rrule(first_rule)
    if not isinstance(exclusions, list):
        exclusions = [exclusions]
        for xdate in exclusions:
            try:
                rules.exdate(xdate.dts[0].dt)
            except AttributeError:
                pass
    now = datetime.now(timezone.utc)
    this_year = now + timedelta(days=60)
    dates = []
    for rule in rules.between(now, this_year):
        dates.append(rule.strftime("%D %H:%M UTC "))
    return dates


COUNT = 0

for filename in glob.glob(os.path.join(args.inPath, FILE_NAME_FILTER)):
    if args.verbose > 0:
        print(f"parsing file {filename}")
    with open(filename, "rb") as ics_file:
        cal = Calendar.from_ical(ics_file.read())

    if args.verbose > 1:
        print(cal)
    XML_FILE_CONTENT += f"\t<!-- filename = {filename} -->\n"

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
                XML_FILE_CONTENT += f"\t\t<!-- reason = {summary} -->\n"
                for single_date in daterange(startdt, enddt):
                    if args.verbose > 0:
                        print(single_date.strftime("%Y-%m-%d"))
                    if args.verbose > 1:
                        print(int(single_date.strftime("%m")))
                        month = MONTHS[int(single_date.strftime("%m"))]
                        print(month)
                        addString = f"""\t\t<tns:Fixed month=\"{month}\" """
                        print(addString)
                    addString = f"\t\t<tns:Fixed month=\"{MONTHS[int(single_date.strftime('%m'))]}\" day=\"{single_date.strftime('%d')}\" descriptionPropertiesKey=\"{summary}\" validFrom=\"{single_date.strftime('%Y')}\" validTo=\"{single_date.strftime('%Y')}\" />\n"
                    if args.verbose > 0:
                        print(addString)
                    XML_FILE_CONTENT += addString
                    COUNT += 1

XML_FILE_CONTENT += "\t</tns:Holidays>"
XML_FILE_CONTENT += "</tns:Configuration>"

with open(args.outFile, mode="w", encoding="utf-8") as out_file:
    out_file.write(XML_FILE_CONTENT)

print(f"Added {COUNT} items to file {args.outFile}")
