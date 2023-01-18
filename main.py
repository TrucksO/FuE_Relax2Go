#!/usr/bin/python3
import numpy as np
import argparse
import datetime
import locale
import pyedflib
# defaults
separator = ';'
locale.setlocale(locale.LC_ALL, '')
decimalpoint = (locale.localeconv()['decimal_point'])
def signalsToCsv(filename, labels, signals):
    filename = filename+'.csv'
    with open(filename, 'w+') as f:
        labels_row = separator.join(labels)
        f.write(labels_row)
        # Get max samples length
        maxLength = 0
        for i in range(len(signals)):
            maxLength = max(maxLength, len(signals[i]))

def signalsToCsvs(filename, labels, signals, sampleRates, dimensions, stepwidth, startTime):
    for i in range(len(signals)):
        curTime = startTime
        filepath = filename+labels[i]+".csv"
        #filepath = filename+labels[i]+'_'+str(sampleRates[i])+'sps.csv'
        with open(filepath, 'w+') as f:
            #Labels
            if ("ECG" in labels[i]):
                f.write('%s%sTime[ms]%c%s\n' %
                        ('Uhrzeit', separator, separator, 'ECG'))
            else:
                f.write('%s%sTime[ms]%c%s\n' %
                        ('Uhrzeit', separator, separator, labels[i]))
            # Prepare time values
            absDelta = datetime.timedelta(seconds=stepwidth[i]/1000)
            print("adsfds" + str(absDelta))

            time = 0
            delta = stepwidth[i]# 1.0/sampleRates[i]    #ausgetauscht, damit in der Datei nachher die tatsächliche Zeit steht
            print(delta)
            print(filepath)
            # Samples saving
            for sample in signals[i]:
                text = '%s%c' % (curTime, separator)   #unnötige Zeile, weil ansonsten Pandas beim Konvertieren der Zeit irgendwie meckert...
                curTime += absDelta
                # DateTime to text
                if (args.timeAbsolute):
                    #print('Absolute')
                    # Absolute time used
                    text += '%s%c' % (time.strftime(
                        '%Y-%m-%d %H:%M:%S.%f'), separator)
                else:
                    #print('Relative')
                    # Relative time used
                    text += '%d%c' % (round(time,0), separator) #changed to %d (int) instead of %2.4f (float) to avoid problems with pandas
                time += delta
                # Sample to text
                text += str(sample)    #hier für Betrag abs() um das sample schreiben, wenn negative Werte gefiltert werden sollen
                # EOL
                text += '\n'
                # Decimal mark conversion of whole line
                text = text.replace(',', '.')
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
def main (filename):
    # Open EDF file
    filepath_in = 'data/raw/' + filename        #TODO: Pfad zur einzulesenden EDF-Datei
    filepath_out = 'data/converted/' + filename #TODO: Pfad, in dem die .csvs abgelegt werden sollen
    f = pyedflib.EdfReader(filepath_in)

    print(f.getSignalHeaders())

    print('(File) Opened', filepath_in)
    n = f.signals_in_file
    print('(File) %u signals in file.' % (n))
    labels = f.getSignalLabels()
    print('(File) Signal labels in file : ', labels)
    startTime = f.getStartdatetime()
    print('(File) Start of recording', startTime)
    sampleRates = f.getSampleFrequencies()
    signals = []
    dimensions = []
    stepwidth = []
    for i in np.arange(n):
        print('(Signal) Reading signal %u `%s`, sampling frequency %u, samples %u' % (
            i, labels[i], f.getSampleFrequency(i), f.getNSamples()[i]))
        print('(Signal) Signal header : ', f.getSignalHeader(i))
        print('')
        signal = f.readSignal(i)
        signals.append(signal)
        dimensions.append(f.getPhysicalDimension(i))
        print(f.datarecord_duration / f.getSampleFrequency(i))
        stepwidth.append(1000* f.datarecord_duration / f.getSampleFrequency(i)) #*1000 um Millisekunden zu bekommen
    # Create .csv
    print('Creation of .csv.')
    print (filepath_out)
    signalsToCsvs(filepath_out, labels, signals, sampleRates, dimensions, stepwidth, f.getStartdatetime())

raw_data = ['1.EDF', '2.EDF', '3.EDF', '4.EDF', '5.EDF', '6.EDF', '7.EDF', '8.EDF', '9.EDF', '10.EDF', '11.EDF',
            '12.EDF', '13.EDF', '14.EDF', '15.EDF']    #hier die Dateinamen eintragen, die transformiert werden sollen

for x in raw_data:
  main(x)