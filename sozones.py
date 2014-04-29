'''
@author: DPH
contains SoZones a class to manage the Sonos topology
'''
from __future__ import print_function
import soco
from soco.utils import really_utf8
from time import sleep
import xml.etree.cElementTree as XML


class SoZones(object):
    ''' A class to get and hold information about the Sonos zones
    Public functions returning a python generator object of:
        all_zones --  all SoCo instances
        masters -- all master SoCo instances
        slaves -- a python generator object of slave SoCo instances
        slave_of - a python generator object of slave SoCo instances for

    '''
    topology = {}
    ''' store for topology of zone players in the system.
        A dictionary of dictionaries one for each zone:
        {'<ip>: {'master': True,
                 'group': 'RINCON_000E5832DEB401400',
                 'zone_name': 'Study'},
                         .......
                        }
         '<ip2>':{'master': False, etc.........}
        }

        '''
    def __init__(self):
        '''Initiate class with all zones in the Sonos system
        if IP given use that zone to extract details, otherwise
        use discover to find zones and use one.
        '''
        starter_zp = None

        while starter_zp is None:
            my_zones = list(soco.discover())
            if len(my_zones) > 0:
                starter_zp = my_zones[0]  # grab first IP found
            else:
                # caters for network not responding or busy
                print ("Warning - not discovered any zone players! - trying again")
                sleep(1)

        # get zone player topology by querying one IP (all ZPs hold the full topology)
        zone_count = self._set_topology(starter_zp)

        if zone_count > 0:  # found at least one zone
            print ('...found %d zones' % (zone_count))
            # add all the soco instances to topology
            for found_soco in my_zones:
                found_ip = found_soco.__dict__['ip_address']
                self.topology[found_ip]['soco'] = found_soco

    def _set_topology(self, zp):
        '''
        improved (!)version of SoCo get_toplogy:
        - uses uPnP call to one zone player
        - excludes invisible zones (e.g. in stereo pair)
        - builds dictionary with key of ip and a dictionary of zone details
        Note: uses master = True v.s. SoCo Coordinator = True!
        '''
        # get group state from one zone via direct uPnP call using SoCo
        zgroups = zp.zoneGroupTopology.GetZoneGroupState()['ZoneGroupState']  
        tree = XML.fromstring(really_utf8(zgroups))
        for grp in tree:
            for zp in grp:
                # ignore zones marked as Invisible (e.g. one of a stereo pair)
                if 'Invisible' in zp.attrib:  # Invisible info not always there
                    if zp.attrib['Invisible']:  # Invisible ==1 (True)
                        continue
                ip_key = zp.attrib['Location'].split('//')[1].split(':')[0]
                self.topology[ip_key] = {}
                self.topology[ip_key]['uuid'] = zp.attrib['UUID']
                self.topology[ip_key]['zone_name'] = zp.attrib['ZoneName']  #not needed if this is the key!!!!!!!
                self.topology[ip_key]['master'] = (zp.attrib['UUID'] == grp.attrib['Coordinator'])
                self.topology[ip_key]['group'] = grp.attrib['Coordinator']
        return len(self.topology)

    def all_zones(self):
        '''gets all slaves
        output a python generator object of SoCo instances
        '''
        for zp in self.topology.values():
            yield zp['soco']

    def masters(self):
        '''gets all masters
        output a python generator object of SoCo instances
        '''
        for zp in self.topology.values():
            if zp['master']:
                yield zp['soco']

    def slaves(self):
        '''gets all slaves
        output a python generator object of SoCo instances
        '''
        for zp in self.topology.values():
            if not zp['master']:
                yield zp['soco']

    def slaves_of(self, master):
        '''returns soco instances of slaves for a master
        input zone name or ip address as string
        output a python generator object of SoCo instances
        '''
        grp = None
        for ip, zp in self.topology.iteritems():
            if master == zp['zone_name'] or master == ip:
                grp = zp['group']
        
        for zp in self.topology.values():
            if not zp['master']:
                if grp == zp['group']:
                    yield zp['soco']
