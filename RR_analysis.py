# system imports
import os
import sys

# data science
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import seaborn as sns

# signal processing
from scipy import signal
from scipy.ndimage import label
from scipy.stats import zscore
from scipy.interpolate import interp1d
from scipy.integrate import trapz

# physionet data
import wfdb
from wfdb import processing


def analyze(filepath_in, filepath_out, file):

    # path settings
    project_path = os.path.join(os.getcwd(), os.pardir)
    #data_path = os.path.join(project_path, 'data\\raw')
    output_path = os.path.join(project_path, 'output')

    # style settings
    sns.set(style='whitegrid', rc={'axes.facecolor': '#EFF2F7'})

    # sample frequency for Bobbi sensor
    settings = {}
    settings['fs'] = 500


    def get_plot_ranges(start=10, end=20, n=5):
        '''
        Make an iterator that divides into n or n+1 ranges.
        - if end-start is divisible by steps, return n ranges
        - if end-start is not divisible by steps, return n+1 ranges, where the last range is smaller and ends at n

        # Example:
        >> list(get_plot_ranges())
        >> [(0.0, 3.0), (3.0, 6.0), (6.0, 9.0)]

        '''
        distance = end - start
        for i in np.arange(start, end, np.floor(distance / n)):
            yield (int(i), int(np.minimum(end, np.floor(distance / n) + i)))

    def group_peaks(p, threshold=5):
        '''
        The peak detection algorithm finds multiple peaks for each QRS complex.
        Here we group collections of peaks that are very near (within threshold) and we take the median index
        '''
        # initialize output
        output = np.empty(0)

        # label groups of sample that belong to the same peak
        peak_groups, num_groups = label(np.diff(p) < threshold)

        # iterate through groups and take the mean as peak index
        for i in np.unique(peak_groups)[1:]:
            peak_group = p[np.where(peak_groups == i)]
            output = np.append(output, np.median(peak_group))
        return output


    def detect_peaks(ecg_signal, threshold=0.3, qrs_filter=None):
        '''
        Peak detection algorithm using cross corrrelation and threshold
        '''
        if qrs_filter is None:
            # create default qrs filter
            t = np.linspace(1.5 * np.pi, 3.5 * np.pi, 15)
            qrs_filter = np.sin(t)

        # normalize data
        ecg_signal = (ecg_signal - ecg_signal.mean()) / ecg_signal.std()

        # calculate cross correlation
        similarity = np.correlate(ecg_signal, qrs_filter, mode="same")
        similarity = similarity / np.max(similarity)

        # return peaks (values in ms) using threshold
        return ecg_signal[similarity > threshold].index, similarity

    # data recorded with the Bobbi sensor
    df = pd.read_csv(filepath_in + file, sep=";", index_col="Time[ms]", decimal=".")
    #df.index.astype(int)
    #df.index = pd.to_numeric(df.index, downcast='integer')

    '''plt.figure(figsize=(40, 10))
    start = 0
    stop = 5000
    duration = (stop-start) / settings['fs']
    plt.title("ECG signal, slice of %.1f seconds" % duration, fontsize=24)
    plt.plot(df[start:stop].index, df[start:stop].ECG, color="#51A6D8", linewidth=1) #ToDO: ECG1 ersetzen durch "EKG" oder anderen guten Schlüssel (und Transformationsfunktion entsprechend anpassen!)
    plt.xlabel("Time (ms)", fontsize=16)
    plt.ylabel("Amplitude (arbitrary unit)", fontsize=16)'''

    #plt.show() #auskommentiert - wieder reinnehmen, wenn man sich die Daten mal kurz visuell anschauen will

    sampfrom = 60000
    sampto = 70000
    nr_plots = 1

    '''for start, stop in get_plot_ranges(sampfrom, sampto, nr_plots):
        # get slice data of ECG data
        cond_slice = (df.index >= start) & (df.index < stop)
        ecg_slice = df.ECG[cond_slice]     #ToDO: ECG1 ersetzen durch "EKG" oder anderen guten Schlüssel (und Transformationsfunktion entsprechend anpassen!)

        # detect peaks
        peaks, similarity = detect_peaks(ecg_slice, threshold=0.3)

        # plot similarity
        plt.figure(figsize=(40, 20))

        plt.subplot(211)
        plt.title("ECG signal with found peaks", fontsize=24)
        plt.plot(ecg_slice.index, ecg_slice, label="ECG", color="#51A6D8", linewidth=1)
        plt.plot(peaks, np.repeat(600, peaks.shape[0]), markersize=10, label="peaks", color="orange", marker="o",
                 linestyle="None")
        plt.legend(loc="upper right", fontsize=20)
        plt.xlabel("Time (milliseconds)", fontsize=16)
        plt.ylabel("Amplitude (arbitrary unit)", fontsize=16)

        plt.subplot(212)
        plt.title('Similarity with QRS template', fontsize=24)
        plt.plot(ecg_slice.index, similarity, label="Similarity with QRS filter", color="olive", linewidth=1)
        plt.legend(loc="upper right", fontsize=20)
        plt.xlabel("Time (milliseconds)", fontsize=16)
        plt.ylabel("Similarity (normalized)", fontsize=16)

        #plt.savefig("data/raw/peaks2-%s-%s.png" % (start, stop))
        '''


    # detect peaks
    peaks, similarity = detect_peaks(df.ECG, threshold=0.3)

    # group peaks
    grouped_peaks = group_peaks(peaks)
    '''
    # plot peaks
    plt.figure(figsize=(40, 10))
    plt.title("Group similar peaks together", fontsize=24)
    plt.plot(df.index, df.ECG, label="ECG", color="#51A6D8", linewidth=2)
    plt.plot(peaks, np.repeat(600, peaks.shape[0]), markersize=10, label="peaks", color="orange", marker="o", linestyle="None")
    plt.plot(grouped_peaks, np.repeat(620, grouped_peaks.shape[0]), markersize=12, label="grouped peaks", color="k", marker="v", linestyle="None")
    plt.legend(loc="upper right", fontsize=20)
    plt.xlabel("Time (ms)", fontsize=16)
    plt.ylabel("Amplitude (arbitrary unit)", fontsize=16)
    plt.gca().set_xlim(0, 200)
    '''
    # detect peaks
    peaks, similarity = detect_peaks(df.ECG, threshold=0.01)    #TODO: Ich vermute man muss mit der Threshold spielen, um Peaks rauszubekommen

    # group peaks so we get a single peak per beat (hopefully)
    grouped_peaks = group_peaks(peaks)

    # RR-intervals are the differences between successive peaks
    rr = np.diff(grouped_peaks)
    '''
    # plot RR-intervals
    plt.figure(figsize=(40, 15))
    plt.title("RR-intervals", fontsize=24)
    plt.xlabel("Time (ms)", fontsize=16)
    plt.ylabel("RR-interval (ms)", fontsize=16)

    plt.plot(np.cumsum(rr), rr, label="RR-interval", color="#A651D8", linewidth=2)
    '''
    '''
    das geht jetzt auf https://github.com/stetelepta/exploring-heart-rate-variability/blob/master/notebooks/blogpost-exploring-hrv.ipynb
    bis einschließlich In[10]
    '''
    #plt.close()

    #In11 Artifact removal
    '''plt.figure(figsize=(40, 10))
    plt.title("Distribution of RR-intervals", fontsize=24)'''
    sns.kdeplot(rr, label="rr-intervals", color="#A651D8", fill=True)

    outlier_low = np.mean(rr)-2 * np.std(rr)
    outlier_high = np.mean(rr)+2 * np.std(rr)
    '''
    plt.axvline(x=outlier_low)
    plt.axvline(x=outlier_high, label="outlier boundary")
    plt.text(outlier_low - 270, 0.004, "outliers low (< mean - 2 sigma)", fontsize=20)
    plt.text(outlier_high + 20, 0.004, "outliers high (> mean + 2 sigma)", fontsize=20)

    plt.xlabel("RR-interval (ms)", fontsize=16)
    plt.ylabel("Density", fontsize=16)

    plt.legend(fontsize=24)

    plt.figure(figsize=(40, 15))
    '''
    #In12
    rr_corrected = rr.copy()
    rr_corrected[np.abs(zscore(rr)) > 2] = np.median(rr)
    '''
    plt.title("RR-intervals", fontsize=24)
    plt.xlabel("Time (ms)", fontsize=16)
    plt.ylabel("RR-interval (ms)", fontsize=16)

    plt.plot(rr, color="red", linewidth=1, label="RR-intervals")
    plt.plot(rr_corrected, color="green", linewidth=2, label="RR-intervals after correction")
    plt.legend(fontsize=20)

    #plt.show()

    #In19 Plot ECG vs RR intervals
    sampfrom = 200000
    sampto = 300000
    nr_plots = 10
    '''
    # detect peaks
    peaks, similarity = detect_peaks(df.ECG, threshold=0.3)

    # group peaks so we get a single peak per beat (hopefully)
    grouped_peaks = group_peaks(peaks)

    # RR-intervals are the differences between successive peaks
    rr = np.diff(grouped_peaks)
    '''
    for start, stop in get_plot_ranges(sampfrom, sampto, nr_plots):
        # plot similarity
        plt.figure(figsize=(40, 20))

        plt.title("ECG signal & RR-intervals", fontsize=24)
        plt.plot(df.index, df.ECG, label="ECG", color="#51A6D8", linewidth=1)
        plt.plot(grouped_peaks, np.repeat(600, grouped_peaks.shape[0]), markersize=14, label="Found peaks", color="orange",
                 marker="o", linestyle="None")
        plt.legend(loc="upper left", fontsize=20)
        plt.xlabel("Time (milliseconds)", fontsize=16)
        plt.ylabel("Amplitude (arbitrary unit)", fontsize=16)
        plt.gca().set_ylim(400, 800)

        ax2 = plt.gca().twinx()
        ax2.plot(np.cumsum(rr) + peaks[0], rr, label="RR-intervals", color="#A651D8", linewidth=2,
                 markerfacecolor="#A651D8", markeredgewidth=0, marker="o", markersize=18)
        ax2.set_xlim(start, stop)
        ax2.set_ylim(-2000, 2000)
        ax2.legend(loc="upper right", fontsize=20)

        plt.xlabel("Time (ms)", fontsize=16)
        plt.ylabel("RR-interval (ms)", fontsize=16)

        #plt.savefig("data/raw/ecg-with-rr-%s-%s.png" % (start, stop))

        #plt.show()
    plt.close()
    '''
    np.savetxt(filepath_out + file + '_rr.txt', rr_corrected, fmt='%d')

filepath_in = 'data/converted/' #TODO: Pfad zur einzulesenden .csv
filepath_out = 'data/analyzed/' #TODO: Pfad, in dem die .txts mit den RR-Werten abgelegt werden sollen

files = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']

for i in range (1, 4):
    for x in files:
        print(str(x+'.EDFECG'+str(i)+'.csv'))
        analyze(filepath_in, filepath_out, x+'.EDFECG'+str(i)+'.csv')
        #analyze(filepath_in, filepath_out, '03bla.EDFECG1_12sps.csv')