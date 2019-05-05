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
#path.append('C:\Users\Sim\Desktop\Oliver\Abaqus\design optimization')





model_name='thermal'
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
film_coeff= 12.0
bot_wall_temp= 50.0
temp_init= 23.0
air_temp= 23.0

#model related values
mesh_size= 0.005 #may be a tad coarse
mod.setValues(absoluteZero=-273, stefanBoltzmann=5.67e-08)

#sketch variables, SI units
ts= 0.01 #sidewall thickness
tb= 0.06 #bottom wall thickness
tt= 0.06 #top wall thickness
tw= 0.2 #total wall thickness
theta= m.pi/6 #zigzag angle from vertical, radians
wh= 2 #wall height
ti= t/m.sin(theta) #horizontal width of infill, will likely calculate with other inputs





#vertice calculations

num=8
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





#calculate cavities necessary for L>2.5
# n=8
# cav_length=2*(tw-tt-tb)*m.tan(theta)
# L=(n-1)*ti+(n/2-0.5)*cav_length

# while L<2:
	



#Sketch
mod.ConstrainedSketch(name='__profile__', sheetSize=20.0)

for i in range(0,num):
    mod.sketches['__profile__'].Line(point1=cav_set[i][0], point2=cav_set[i][1])
    mod.sketches['__profile__'].Line(point1=cav_set[i][1], point2=cav_set[i][2])
    mod.sketches['__profile__'].Line(point1=cav_set[i][2], point2=cav_set[i][0])

mod.sketches['__profile__'].Line(point1=bl_corner, point2=tl_corner)
mod.sketches['__profile__'].Line(point1=tl_corner, point2=tr_corner)
mod.sketches['__profile__'].Line(point1=tr_corner, point2=br_corner)
mod.sketches['__profile__'].Line(point1=br_corner, point2=bl_corner)





#create part
mod.Part(dimensionality=TWO_D_PLANAR, name='Part-1', type=DEFORMABLE_BODY)
mod.parts['Part-1'].BaseShell(sketch=mod.sketches['__profile__'])
del mod.sketches['__profile__']






#assign section
mod.HomogeneousSolidSection(material='conc', name='Section-1', thickness=wh)	
mod.parts['Part-1'].Set(faces=mod.parts['Part-1'].faces.findAt(((0.001,0.001,0.0),)), name='wholething')
mod.parts['Part-1'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=mod.parts['Part-1'].sets['wholething'], sectionName='Section-1', thicknessAssignment=FROM_SECTION)





#create assembly	
mod.rootAssembly.DatumCsysByDefault(CARTESIAN)
mod.rootAssembly.Instance(dependent=ON, name='Part-1-1', part=mod.parts['Part-1'])





#create sets, surfaces
bottom_mid= tuple(n.divide(tuple(n.add(br_corner, bl_corner)), (2, 2)))+(0.0,)
mod.rootAssembly.Set(edges=mod.rootAssembly.instances['Part-1-1'].edges.findAt((bottom_mid,)), name='bottom')

for i in range(0,num):
    cavmid1= tuple(n.divide(tuple(n.add(cav_set[i][0], cav_set[i][1])), (2, 2)))+(0.0,)
    cavmid2= tuple(n.divide(tuple(n.add(cav_set[i][1], cav_set[i][2])), (2, 2)))+(0.0,)
    cavmid3= tuple(n.divide(tuple(n.add(cav_set[i][2], cav_set[i][0])), (2, 2)))+(0.0,)
    mod.rootAssembly.Surface(name='cav'+str(i+1), side1Edges=mod.rootAssembly.instances['Part-1-1'].edges.findAt((cavmid1,), (cavmid2,), (cavmid3,)))

lwall_mid= tuple(n.divide(tuple(n.add(bl_corner, tl_corner)), (2, 2)))+(0.0,)
twall_mid= tuple(n.divide(tuple(n.add(tl_corner, tr_corner)), (2, 2)))+(0.0,)
rwall_mid= tuple(n.divide(tuple(n.add(tr_corner, br_corner)), (2, 2)))+(0.0,)
mod.rootAssembly.Surface(name='top', side1Edges=mod.rootAssembly.instances['Part-1-1'].edges.findAt((twall_mid,)))

	
#not sure what this does...
# mod.ConstrainedSketch(name='__edit__', objectToCopy=
    # mod.parts['Part-1'].features['Shell planar-1'].sketch)
