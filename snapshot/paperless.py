#!/usr/bin/python
import argparse
import datetime
import os.path
import PyPDF2 as pypdf
import re
from shutil import move as mv

class Paperless:
    
    DATE_CONVERTER ={
        '1':'01','2':'02','3':'03','4':'04','5':'05','6':'06','7':'07',
        '8':'08','9':'09',
        '01':'01','02':'02','03':'03','04':'04','05':'05','06':'06','07':'07',
        '08':'08','09':'09',
        '10':'10','11':'11','12':'12','13':'13','14':'14',
        '15':'15','16':'16',17:'17','18':'18','19':'19','20':'20','21':'21',
        '22':'22','23':'23','24':'24','25':'25','26':'26','27':'27','28':'28',
        '29':'29','30':'30','31':'31',
        'JANUARY':'01','FEBRUARY':'02','MARCH':'03','APRIL':'04','MAY':'05',
        'JUNE':'06','JULY':'07','AUGUST':'08','SEPTEMBER':'09','OCTOBER':'10',
        'NOVEMBER':'11','DECEMBER':'12','JAN':'01','FEB':'02','MAR':'03',
        'APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09',
        'OCT':'10','NOV':'11','DEC':'12'
    }
    
    PATTERN_FULLDATE = "(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC) *(\d{1,2}), *(\d{4}|\d{2})"
    PATTERN_NUMDATE = "(\d{1,2})[/-] *(\d{1,2})[/-] *(\d{4}|\d{2})"
    
    def __init__(self, path, file):
        self.__path = path
        self.__file = file
        self.__filepath = "%s/%s" % (path, file)
        self.__vendors = self.__loadVendors()
    
    def extractPDFContent(self, filepath=None):
        if filepath is None:
            filepath = self.__filepath
        
        file = open(filepath, "rb")
        pdf = pypdf.PdfFileReader(file)
        buffer = ""
        for i in range(0, pdf.getNumPages()):
            buffer += pdf.getPage(i).extractText() + " \n"
        buffer = " ".join(buffer.replace(u"\xa0", u" ").strip().split())
        file.close()
        
        content = ""
        for b in buffer:
            if 32 <= ord(b) <= 126:
                content += b
            else:
                content += ' '

        while "  " in content:
            content = content.replace("  ", " ")

        content = content.upper()
        self.__content = content
        return content

    def parseDates(self, content):
        if content is None:
            content = self.__content

    def __convertMonth(self, m):
        value = Paperless.DATE_CONVERTER[m]
        assert 1 <= int(value) <= 12
        return value

    def __convertDay(self, d):
        value = Paperless.DATE_CONVERTER[d]
        assert 1 <= int(value) <= 31
        return value

    def __convertYear(self, y):
        cy = datetime.datetime.now().year
        value = None
        if 4 == len(y):
            value = y
        elif 2 == len(y):
            value = '20%s' % y
            if cy < int(value):
                value = '19%s' % y
        assert int(value) <= cy
        return value

    def __parseDatePattern(self, pattern, content):
        p = re.compile(pattern)
        dates = []
        results = re.findall(p, content)
        for result in results:
            try:
                y = self.__convertYear(result[2])
                m = self.__convertMonth(result[0])
                d = self.__convertDay(result[1])
                date = "%s-%s-%s" % (y, m, d)
                if date not in dates:
                    dates.append("%s-%s-%s" % (y, m, d))
            except:
                pass
        return dates

    def parseDates(self, content=None):
        if content is None:
            content = self.__content
        dates = []
        dates += self.__parseDatePattern(pattern=Paperless.PATTERN_FULLDATE, content=content)
        dates += self.__parseDatePattern(pattern=Paperless.PATTERN_NUMDATE, content=content)
        return dates

    def getDate(self, override=0):
        ct = datetime.datetime.now()
        ct = "%s-%s-%s-%s-%s-%s-%s" % (ct.year, ct.month, ct.day, ct.hour,ct.minute, ct.second, ct.microsecond)
        datestamp = "e-%s" % ct
        dates = self.parseDates()
        if 1 == len(dates):
            datestamp = dates[0]
        else:
            if 0 == len(dates):
                datestamp = "z-%s" % ct
            elif 1 < len(dates):
                if 0 == override:
                    datestamp = "m-%s" % ct
                else:
                    datestamp = dates[override-1]
        return datestamp

    def __loadVendors(self):
        vendors = {}
        with open('/etc/paperless/vendors', 'r') as f:
            for line in f:
                line = line.strip()
                if 0 < len(line):
                    line = line.split("=")
                    vendors[line[0].strip()] = line[1].strip()
        f.close()
        return vendors

    def getVendor(self, content=None):
        if content is None:
            content = self.__content
        for pattern in self.__vendors.keys():
            cp = re.compile(pattern)
            result = re.findall(cp, content)
            if 0 < len(result):
                return self.__vendors[pattern]
        return "UNKNOWN"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help='File to parse')
    parser.add_argument('--content', help='Print extracted text', default=True)
    parser.add_argument('--date', help='Select which date from multiple dates found to use', default=0)
    args = parser.parse_args()

    path = os.path.dirname(args.file)
    path = os.path.abspath(path)
    file = os.path.split(args.file)[1]
    
    # path = '/Users/agautier/Desktop'
    # file = '2018-12-13-13-11-30.pdf'

    p = Paperless(path=path, file=file)
    content = p.extractPDFContent()
    # if args.content:
    print("CONTENT: ")
    print(content)
    print()
    print("------------------------------------------")
    print()
    dates = p.parseDates()
    print(dates)
    print()
    vendor = p.getVendor()
    print(vendor)

    nfile = "%s %s.pdf" % (p.getDate(override=int(args.date)), vendor)
    mv("%s/%s" % (path, file), "%s/%s" % (path, nfile))
