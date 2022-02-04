import os
import pickle
from time import time
import csv
import numpy as np

from matplotlib import pyplot as plt

from alns import utils
import alns.improvement as imp
from alns.solution_instance import SolutionInstance

RESULTPATH = 'data/results'
ANALYSISPATH = 'data/analysis'
HEADER = ['Instance', 'Result 1', 'Result 2', 'Result 3', 'Result 4', 'Result 5', 'Avg', 'Std', 'Avg time', 'Std time', 'Avg initial', 'Std initial']


def main(generate_img=False, show=False):
    rows = []
    for filename in os.listdir(RESULTPATH):
        file = os.path.join(RESULTPATH, filename)
        if not os.path.isfile(file):
            continue

        print(f"Analizing file: {file}")

        dir = ''.join(filename.split('.')[:-1])
        ana_dir = os.path.join(ANALYSISPATH, dir)
        if not os.path.exists(ana_dir):
            os.mkdir(ana_dir)

        result_dict = pickle.load(open(file, 'rb'))

        graphs = [g["best"] for g in result_dict["results"]]
        for graphs in result_dict["results"]:
            g = graphs["best"]
            for n in g.solution.nodes(data=True):
                g.solution.nodes[n[0]]["prize"] = g.instance.nodes[n[0]]["prize"]
                g.solution.nodes[n[0]]["terminal"] = g.instance.nodes[n[0]]["terminal"]
                
            G = imp.remove_leaves(g.solution)
            G = SolutionInstance(g.instance, G)
            graphs["best"] = G

        results = result_dict["results"]
        statistics = result_dict["statistics"]
        timing = result_dict["timing"]

        values = np.array(list(map(lambda x: x["best"].value, results)))
        initial_values = np.array(list(map(lambda x: x["initial"].value, results)))
        rows.append([
            dir,
            *values,
            np.mean(values),
            np.std(values),
            np.mean(timing),
            np.std(timing),
            np.mean(initial_values),
            np.std(initial_values)
        ])

        if not generate_img:
            continue

        pos = results[0]['initial'].plot(
            output=os.path.join(ana_dir, f"initial.png"),
            title=f"Initial Solution\nValue: {results[0]['initial'].value}",
            show=show
        )
        for i, res in enumerate(results):
            for t in ['current', 'best']:
                pos = res[t].plot(
                    pos=pos,
                    output=os.path.join(ana_dir, f"{t}-{i}.png"),
                    title=f"{t.capitalize()} Solution - Execution {i+1}\nValue: {res[t].value}",
                    show=show)
    
    with open(os.path.join(ANALYSISPATH, f'result-analysis-{int(time())}.csv'), 'w') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(HEADER)
        writer.writerows(rows)


if __name__ == '__main__':
    main(False, False)