# mod.parts['Part-1'].projectReferencesOntoSketch(filter=
    # COPLANAR_EDGES, sketch=mod.sketches['__edit__'], 
    # upToFeature=
    # mod.parts['Part-1'].features['Shell planar-1'])
	
	
	
	
	
#create representative surface for temperature analysis
mod.ConstrainedSketch(gridSpacing=0.16, name='__profile__', sheetSize=6.77, transform=mod.parts['Part-1'].MakeSketchTransform(sketchPlane=mod.parts['Part-1'].faces[0], sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0)))
mod.parts['Part-1'].projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=mod.sketches['__profile__'])

mod.sketches['__profile__'].Line(point1=cav_set[num/2-2][1], point2=cav_set[num/2][1])
mod.sketches['__profile__'].Line(point1=cav_set[num/2][1], point2=tuple(map(operator.add, cav_set[num/2][1], (0, tw))))
mod.sketches['__profile__'].Line(point1=tuple(map(operator.add, cav_set[num/2][1], (0, tw))), point2=tuple(map(operator.add, cav_set[num/2-2][1], (0, tw))))
mod.sketches['__profile__'].Line(point1=tuple(map(operator.add, cav_set[num/2-2][1], (0, tw))), point2=cav_set[num/2-2][1])

mod.parts['Part-1'].PartitionFaceBySketch(faces=mod.parts['Part-1'].faces.getSequenceFromMask(('[#1 ]', ), ), sketch=mod.sketches['__profile__'])
del mod.sketches['__profile__']
mod.rootAssembly.regenerate()

partition_mid= tuple(n.divide(tuple(n.add((cav_set[num/2-2][1][0], tw), (cav_set[num/2][1][0], tw))), (2, 2)))+(0.0,)
mod.rootAssembly.Set(edges=mod.rootAssembly.instances['Part-1-1'].edges.findAt((partition_mid,)), name='representative_surface')

	
	
	
	
	
#create heat transfer step
mod.HeatTransferStep(amplitude=RAMP, name='Step-1', previous='Initial', response=STEADY_STATE)



		
	
#BCs and interactions
#cavity radiation
mod.CavityRadiationProp(name='cement', property=((emissivity, ), ))
mod.CavityRadiation(createStepName='Step-1', name='cav_1', surfaceEmissivities=('cement', ), surfaces=(mod.rootAssembly.surfaces['cav1'], ))
mod.CavityRadiation(createStepName='Step-1', name='cav_2', surfaceEmissivities=('cement', ), surfaces=(mod.rootAssembly.surfaces['cav2'], ))
mod.CavityRadiation(createStepName='Step-1', name='cav_3', surfaceEmissivities=('cement', ), surfaces=(mod.rootAssembly.surfaces['cav3'], ))
mod.CavityRadiation(createStepName='Step-1', name='cav_4', surfaceEmissivities=('cement', ), surfaces=(mod.rootAssembly.surfaces['cav4'], ))
mod.CavityRadiation(createStepName='Step-1', name='cav_5', surfaceEmissivities=('cement', ), surfaces=(mod.rootAssembly.surfaces['cav5'], ))
mod.CavityRadiation(createStepName='Step-1', name='cav_6', surfaceEmissivities=('cement', ), surfaces=(mod.rootAssembly.surfaces['cav6'], ))
mod.CavityRadiation(createStepName='Step-1', name='cav_7', surfaceEmissivities=('cement', ), surfaces=(mod.rootAssembly.surfaces['cav7'], ))
mod.CavityRadiation(createStepName='Step-1', name='cav_8', surfaceEmissivities=('cement', ), surfaces=(mod.rootAssembly.surfaces['cav8'], ))
	
#convection
mod.FilmCondition(createStepName='Step-1', definition=EMBEDDED_COEFF, filmCoeff=film_coeff, filmCoeffAmplitude='', name='film', sinkAmplitude='', sinkDistributionType=UNIFORM, sinkFieldName='', sinkTemperature=air_temp, surface=mod.rootAssembly.surfaces['top'])

