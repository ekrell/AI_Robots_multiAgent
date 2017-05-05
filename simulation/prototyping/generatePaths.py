
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--outdir", help = "output directory")
parser.add_argument("-d", "--diff", help = "max difference between waypoints")
args = parser.parse_args()

x = args.diff

p1 = []
p2 = []
p3 = []
for x in range (5):
    seed =  (random.randint(-60,60), random.randint(-60,60)) 
    p1.append ( ( random.randint(seed[0] - x, seed[0] + 1), random.randint(seed[1] - 1, seed[1] + 1)) )
    p2.append ( ( random.randint(seed[0] - x, seed[0] + 1), random.randint(seed[1] - 1, seed[1] + 1)) )
    p3.append ( ( random.randint(seed[0] - x, seed[0] + 1), random.randint(seed[1] - 1, seed[1] + 1)) )


outP1 = args.outdir + "susan.waypoints"
outP2 = args.outdir + "django.waypoints"
outP3 = args.outdir + "anton.waypoints"

fP1 = open (outP1, 'w')
fP2 = open (outP2, 'w')
fP3 = open (outP3, 'w')

for x in range (5):
    line = '{0},{1}\n'.format(p1[x][0], p1[x][1])
    fP1.write (line)
    line = '{0},{1}\n'.format(p2[x][0], p2[x][1])
    fP2.write (line)
    line = '{0},{1}\n'.format(p3[x][0], p3[x][1])
    fP3.write (line)
print (p1)
print (p2)
print (p3)

fP1.close ()
fP2.close ()
fP3.close ()
