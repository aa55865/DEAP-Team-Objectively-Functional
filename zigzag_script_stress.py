# -*- coding: mbcs -*-
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
from sys import path
import operator
import math as m
import numpy as n
from odbAccess import *
path.append('C:\Users\Sim\Desktop\Oliver\Abaqus')





model_name='stress_model'
mdb.Model(modelType=STANDARD_EXPLICIT, name=model_name)
mod=mdb.models[model_name]
del mdb.models['Model-1']





#material
#cement/concrete
mod.Material(name='conc')
mod.materials['conc'].Elastic(table=((10.6e9, 0.3), )) #mod of elasticity, poisson ratio
mod.materials['conc'].Conductivity(table=((0.29, ), )) #cement mortor -> 1.73
mod.materials['conc'].SpecificHeat(table=((1550.0, ), ))
mod.materials['conc'].Density(table=((3150.0, ), ))
emissivity= 0.2

#BC related values
pressure=1500 #N/m^2, calculated as wind pressure when wind speed = 100 mph (moderate tornado)

#model related values
mesh_size= 0.015 #may be a tad coarse
mod.setValues(absoluteZero=-273, stefanBoltzmann=5.67e-08)

#import sketch variables, SI units
valnum=1
with open ('HT_inputfile.txt', 'rt') as var_values: # Open file
    for value in var_values:
        if valnum==1:
            ts= value
        elif valnum==2:
            tb= value
        elif valnum==3:
            tt= value
        elif valnum==4:
            tw= value
        elif valnum==5:
            ti= value
        elif valnum==6:
            theta= value
        elif valnum==7:
            wh= value
        valnum+=1
#ts= sidewall thickness
#tb= bottom wall thickness
#tt= top wall thickness
#tw= total wall thickness
#ti= horizontal width of infill, will likely calculate with other inputs
#theta= zigzag angle from vertical, radians
#wh= wall height





#calculations
num=4
cav_length=2*(tw-tt-tb)*m.tan(theta)
L=(num-1)*ti+(num/2-0.5)*cav_length

# while L<2.0:
    # num=num+2
    # L=(num-1)*ti+(num/2-0.5)*cav_length

cav_set=[]
bl_corner= (0, 0)
tl_corner= (0, tw)

for i in range(0,num):
    if i==0:
        cav1= (ts, tw-tt)
        cav2= tuple(map(operator.add, cav1, ((tw-tt-tb)*m.tan(theta), 0)))
        cav3= (ts, tb)
        cavlist=[cav1,cav2,cav3]
        cav_set.append(cavlist)
    if (i%2)==1 and i!=num-1:
        cav1= tuple(map(operator.add, cav_set[i-1][1], (ti, 0)))
        cav2= tuple(map(operator.add, cav1, ((tw-tt-tb)*m.tan(theta), (-tw+tt+tb))))
        cav3= tuple(map(operator.add, cav_set[i-1][2], (ti, 0)))
        cavlist=[cav1,cav2,cav3]
        cav_set.append(cavlist)
    if (i%2)==0 and i!=0 and i!=num-1:
        cav1= tuple(map(operator.add, cav_set[i-1][0], (ti, 0)))
        cav3= tuple(map(operator.add, cav_set[i-1][1], (ti, 0)))
        cav2= tuple(map(operator.add, cav3, ((tw-tt-tb)*m.tan(theta), (tw-tt-tb))))
        cavlist=[cav1,cav2,cav3]
        cav_set.append(cavlist)
    if i==num-1:
        cav1= tuple(map(operator.add, cav_set[i-1][1], (ti, 0)))
        cav2= tuple(map(operator.add, cav1, (0, (-tw+tt+tb))))
        cav3= tuple(map(operator.add, cav_set[i-1][2], (ti, 0)))
        tr_corner= tuple(map(operator.add, cav1, (ts, tt)))
        br_corner= tuple(map(operator.add, cav2, (ts, -tb)))
        cavlist=[cav1,cav2,cav3]
        cav_set.append(cavlist)





#sketch
mod.ConstrainedSketch(name='__profile__', sheetSize=200.0)

for i in range(0,num):
    mod.sketches['__profile__'].Line(point1=cav_set[i][0], point2=cav_set[i][1])
    mod.sketches['__profile__'].Line(point1=cav_set[i][1], point2=cav_set[i][2])
    mod.sketches['__profile__'].Line(point1=cav_set[i][2], point2=cav_set[i][0])