#surface radiation
mod.RadiationToAmbient(ambientTemperature=23.0, ambientTemperatureAmp='', createStepName='Step-1', distributionType=UNIFORM, emissivity=0.2, field='', name='Int-10', radiationType=AMBIENT, surface=mod.rootAssembly.surfaces['top'])
	
#temp BC
mod.TemperatureBC(amplitude=UNSET, createStepName='Step-1', distributionType=UNIFORM, fieldName='', fixed=OFF, magnitude=bot_wall_temp, name='temp_bot', region=mod.rootAssembly.sets['bottom'])

#initial temp
mod.Temperature(createStepName='Initial', crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, distributionType=UNIFORM, magnitudes=(temp_init, ), name='Predefined Field-1', region=mod.rootAssembly.instances['Part-1-1'].sets['wholething'])




#mesh
mod.parts['Part-1'].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=mesh_size)
mod.parts['Part-1'].setMeshControls(algorithm=MEDIAL_AXIS, elemShape=QUAD, regions=mod.parts['Part-1'].faces.getSequenceFromMask(('[#3 ]', ), ))
mod.parts['Part-1'].setElementType(elemTypes=(ElemType(elemCode=DC2D4, elemLibrary=STANDARD), ElemType(elemCode=DC2D3, elemLibrary=STANDARD)), regions=(mod.parts['Part-1'].sets['wholething']))
mod.parts['Part-1'].generateMesh()
mod.rootAssembly.regenerate()



	
	
#output requests
# mod.HistoryOutputRequest(createStepName='Step-1', name='H-Output-1', variables=('FTEMP', 'HFLA', 'HTL', 'HTLA', 'RADFL', 'RADFLA', 'RADTL', 'RADTLA', 'VFTOT', 'SJD', 'SJDA', 'SJDT', 'SJDTA', 'WEIGHT'))	
mod.fieldOutputRequests['F-Output-1'].setValues(variables=('NT', 'HFL', 'HFLA', 'HTL', 'HTLA', 'RFLE', 'RFL', 'RADFL', 'HBF'))
# del mod.fieldOutputRequests['F-Output-1']
mod.HistoryOutputRequest(createStepName='Step-1', frequency=LAST_INCREMENT, name='repr_surf_end_temp', rebar=EXCLUDE, region=mod.rootAssembly.sets['representative_surface'], sectionPoints=DEFAULT, variables=('NT', ))

	
#job creation/submission	
mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, 
    explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, 
    memory=90, memoryUnits=PERCENTAGE, model=model_name, modelPrint=OFF, 
    multiprocessingMode=DEFAULT, name=model_name, nodalOutputPrecision=SINGLE, 
    numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch='', type=
    ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
#mdb.Job(activateLoadBalancing=False, atTime=None, contactPrint=OFF, 
#	 description='', echoPrint=OFF, explicitPrecision=DOUBLE, historyPrint=OFF, 
#	 memory=90, memoryUnits=PERCENTAGE, model=model_name, modelPrint=OFF, 
#	 multiprocessingMode=DEFAULT, name=model_name, nodalOutputPrecision=SINGLE, 
#	 numCpus=16, numDomains=16, parallelizationMethodExplicit=DOMAIN, queue=None #8 processors per job is the fastest for 4 jobs, use 16 when doing a single job
#	 , resultsFormat=ODB, scratch='', type=ANALYSIS, userSubroutine='', 
#	 waitHours=0, waitMinutes=0)
mdb.jobs[model_name].submit(consistencyChecking=OFF)

mdb.jobs[model_name].waitForCompletion()

odb = openOdb(path='C:\\Users\\Sim\\Desktop\\Oliver\\design optimization\\GA\\thermal.odb')
step1 = odb.steps['Step-1']

with open("temperature_results.txt","w+") as writefile:
	for f in step1.historyRegions.values():
		region = step1.historyRegions[f.name]
		NT11Data = region.historyOutputs['NT11'].data
		for time, NT11 in NT11Data:
			if time>0.0:
				writefile.write(repr(NT11)+'\n')

