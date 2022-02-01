import os
import pickle
import numpy as np
from matplotlib import pyplot as plt

from alns import utils


RESULTPATH = 'data/results'
ANALYSISPATH = 'data/analysis'


def main(show=False):
    for filename in os.listdir(RESULTPATH):
        file = os.path.join(RESULTPATH, filename)
        if not os.path.isfile(file):
            continue

        dir = ''.join(filename.split('.')[:-1])
        ana_dir = os.path.join(ANALYSISPATH, dir)
        if not os.path.exists(ana_dir):
            os.mkdir(ana_dir)

        result_dict = pickle.load(open(file, 'rb'))

        results = result_dict["results"]
        statistics = result_dict["statistics"]
        timing = result_dict["timing"]

        print(results[0]['best'].value)

        values = np.array(map(lambda x: x["best"].value, results))

        pos = results[0]['initial'].plot(
            output=os.path.join(ana_dir, f"initial.png"),
            title=f"Initial Solution\nValue: {results[0]['initial'].value}",
            show=show
        )
        for i, res in enumerate(results):
            for t in ['current', 'best']:
                res[t].plot(
                    pos=pos,
                    output=os.path.join(ana_dir, f"{t}-{i}.png"),
                    title=f"{t.capitalize()} Solution - Execution {i+1}\nValue: {res[t].value}",
                    show=show)


if __name__ == '__main__':
    main(False)