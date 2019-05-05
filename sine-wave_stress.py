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
# path.append('C:\Users\Sim\Desktop\Oliver\Abaqus')





model_name='stress'
mdb.Model(modelType=STANDARD_EXPLICIT, name=model_name)
mod=mdb.models[model_name]
del mdb.models['Model-1']

input = open('C:\\Users\\Sim\\Desktop\\Oliver\\design optimization\\GA\\inputs.txt', 'r').read().splitlines()
t=float(input[1])



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

#sketch variables, SI units
ts= 0.0 #sidewall thickness
tb= 0.06 #bottom wall thickness
tt= 0.06 #top wall thickness
tw= 0.2 #total wall thickness
ti= t #horizontal width of infill, will likely calculate with other inputs
theta= m.pi/6 #zigzag angle from vertical, radians
wh= 2 #wall height





#calculations
num=4





#sketch
mod.ConstrainedSketch(name='__profile__', sheetSize=20.0)

Amp= (ti-tb-tt)+tw
points = []
for i in range(301):
	x = (float(i)/100)*Amp
	y = (Amp/2)*m.cos((m.pi/Amp)*x)+Amp/2
	points.append([x,y])

points_Loff=[]
points_Roff=[]
for i in range(301):
	if i==0:
		slope=0
	elif i==300:
		slope=0
	else:
		Lslope=(points[i][1]-points[i-1][1])/(points[i][0]-points[i-1][0])
		Rslope=(points[i+1][1]-points[i][1])/(points[i+1][0]-points[i][0])
		slope=(Lslope+Rslope)/2
	if slope!=0:
		rotslope= -1/slope
		if slope>0:
			Lx=-m.sqrt(((ti/2)**2)/((rotslope**2)+1))
			Rx=m.sqrt(((ti/2)**2)/((rotslope**2)+1))
		else:
			Lx=m.sqrt(((ti/2)**2)/((rotslope**2)+1))
			Rx=-m.sqrt(((ti/2)**2)/((rotslope**2)+1))
		Ly=rotslope*Lx
		Ry=rotslope*Rx
	else:
		Lx=0.0
		Rx=0.0
		Ly=ti/2
		Ry=-ti/2
	
	points_Loff.append([Lx+points[i][0],Ly+points[i][1]])
	points_Roff.append([Rx+points[i][0],Ry+points[i][1]])

mod.sketches['__profile__'].Spline(points=points_Loff)
mod.sketches['__profile__'].Spline(points=points_Roff)

mod.sketches['__profile__'].Line(point1=(points_Roff[0][0],points_Roff[0][1]), point2=(points_Roff[300][0],points_Roff[0][1]))
mod.sketches['__profile__'].Line(point1=(points_Loff[300][0],points_Loff[300][1]), point2=(points_Loff[0][0],points_Loff[300][1]))

mod.sketches['__profile__'].autoTrimCurve(curve1=
    mod.sketches['__profile__'].geometry[4], point1=(points_Roff[0][0]+0.0001,points_Roff[0][1]))
mod.sketches['__profile__'].autoTrimCurve(curve1=
    mod.sketches['__profile__'].geometry[6], point1=(points_Roff[200][0]-0.0001,points_Roff[200][1]))
mod.sketches['__profile__'].autoTrimCurve(curve1=
    mod.sketches['__profile__'].geometry[8], point1=(points_Roff[200][0]+0.0001,points_Roff[200][1]))
	
mod.sketches['__profile__'].autoTrimCurve(curve1=
    mod.sketches['__profile__'].geometry[5], point1=(points_Loff[100][0]-0.0001,points_Loff[100][1]))
mod.sketches['__profile__'].autoTrimCurve(curve1=
    mod.sketches['__profile__'].geometry[10], point1=(points_Loff[100][0]+0.0001,points_Loff[100][1]))
mod.sketches['__profile__'].autoTrimCurve(curve1=
    mod.sketches['__profile__'].geometry[12], point1=(points_Loff[300][0]-0.0001,points_Loff[300][1]))
	
mod.sketches['__profile__'].Line(point1=(points_Roff[0][0],points_Roff[0][1]), point2=(points_Loff[0][0],points_Roff[0][1]+tt))
mod.sketches['__profile__'].Line(point1=(points_Loff[300][0],points_Loff[300][1]), point2=(points_Roff[300][0],points_Loff[300][1]-tb))

mod.sketches['__profile__'].autoTrimCurve(curve1=
    mod.sketches['__profile__'].geometry[2], point1=(points_Loff[1][0],points_Loff[1][1]))
mod.sketches['__profile__'].autoTrimCurve(curve1=
    mod.sketches['__profile__'].geometry[16], point1=(points_Loff[200][0],points_Loff[200][1]))
	
	
mod.sketches['__profile__'].autoTrimCurve(curve1=
    mod.sketches['__profile__'].geometry[3], point1=(points_Roff[100][0],points_Roff[100][1]))
mod.sketches['__profile__'].autoTrimCurve(curve1=
    mod.sketches['__profile__'].geometry[20], point1=(points_Roff[300][0],points_Roff[300][1]))

mod.sketches['__profile__'].Line(point1=(points_Roff[0][0]-ts,points_Roff[0][1]+tt), point2=(points_Roff[300][0]+ts,points_Roff[0][1]+tt))
mod.sketches['__profile__'].Line(point1=(points_Loff[300][0]+ts,points_Loff[300][1]-tb), point2=(points_Loff[0][0]-ts,points_Loff[300][1]-tb))

mod.sketches['__profile__'].Line(point1=(points_Roff[0][0]-ts,points_Loff[300][1]), point2=(points_Loff[0][0]-ts,points_Loff[300][1]-tb))
mod.sketches['__profile__'].Line(point1=(points_Loff[300][0]+ts,points_Roff[0][1]), point2=(points_Roff[300][0]+ts,points_Roff[0][1]+tt))

L=points_Loff[300][0]+ts





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
mod.rootAssembly.Surface(name='side', side1Faces=mod.rootAssembly.instances['Part-1-1'].faces.findAt(((L/2, points_Roff[0][1]+tt, wh/2),)))





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
# mdb.Job(activateLoadBalancing=False, atTime=None, contactPrint=OFF, 
	# description='', echoPrint=OFF, explicitPrecision=DOUBLE, historyPrint=OFF, 
	# memory=90, memoryUnits=PERCENTAGE, model=model_name, modelPrint=OFF, 
	# multiprocessingMode=DEFAULT, name=model_name, nodalOutputPrecision=SINGLE, 
	# numCpus=16, numDomains=16, parallelizationMethodExplicit=DOMAIN, queue=None #8 processors per job is the fastest for 4 jobs, use 16 when doing a single job
	# , resultsFormat=ODB, scratch='', type=ANALYSIS, userSubroutine='', 
	# waitHours=0, waitMinutes=0)
mdb.jobs[model_name].submit(consistencyChecking=OFF)

mdb.jobs[model_name].waitForCompletion()


odb = openOdb(path='C:\\Users\\Sim\\Desktop\\Oliver\\design optimization\\GA\\thermal.odb')
lastFrame = odb.steps['Step-1'].frames[-1]
stress=lastFrame.fieldOutputs['S']

with open("stress_results.txt","w+") as writefile:
	for S in stress.values:
		writefile.write(repr(S.maxPrincipal)+'\n')

