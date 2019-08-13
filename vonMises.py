# Script for scanning the maximum von mises stress from the LS-Dyna output file. 
# Kindly use the von Mises output from all elements (use elout file)

import os, sys
import matplotlib.pyplot as plt
proceed = False
print sys.argv
print len(sys.argv)
if len(sys.argv)>1:
    vmfile = sys.argv[1]
    print (vmfile)
    if os.path.isfile(vmfile):
        proceed = True
if not proceed:
    sys.exit("Kindly specity the von Mises stresses Output File")
ifile = open(vmfile, "r")
lines = ifile.readlines()
ifile.close()
idx1 = []
idx2 = None 
for indx, line in enumerate(lines):
    if line[0:8]=="* Maxval":
        idx1.append(indx+1)
    if line[0:8]=="endcurve":
        idx2 = indx
print len(idx1)
blockLength = idx2-idx1[-1]
vmValues = {}
for i in range(0,blockLength):
    vmValues[i] = []
vmStressList = []
for i in range(0,blockLength):
    for j in idx1:
        x = lines[j+i].strip().split()[1].strip()
        vmStress = float(x)
        vmValues[i].append(vmStress)
#
for i in range(0,blockLength):
    vmStressList.append(max(vmValues[i]))
print vmStressList
time = [float(i)/10. for i in range(0,11)]
plt.plot(time, vmStressList)
plt.ylabel('von Mises Stress')
plt.xlabel("Total Time")
plt.grid(True)
plt.show()
