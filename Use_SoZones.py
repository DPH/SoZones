'''
Created on 27 Apr 2014

@author: David
'''
from sozones import SoZones

myZones = SoZones()

for zp in myZones.all_zones():
    print 'All', zp.player_name

for zp in myZones.masters():
    print 'Masters', zp.player_name

for zp in myZones.slaves():
    print 'Slaves:', zp.player_name

for zp in myZones.slaves_of('Study'):
    print 'Slaves of:', zp.player_name

print (myZones.topology)
