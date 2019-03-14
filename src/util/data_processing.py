import csv, glob, gc, pandas as pd, matplotlib.pyplot as plt, numpy as np
from numpy.polynomial.polynomial import polyfit
from scipy.signal import savgol_filter
from util import bat

def clean_graph(filename, graph=None, dy_cutoff=2000, dx_cutoff=.2, pulse_size=20):
    if graph is None:
        # Load file into 2d list
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            zc_str = list(reader)
    else:
        zc_str = graph

    zc_x, zc_y = graph[0], graph[1]

    # Identify pulses
    graph = list()
    pulse = list()
    prev_x = 0
    for x, y in zip(zc_x, zc_y):
        if x - prev_x <= dx_cutoff:
            pulse.append([x, y])
        elif len(pulse) < pulse_size:
            pulse = [[x, y]]
        else:
            graph.append(pulse)
            pulse = [[x, y]]
        prev_x = x

    # Get 1st derivative
    graph_dy = list()
    prev_y = 0
    for pulse in graph:
        dy = list()
        for x, y in pulse:
            dy.append(abs(y - prev_y))
            prev_y = y
        graph_dy.append(dy)

    # Smooth holes
    for dy, pulse in zip(graph_dy, graph):
        i = 1
        while i < (len(dy) - 2):
            if dy[i] > dy_cutoff:
                if dy[i - 1] < dy_cutoff:
                    if dy[i + 1] < dy_cutoff:
                        pulse[i][1] = (pulse[i - 1][1] + pulse[i + 1][1])/2
                    elif dy[i + 2] < dy_cutoff:
                        pulse[i][1] = (pulse[i - 1][1] + pulse[i + 2][1])/2
                elif dy[i - 2] < dy_cutoff:
                    if dy[i + 1] < dy_cutoff:
                        pulse[i][1] = (pulse[i - 2][1] + pulse[i + 1][1])/2
                    elif dy[i + 2] < dy_cutoff:
                        pulse[i][1] = (pulse[i - 2][1] + pulse[i + 2][1])/2
            i += 1

    # Clean pulses
    clean_graph = list()
    for k, pulse in enumerate(graph):
        i = 1
        while i < len(pulse):
            j = i

            # Count neighboring points
            while j < len(pulse) - 1 and graph_dy[k][j] <= dy_cutoff:
                j += 1

            # If there are enough neighbors, it's good
            if j - i >= pulse_size:
                clean_graph.append(pulse[i:j])

            i = j + 1

    # Distance functions
    def dist(ax, ay, bx, by):
        return np.sqrt((ax - bx)**2 + (ay - by)**2)

    def dista(pair):
        return dist(pair[0][0], pair[0][1], pair[1][0], pair[1][1])

    # Clean pulses more
    cleaner_graph = list()
    smooth_graph = list()
    for pulse in clean_graph:

        # Build smooth graph using Savitzky-Golay filter
        # Left param is all x values in current pulse, right param is smoothed y values
        # Params are zipped together then converted to list
        # This is the dark side of pythonic code
        smooth_pulse = list(zip([point[0] for point in pulse], savgol_filter([point[1] for point in pulse], 17, 3)))
        smooth_graph.extend(smooth_pulse)

        # Build clean pulse
        # Iterate through zipped list of smooth_pulse and pulse, producing [[ax, ay],[bx, by]]
        # Keep only those where the absolute distance between pair 1 and pair 2 is less than 1/2 dy_cutoff
        # This is the even darker side of pythonic code
        cleaner_graph.append([pair[0] for pair in zip(pulse, smooth_pulse) if dista(pair) < dy_cutoff / 2])

    return cleaner_graph

# fetch ZC file from GUI upload process located at indir
# output pulses as PNG images and place them in outdir
def zc_prc(indir, outdir):
    path = f'{indir}/**/*#'
    zc_files = glob.glob(path, recursive=True)

    # helper funtion for zc_prc
    # cleans data and extracts pulses, then saves those pulses into PNG images
    def extract_pulses(filename, outdir):
        data = bat.extract_anabat(filename)
        raw = list(data)
        pulses = clean_graph(filename=filename, graph=[raw[0], raw[1]])
        fig, ax = plt.subplots()

        for i, pulse in enumerate(pulses):
            x = [point[0] for point in pulse]
            y = [point[1] for point in pulse]
            plyft = polyfit(x=x, y=y, deg=1)
            classification = '/echolocation/' if plyft[1] < 0 else '/abnormal/'
            filename_split = filename.rsplit(".", 1)[0].rsplit("\\", 1)[-1]
            save_path = f'{outdir}{classification}{filename_split}_{i}.png'

            # create and save PNG files of pulses
            ax.axis('off')
            ax.scatter(x, y)
            fig.savefig(save_path, transparent=True, dpi=50)
            plt.cla()
            gc.collect()

    s = pd.Series(zc_files)
    s.apply(lambda filename: extract_pulses(filename, outdir))
