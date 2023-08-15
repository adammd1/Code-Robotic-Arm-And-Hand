import serial, sys
import time
import numpy as np
import random as Random


import pyNN.nest as sim

currentTime = 0
TIME_STEP = 1.0
numberNeurons = 500
synapsesFromEachNeuron = 30
weight = 0.0039;
CHECK_STEPS = 1

#---Neuron Stuff
#initialize the simulator. 
def init():
    sim.setup(timestep=TIME_STEP,min_delay=TIME_STEP,
                    max_delay=TIME_STEP, debug=0)

def createNeurons():
    numNeurons = fsa.CA_SIZE * 3
    cells=sim.Population(numNeurons,sim.IF_cond_exp,fsa.CELL_PARAMS)
    return cells

def setupRecording(cells):
    cells.record({'spikes','v'})

def createInput(Time):
    inputSpikeTimes0 = [Time,Time+10, Time+20]
    spikeArray0 = {'spike_times': [inputSpikeTimes0]}
    spikeGen0=sim.Population(1,sim.SpikeSourceArray,spikeArray0,
                                   label='inputSpikes_0')

    return spikeGen0

def checkThreshold(cells):
    #print("checkThresh " + str(currentTime))
    data = cells.get_data('spikes')
    segment = data.segments[0]
    spikeTrains = segment.spiketrains
    lastNeuron = len(spikeTrains) - 1

    totalSpikes=0
    #Go through all the neurons
    for neuronNum in range(0,lastNeuron):
        spikes = spikeTrains[neuronNum]
        #add spikes in last 10 steps
        numberSpikes = len(spikes)
        for spikeNum in range(0,numberSpikes):
            spikeTime =spikes[spikeNum]
            #print (spikeTime)
            if (spikeTime>(currentTime-10)):
                totalSpikes = totalSpikes + 1

    print (currentTime, totalSpikes)
    if (totalSpikes > 1100):
        return True
    return False

def runUntilThreshold(cells):
    global currentTime
    stepDuration = CHECK_STEPS
    done = False
    step = 0
    while (not done):
        sim.run(stepDuration)
        currentTime = currentTime + stepDuration
        if (checkThreshold(cells)):
            done = True
        #else: time.sleep(0.01)

    
    
def printResults(simCells):
    simCells.printSpikes('temp.pkl')

#Get connections so that each neuron has one leaving and one entering.
#Can have a self connection
def getOneToOneConnection(toArray,numOneToOne):
    global numberNeurons
    
    synapseNeuronPairs = []
    #create a connection list with numOneTOne synapses leaving and one 
    #entering each neuron.
    for currentSynapsesPerNeuron in range (0,numOneToOne):
        singleSynapses = 0
        #For each neuron
        for fromNeuron in range (0,numberNeurons):
            #See how many open neurons to skip
            toOpenNeuron = Random.randint(0,(numberNeurons-singleSynapses)-1)
            toNeuron = 0
            toNeuronFound = False
            while (not toNeuronFound):
                #skip neuron slots that are already filled
                while (toArray[toNeuron] == currentSynapsesPerNeuron+1): 
                    toNeuron = toNeuron+1
                if (toOpenNeuron == 0):
                    toNeuronFound = True
                    synapseNeuronPairs = synapseNeuronPairs+[(fromNeuron,toNeuron)]
                    singleSynapses = singleSynapses + 1
                    toArray[toNeuron] = toArray[toNeuron]+1
                toOpenNeuron = toOpenNeuron -1
                toNeuron = toNeuron+1
    return synapseNeuronPairs

def inPairList(fromNeuron,toNeuron,list):
    result = False
    posInList = 0
    while posInList < len(list):
        if ((list[posInList][0] == fromNeuron) and 
            (list[posInList][1] == toNeuron)):
            #print element
            result = True
        posInList = posInList + 1

    return result