mod.sketches['__profile__'].Line(point1=bl_corner, point2=cav_set[0][2])
mod.sketches['__profile__'].Line(point1=tl_corner, point2=cav_set[0][0])
mod.sketches['__profile__'].Line(point1=tl_corner, point2=tr_corner)
mod.sketches['__profile__'].Line(point1=tr_corner, point2=cav_set[3][0])
mod.sketches['__profile__'].Line(point1=br_corner, point2=cav_set[3][1])
mod.sketches['__profile__'].Line(point1=br_corner, point2=bl_corner)

mod.sketches['__profile__'].delete(objectList=(mod.sketches['__profile__'].geometry[4], ))
mod.sketches['__profile__'].delete(objectList=(mod.sketches['__profile__'].geometry[11], )) #4 cavities





#part creation
mod.Part(dimensionality=THREE_D, name='Part-1', type=
    DEFORMABLE_BODY)
mod.parts['Part-1'].BaseSolidExtrude(depth=wh, sketch=
    mod.sketches['__profile__'])
del mod.sketches['__profile__']


#section creation/assignment
mod.HomogeneousSolidSection(material='conc', name='Section-1', 
    thickness=None)
mod.parts['Part-1'].Set(cells=mod.parts['Part-1'].cells.getSequenceFromMask(('[#1 ]', ), ), name='Set-1')
mod.parts['Part-1'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=mod.parts['Part-1'].sets['Set-1'], sectionName='Section-1', thicknessAssignment=FROM_SECTION)





#create assembly
mod.rootAssembly.DatumCsysByDefault(CARTESIAN)
mod.rootAssembly.Instance(dependent=OFF, name='Part-1-1', part=mod.parts['Part-1'])





#create static loading step
mod.rootAssembly.Instance(dependent=OFF, name='Part-1-1', 
    part=mod.parts['Part-1'])
mod.StaticStep(initialInc=0.001, name='Step-1', previous='Initial')





#create surfaces/sets
mod.rootAssembly.Set(faces=mod.rootAssembly.instances['Part-1-1'].faces.findAt(((0.001, 0.001, 0.0),)), name='bot')
mod.rootAssembly.Surface(name='top', side1Faces=mod.rootAssembly.instances['Part-1-1'].faces.findAt(((0.001, 0.001, wh),)))
mod.rootAssembly.Surface(name='side', side1Faces=mod.rootAssembly.instances['Part-1-1'].faces.findAt(((L/2, tw, wh/2),)))





#Loads and BCs
mod.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='rigidBC', region=mod.rootAssembly.sets['bot'], u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET)
mod.Pressure(amplitude=UNSET, createStepName='Step-1', distributionType=UNIFORM, field='', magnitude=pressure, name='Load-1', region=mod.rootAssembly.surfaces['side'])





#mesh
mod.rootAssembly.setElementType(elemTypes=(ElemType(elemCode=C3D8R, elemLibrary=STANDARD, secondOrderAccuracy=OFF, kinematicSplit=AVERAGE_STRAIN, hourglassControl=DEFAULT, distortionControl=DEFAULT), ElemType(elemCode=C3D6, elemLibrary=STANDARD), ElemType(elemCode=C3D4, elemLibrary=STANDARD)), regions=(mod.rootAssembly.instances['Part-1-1'].cells.getSequenceFromMask(('[#1 ]', ), ), ))
mod.rootAssembly.seedPartInstance(deviationFactor=0.1, 
    minSizeFactor=0.1, regions=(
    mod.rootAssembly.instances['Part-1-1'], ), size=mesh_size)
mod.rootAssembly.generateMesh(regions=(
    mod.rootAssembly.instances['Part-1-1'], ))





#job
mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, 
    explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, 
    memory=90, memoryUnits=PERCENTAGE, model=model_name, modelPrint=OFF, 
    multiprocessingMode=DEFAULT, name=model_name, nodalOutputPrecision=SINGLE, 
    numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch='', type=
    ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
mdb.jobs[model_name].submit(consistencyChecking=OFF)

mdb.jobs[model_name].waitForCompletion()





#write output file
odb = openOdb(path='C:\\Temp\\Job-1.odb') # enter path e.g. as C:\SIMULIA\Temp\...file.odb
lastFrame = odb.steps['Step-1'].frames[-1]
stress=lastFrame.fieldOutputs['S']

with open("stress_results.txt","w+") as writefile:
	for S in stress.values:
		writefile.write(repr(S.maxPrincipal)+'\n')
