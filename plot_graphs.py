import os
import pickle
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd

RESULTPATH = 'data/results'
ANALYSISPATH = 'data/analysis'


def plot_operators_usage(d_count, d_best, r_count, r_best, ana_dir, filename, show=False):
    fig, (ax1, ax2) = plt.subplots(2, figsize=(7, 9))
    fig.suptitle(f'Mean # operator applied\n Mean # of bests applied\n{filename[8:-7]}',
                 fontsize=12)
    sub_titles = ['Removal operators', 'Repair operators']
    plt.subplots_adjust(hspace=0.3)
    sns.set_theme(style="white")
    for count, best, a, st in zip([d_count, r_count], [d_best, r_best], [ax1, ax2], sub_titles):
        ax_2 = a.twinx()

        std_label = count.std().tolist()
        a = sns.barplot(ax=a,
                        data=count.mean().to_frame().transpose(),
                        yerr=std_label)
        a.bar_label(a.containers[1])
        a.set_title(st)
        a.set_ylabel("Operator applied")
        a.set_xlabel("Operator name")

        sns.lineplot(ax=ax_2, data=best.mean().tolist(),
                     linestyle="-.",
                     marker="o",
                     color="salmon")
    plt.plot(output=os.path.join(ana_dir, "operators-bars.png"), show=show)
    plt.show()
    print("")


def plot_prize_iteration(y_val, filename, ana_dir, show=False):
    _, ax = plt.subplots(figsize=(9, 6))
    ordered_ex = dict(sorted(y_val.items()))
    ax = sns.lineplot(ax=ax, data=list(ordered_ex.values()))

    ax.set_title(f"Best prize values - {filename[8:-7]} - Value:{list(ordered_ex.keys())[0]}")
    ax.set_ylabel("Objective value")
    ax.set_xlabel("Temperature iteration (#)")

    ax.legend(["#1 best", "#2 best",
               "#3 best", "#4 best",
               "#5 best"], loc="upper right")
    plt.plot(output=os.path.join(ana_dir, "prize-iteration-lines.png"), show=show)
    print("")


def main():
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

        d_count_all = pd.DataFrame()
        d_best_all = list()
        r_count_all = pd.DataFrame()
        r_best_all = list()
        y_val = dict()
        for item in results:
            statistics = item['statistics']
            y_val[statistics.best_evaluations()[-1]] = statistics.best_evaluations()

            d_count = pd.DataFrame(statistics.destroy_operator_counts()).sum()
            d_count_all = d_count_all.append(d_count, ignore_index=True)
            d_best_all.append(statistics.destroy_operator_n_improvements())

            r_count = pd.DataFrame(statistics.repair_operator_counts()).sum()
            r_count_all = r_count_all.append(r_count, ignore_index=True)
            r_best_all.append(statistics.repair_operator_n_improvements())

        plot_prize_iteration(y_val, filename, ana_dir)

        plot_operators_usage(d_count_all, pd.DataFrame(d_best_all),
                             r_count_all, pd.DataFrame(r_best_all),
                             ana_dir,
                             filename)


if __name__ == '__main__':
    main()