def getNextSynapse(fromNeuron,toArray,synapseNeuronPairs):
    done = False
    synapses = len(synapseNeuronPairs)
    while (not done):
        synapsesToSkip = Random.randint(0,synapses-1)
        toNeuron = 0
        synapsesSkipped = toArray[toNeuron]
        while (synapsesSkipped < synapsesToSkip):
            toNeuron = toNeuron + 1
            synapsesSkipped = synapsesSkipped + toArray[toNeuron]
            #print toNeuron, synapsesToSkip, synapsesSkipped
        if (not inPairList(fromNeuron,toNeuron,synapseNeuronPairs)):
            done = True

    return toNeuron


#This makes a small world topology with a (roughly) constant number of
#synapses leaving each neuron, but a rich gets richer ratio of those entering
def smallWorldToConnect(neurons):
    global numberNeurons
    
    toArray = np.zeros(numberNeurons) #How many connections come into each neur

    numOneToOneConnections = 1
    synapseNeuronPairs = getOneToOneConnection(toArray,numOneToOneConnections)
    #print toArray

    synapses = numberNeurons
    for outSynapseNumber in range (0,synapsesFromEachNeuron):
        for fromNeuron in range (0,numberNeurons):
            toNeuron = getNextSynapse(fromNeuron,toArray,synapseNeuronPairs)
            synapses = synapses + 1
            toArray[toNeuron] = toArray[toNeuron]+ 1
            synapseNeuronPairs = synapseNeuronPairs+[(fromNeuron,toNeuron)]

    #copy the synapse pairs to the connector
    connector = []
    stdConnector = []
    for synapseOffset in range (0,len(synapseNeuronPairs)):
        fromNeuron = synapseNeuronPairs[synapseOffset][0]
        toNeuron = synapseNeuronPairs[synapseOffset][1]
        connector = connector+ [(fromNeuron,toNeuron,weight,TIME_STEP)]

    print (len(connector))
    #connector = cleanUpSynapses(connector)
    #comment the filehandle and pickle lines back into dump the last sw.
    #fileHandle = open("tempConn","w")
    #pickle.dump(connector,fileHandle)
    #fileHandle.close()
    fromListConnector = sim.FromListConnector(connector)
    sim.Projection(neurons, neurons, fromListConnector,
                   receptor_type='excitatory')
    return synapses

def igniteCA(spikeSource,cells,neuronsToStart,startWt):
    connector = []
    
    printNeurons = []
    for neuronOn in range (0,neuronsToStart):
        toNeuron = Random.randint(0,numberNeurons -1)
        printNeurons = printNeurons + [toNeuron]
        connector = connector+ [(0,toNeuron,startWt,TIME_STEP)]
    fromListConnector = sim.FromListConnector(connector)
    sim.Projection(spikeSource, cells, fromListConnector,
                   receptor_type='excitatory')



#--main
args = sys.argv
numberArgs = args.__len__()
print (args, numberArgs)
if (numberArgs == 4):
    seed = int(args[1])
    mixStart = int(args[2])
    ignitingNeurons = int(args[3])
    print (seed,mixStart,ignitingNeurons)
else:
    seed = 4
    mixStart = 0
    ignitingNeurons = 50


#simName = "nest"
#spinnVersion = -1
Random.seed(seed) # for all kinds of randomnesss

init()

CACells =  sim.Population(numberNeurons,sim.IF_cond_exp,cellparams={})
smallWorldToConnect(CACells)
CACells.record({'spikes','v'})

#Get Different Random Start Cells
for ignore in range (0,mixStart):
   ignoreRand = Random.randint(0,10)

spikeGenerator = createInput(5)
igniteCA(spikeGenerator,CACells,ignitingNeurons,0.1)


sys.stdout.write("Received start signal from robot.")
sys.stdout.flush()

runUntilThreshold(CACells)


#time.sleep(1) #left

CACells.write_data("CA.pkl",'spikes')

fileHandle = open("tempOut.txt",'a')
fileHandle.write(str(currentTime) + "\n")
fileHandle.close()

print (currentTime)
#print ("caught a left")


    

