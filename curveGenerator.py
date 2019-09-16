# Script to automate the curve extraction procedure
# Hypermesh function from msa

import fcm
import os, re
import subprocess as sp
os.system("cls") 

projDir = os.path.join("D:\\1-FCMS\\01-CraTE\\06-fromMubeen\\Sampaul","Work")
print projDir

if not os.path.exists(projDir):
	os.mkdir(projDir)

includeFilesFolderPath = "D:\\1-FCMS\\01-CraTE\\06-fromMubeen\\Sampaul\\includes"
### SPECIFY THE LOAD NAMES
loadsNameList = ["Tension", "Compression", "TorsionXpos", "TorsionXneg", "BendingYpos", "BendingYneg", "BendingZpos", "BendingZneg"]

### SPECIFY THE BOUNDARY CONDITIONS INCLUDE FILES:
loadIncludeFiles = {
    "Tension"    : os.path.join(includeFilesFolderPath,"include_bend_Y_neg.dyn"),
    "Compression": os.path.join(includeFilesFolderPath,"include_bend_Y_pos.dyn"),
    "TorsionXpos": os.path.join(includeFilesFolderPath,"include_bend_Z_neg.dyn"),
    "TorsionXneg": os.path.join(includeFilesFolderPath,"include_bend_Z_pos.dyn"),
    "BendingYpos": os.path.join(includeFilesFolderPath,"include_compression.dyn"),
    "BendingYneg": os.path.join(includeFilesFolderPath,"include_rot_X_neg.dyn"),
    "BendingZpos": os.path.join(includeFilesFolderPath,"include_rot_X_pos.dyn"),
    "BendingZneg": os.path.join(includeFilesFolderPath,"include_tension.dyn")
    }
   
def createDynaMesh(meshdir):  
    import BatchMeshHyperMesh, time
    from BatchMeshHyperMesh import KEY_CREATE_PROPERTY_JOIN
    if not os.path.exists(meshdir):
        return False
    solver = fcm.SOLVER_LSDYNA
    mesh_options = { 'SURFACE_LINE_MERGE' : False,
            'MERGE_DUP_NODES' : True,
            #'EXCLUDE_CURRENT_PROPERTY' : True,
            #CREATE_PROPERTY_JOIN'  : False,
            #'CUSTOM_CRITERIA_FILE' : 'fcm_10mm.criteria',
            #'CUSTOM_PARAMETER_FILE': 'fcm_10mm.param',
            'KEY_SOLVER_NAME' : solver
        }
    mesh_output_file = BatchMeshHyperMesh.mesh_lsdyna(meshdir,mesh_options)
    return mesh_output_file

def read_mesh(mesh_file):
    f = open(mesh_file,"r")
    lines = f.readlines()
    f.close()
    data = ["\n"]
    in_mesh = False
    for line in lines:
        if re.match('^\*KEYWORD\s+$', line):
            in_mesh = True
            continue
        if in_mesh:
            data.append(line)
    return data

def exportDynaMesh(mesh_file, loadIncludeFiles, combnId):
    hmOutputDir = os.path.split(mesh_file)[0]
    OutputFileNamesMap = {}
    for loadName, loadIncludeFile in loadIncludeFiles.iteritems():
        print "\n\n\n Load Name: ", loadName, "\n Load File: ", loadIncludeFile
        exportDir = os.path.join(hmOutputDir,loadName)
        os.mkdir(exportDir)
        if not os.path.exists(exportDir) or not os.path.exists(loadIncludeFile):
            print "\n\n\n\nERROR: Skipping Load Case: ", loadName
            print "due to nonexistent \nMesh export directory:", exportDir, "\nor LoadIncludeFile:", loadIncludeFile
            continue
        mesh_lines = read_mesh(mesh_file)
        d = open(loadIncludeFile,"r")
        include_lines = d.readlines()
        d.close()
        include_lines.extend(mesh_lines)
        OutputFileName = "fcm_solution_%d_%s.dyn"%(combnId,loadName) 
        dynFile = os.path.join(hmOutputDir, OutputFileName)
        print "Dyna File will be printed to:   ", dynFile
        f = open(dynFile,"w")
        f.writelines(include_lines)
        f.close()
        OutputFileNamesMap[exportDir] = dynFile
    print "Dyna file exported to: ", dynFile
    return OutputFileNamesMap

#global loadIncludeFiles
#projDir = "D:\\batchmesh\\TestDynaShells"
if not os.path.exists(projDir):
    fcm.showError("The path does not exists.\nPlease check the path specified.")
    os.mkdir(projDir)
    os.chdir(projDir)
    #return False
parametersNames = ("xs_scale", "beam_length", "thickness")
parameterSetName = "Parameters"
psetList = fcm.listParameterSet()
parameterSet = None
for p in psetList:
    if p.name() == parameterSetName:
        parameterSet = p
        print parameterSet, parameterSet.name()
print "\n\n\n"
paramList = parameterSet.getParameters()
paramNamesMap = {}
for p in paramList:
    p_name = p.name().split("\\")[-1]
    if p_name in parametersNames:
        paramNamesMap[p_name] = p
#
# for each parameter, there is a corresponding list containing values
combinations = []
xs_scale    = [1.0]  #, 1.5, 2.0]  # "xs_scale"
beam_length = [250.0]  # "beam_length"
thickness   = [1.0] #, , 2.0]  # "thickness"
# create combinations of the parameters 
for x in xs_scale:
    for b in beam_length:
        for t in thickness:
            combinations.append((x,b,t))

configList = "%-16s%-16s%-16s%-16s\n"%("indx", "xs_scale", "beam_length", "thickness")

for indx, c in enumerate(combinations):
    xs,bl,th = paramNamesMap["xs_scale"],paramNamesMap["beam_length"],paramNamesMap["thickness"]
    xs.setValue(c[0])
    bl.setValue(c[1])
    th.setValue(c[2])
    fcm.updateActivePart()
    fcm.updateActivePart()
    meshdir = os.path.join(projDir,str(indx))
    os.mkdir(meshdir)
    configList += "%-8d%-8s%-16s%-16s%-16s\n"%(indx," ", str(c[0]), str(c[1]), str(c[2]))
    print "\n\n\n\nPrinting the mesh directory", meshdir
    if os.path.exists(meshdir):
        print "Mesh directory generated"
        mesh_file = createDynaMesh(meshdir)
        try:
            myfile = open(mesh_file, "r") 
            myfile.close()
        except:
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>Could not open file! Please close "
        print "Mesh generated :   ", mesh_file 
        OutputDirFileNamesMap = exportDynaMesh(mesh_file, loadIncludeFiles, indx)
        for exportDir, outputFile in OutputDirFileNamesMap.iteritems():
            print "LSDyna mesh exported for combination # ", indx, "\t: ",c 
            print "File: ", outputFile 
            os.chdir(exportDir)
            print "Current Solution Working Directory: ", os.getcwd()
            lsdyna_exe = os.getenv("LSDYNA_EXE")
            print "LS-Dyna exe: ", lsdyna_exe
            sp.check_output(lsdyna_exe +" I="+ outputFile + " ncpu=4") 
            os.chdir(projDir)

configFile = open("Configurations.txt","w")
configFile.write(configList)
configFile.close()
#
#main("F:\\Work")
#fcm.showFolderPickerDialog('Select directory for LS Dyna Shell outputs:', main, 'D:\\Batchmesh')
