#!/usr/bin/python3
import numpy as np
import argparse
import datetime
import locale
import pyedflib
import pandas

# defaults
separator = ';'
locale.setlocale(locale.LC_ALL, '')
decimalpoint = (locale.localeconv()['decimal_point'])

def signalsToCsv(filename, labels, signals):
    ''' Export all signals to single .csv'''
    filename = filename+'.csv'
    with open(filename, 'w+') as f:
        labels_row = separator.join(labels)
        f.write(labels_row)

        # Get max samples length
        maxLength = 0
        for i in range(len(signals)):
            maxLength = max(maxLength, len(signals[i]))

        


def signalsToCsvs(filename, labels, signals, sampleRates, dimensions):
    ''' Export all signals to multiple .csv'''

    for i in range(len(signals)):
        laufvariable = 0
        filepath = filename+labels[i]+'_'+str(sampleRates[i])+'sps.csv'
        with open(filepath, 'w+') as f:
            # Labels
            f.write('Time[s]%c%s [%s]\n' %
                    (separator, labels[i], dimensions[i]))

            # Prepare time values
            if (args.timeAbsolute):
                time = startTime
                delta = datetime.timedelta(seconds=1.0/sampleRates[i])
            else:
                time = 0
                delta = 1.0/sampleRates[i]

            # Samples saving
            for sample in signals[i]:
                # DateTime to text
                if (args.timeAbsolute):
                    # Absolute time used
                    text = '%s%c' % (time.strftime(
                        '%Y-%m-%d %H:%M:%S.%f'), separator)
                else:
                    # Relative time used
                    text = '%2.4f%c' % (time, separator)
                if sample <= 0:
                    sample = abs(sample)
                time += delta
                # Sample to text

                text += str(sample)
                # EOL
                text += '\n'
                # Decimal mark conversion of whole line
                if (decimalpoint == ','):
                    text = text.replace('.', ',')




                # Save
                f.write(text)

# Arguments and config
# #####################################################
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', type=str, nargs='?', const='\Test_Proband.EDF',
                    required=False, help='Input EDF file')
parser.add_argument('-s', '--separator', type=str,
                    required=False, help='Data CSV separator')
parser.add_argument('-d', '--decimalpoint', type=str,
                    required=False, help='Decimal point character')
parser.add_argument('-t', '--timeAbsolute', action='store_true',
                    required=False, help='Default behaviour is relative time printing (First sample is 0s). Absolute time prints time according to record start time.')
args = parser.parse_args()

if (args.separator is not None):
    separator = args.separator

if (args.decimalpoint is not None):
    decimalpoint = args.decimalpoint

# Open EDF file
f = pyedflib.EdfReader('../Test_Oli.edf')
print('(File) Opened', '../Test_Oli.edf')
n = f.signals_in_file
print('(File) %u signals in file.' % (n))
labels = f.getSignalLabels()
print('(File) Signal labels in file : ', labels)
startTime = f.getStartdatetime()
print('(File) Start of recording', startTime)

sampleRates = f.getSampleFrequencies()
signals = []
dimensions = []
for i in np.arange(n):
    print('(Signal) Reading signal %u `%s`, sampling frequency %u, samples %u' % (
        i, labels[i], f.getSampleFrequency(i), f.getNSamples()[i]))
    print('(Signal) Signal header : ', f.getSignalHeader(i))
    print('')
    signal = f.readSignal(i)
    signals.append(signal)
    dimensions.append(f.getPhysicalDimension(i))

# Create .csv
print('Creation of .csv.asdfadsfadsf')
signalsToCsvs('4a35ced6-dd19-43f8-be74-59a854f87db7.EDF', labels, signals, sampleRates, dimensions)