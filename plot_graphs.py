import os
import pickle
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
from operator import itemgetter

RESULTPATH = 'data/results'
ANALYSISPATH = 'data/analysis'


def plot_operators_usage(d_count, d_best, r_count, r_best, ana_dir, filename, show=True):
    fig, (ax1, ax2) = plt.subplots(2, figsize=(10, 9))
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
    # plt.show()
    fig.savefig(os.path.join(ana_dir, f"{filename}prize-operators-usage.png"))
    print("")


def plot_operators_weight(d_weights, r_weights, ana_dir, filename):
    fig, (ax, ax2) = plt.subplots(2, figsize=(10, 9))
    fig.suptitle(f'Weight of operators \n Mean # of bests applied\n{filename[8:-7]}',
                 fontsize=12)
    sub_titles = ['Removal operators', 'Repair operators']
    plt.subplots_adjust(hspace=0.3)
    sns.set_theme(style="white")
    for weights, a, st in zip([d_weights, r_weights], [ax, ax2], sub_titles):
        sns.lineplot(ax=a, data=pd.DataFrame(weights).to_dict('list'))
        a.set_title(st)
        a.set_ylabel("Operator weight")
        a.set_xlabel("Temperature iteration")

    # plt.show()
    fig.savefig(os.path.join(ana_dir, f"{filename}-operators-weight.png"))
    print("")


def plot_prize_iteration(y_val, filename, ana_dir, show=True):
    fig, ax = plt.subplots(figsize=(9, 6))
    ordered_ex = sorted(y_val, key=itemgetter(-1))
    ax = sns.lineplot(ax=ax, data=ordered_ex)

    ax.set_title(f"Best prize values - {filename[8:-7]} - Value:{ordered_ex[0][-1]}")
    ax.set_ylabel("Objective value")
    ax.set_xlabel("Temperature iteration (#)")
    ax.legend([f"#{i} best" for i in range(1, len(ordered_ex) + 1)], loc="upper right")
    # plt.show()
    fig.savefig(os.path.join(ana_dir, f"{filename}prize-iteration-lines.png"))
    print("")


def main():
    for filename in os.listdir(RESULTPATH):
        file = os.path.join(RESULTPATH, filename)
        if not os.path.isfile(file):
            continue

        # dir = ''.join(filename.split('.')[:-1])
        ana_dir = os.path.join(ANALYSISPATH)
        if not os.path.exists(ana_dir):
            os.mkdir(ana_dir)

        result_dict = pickle.load(open(file, 'rb'))

        results = result_dict["results"]

        d_count_all = pd.DataFrame()
        d_best_all = list()
        r_count_all = pd.DataFrame()
        r_best_all = list()
        y_val = list()
        already_plotted_weights = False
        for item in results:
            statistics = item['statistics']
            y_val.append(statistics.best_evaluations())

            d_count = pd.DataFrame(statistics.destroy_operator_counts()).sum()
            d_count_all = d_count_all.append(d_count, ignore_index=True)
            d_best_all.append(statistics.repair_operator_n_improvements())

            r_count = pd.DataFrame(statistics.repair_operator_counts()).sum()
            r_count_all = r_count_all.append(r_count, ignore_index=True)
            r_best_all.append(statistics.destroy_operator_n_improvements())

            if not already_plotted_weights:
                plot_operators_weight(statistics.destroy_operator_weights(),
                                      statistics.repair_operator_weights(), ana_dir,
                                      filename)
                already_plotted_weights = True
        plot_prize_iteration(y_val, filename, ana_dir)

        plot_operators_usage(d_count_all, pd.DataFrame(d_best_all),
                             r_count_all, pd.DataFrame(r_best_all),
                             ana_dir,
                             filename)


if __name__ == '__main__':
    main()
