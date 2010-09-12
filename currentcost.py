#!/usr/bin/env python

# XML lib
import xml.dom.minidom as minidom
from time import localtime

class Packet:
    """
    XML packet
    """
    def __init__(self, source, log_dir):
        """Gets an XML packet from the serial connection and parses it"""

        # This just waits until the XML comes through
        self.xml = {}
        self.xml['text'] = source.readline()
        self.xml['dom'] = minidom.parseString(self.xml['text'])

        # Parse into packet data - element names are unique in child nodes
        self.parse_data()


        # Store log dir
        self.log_dir = log_dir.rstrip('/') + '/'

    def parse_data(self):
        """Parse XML data into a set of dicts, and pull out relevant data"""

        msg = self.xml['dom'].childNodes[0]
        self.data = xml_to_dicts(msg, False)

        # Get some metadata together
        self.id = "%s:%s" % (self.data['src']['name']['#cdata'], self.data['src']['id']['#cdata'])
        self.temp = self.data['tmpr']['#cdata']
        self.watts = self.data['ch1']['watts']['#cdata']

        # Time - CurrentCost and local
        self.date = {}
        self.date['cc'] = [ int(self.data['date'][k]['#cdata']) for k in ('dsb','hr','min','sec') ]
        self.date['now'] = localtime()

    def ts(self, which='now'):
        """Generate a timestamp from an internally stored date"""
        if which == 'now':
            return '%d%02d%02dT%02d%02d%02d' % self.date['now'][0:6]
        else:
            return '%05dT%02d%02d%02d' % (self.date['cc'][0], self.date['cc'][1], self.date['cc'][2], self.date['cc'][3])

    def save_raw(self):
        """Save raw data"""
        f = open(self.log_dir + 'raw.txt', 'a')
        try:
            f.write(self.xml['text'])
        finally:
            f.close()

    def log(self):
        """Write single-line plain-text logfile"""
        f = open(self.log_dir + 'parsed.log', 'a')
        try:
            # Write: local time | CurrentCost "time" | id | temp/C | power/W 
            f.write("%s\t%s\t%s\t%s\t%s\n" 
              % (self.ts('now'), self.ts('cc'), self.id, self.temp, self.watts))
        finally:
            f.close()

    def log_all(self):
        """Perform all log and save operations"""
        self.save_raw()
        self.log()

def xml_to_dicts(xml, cope_with_duplicates=True):
    d = {}
    for n in xml.childNodes:
        try:
            # Tag - parse its child nodes
            k = n.tagName
            dd = xml_to_dicts(n, cope_with_duplicates)
        except AttributeError:
            # Not tag - return text
            k = '#cdata'
            dd = n.wholeText
        if cope_with_duplicates:
            # Use an array to cope with duplicate values
            if not d.has_key(k):
                d[k] = []
            d[k].append(dd)
        else:
            # Just set a direct value
            d[k] = dd
    return d
