# -*- coding: utf-8 -*-
'''
EXPOsan: Exposition of sanitation and resource recovery systems

This module is developed by:
    
    Joy Zhang <joycheung1994@gmail.com>

This module is under the University of Illinois/NCSA Open Source License.
Please refer to https://github.com/QSD-Group/EXPOsan/blob/main/LICENSE.txt
for license details.
'''

from qsdsan.utils import load_data, ospath
from exposan.metab_mock.let23 import (
    results_path, 
    figures_path,
    mc
     )
import numpy as np, pandas as pd
import matplotlib as mpl, matplotlib.pyplot as plt

mpl.rcParams['font.sans-serif'] = 'arial'
mpl.rcParams["figure.autolayout"] = False
mpl.rcParams['ytick.minor.visible'] = True

#%% metric data processing
def load_metrics(seed):
    slc = {}
    non = {}
    for i in 'ABCD':
        df = load_data(ospath.join(results_path, f'sys{i}_selective_table_{seed}.xlsx'),
                       index_col=0, header=[0,1])
        slc[i] = df.iloc[:,23:]
        df = load_data(ospath.join(results_path, f'sys{i}_nonselect_table_{seed}.xlsx'),
                       index_col=0, header=[0,1])
        non[i] = df.iloc[:,23:]

    metrics = {}
    iterables = [['selective', 'nonselect'], ['A','B','C','D']]
    for col in slc['A'].columns:
        l = [slc[i].loc[:,col] for i in 'ABCD'] \
            + [non[i].loc[:,col] for i in 'ABCD']
        metrics[col[1]] = pd.concat(l, axis=1, keys=pd.MultiIndex.from_product(iterables,
                                                                       names=['group', 'sys']))
    return metrics
    
#%% Boxplots of all UA results

idx = pd.IndexSlice
flierprops = dict(marker='.', markersize=1, markerfacecolor='#90918e', markeredgecolor='#90918e')
meanprops = dict(marker='^', markersize=2.5, markerfacecolor='black', markeredgecolor='black')
medianprops = dict(color='black')

def plot_dist(df, save_to=None):
    fig, axes = plt.subplots(1, 4, sharey=True, figsize=(5, 4))
    for i, sys in enumerate('ABCD'):
        ax = axes[i]
        data = df.loc[:, idx[:, sys]].to_numpy()
        left = data[:,0][~np.isnan(data[:,0])]
        right = data[:,1][~np.isnan(data[:,1])]
        ax.boxplot([left, right], showmeans=True, labels=['',''], 
                   flierprops=flierprops, meanprops=meanprops,
                   medianprops=medianprops)
        parts = ax.violinplot([left, right], showextrema=False)
        for p, c in zip(parts['bodies'], ('#60c1cf', '#F98F60')):
            p.set_facecolor(c)
            p.set_alpha(1)
        ax.tick_params(axis='y', which='both', direction='inout')
        ax.set_title(sys)
    fig.subplots_adjust(wspace=0)
    if save_to:
        fig.savefig(ospath.join(figures_path, save_to), dpi=300,
                    facecolor='white')
    else: return fig, axes

def plot_all_metrics(metrics):
    mpl.rcParams['xtick.minor.visible'] = False
    for k, df in metrics.items():
        var = k.split(" [")[0]
        plot_dist(df, f'{var}.png')

def plot_E_per_rCOD(metrics):
    mpl.rcParams['xtick.minor.visible'] = False
    E_use = - metrics['Net operation energy [kW]']/metrics['Hourly COD removal [kgCOD/hr]']
    fig, axes = plot_dist(E_use)
    metro_E = mc.E_model()
    p5, p25, p50, p75, p95 = np.percentile(metro_E, [5, 25, 50, 75, 95])
    fig, axes = plt.subplots(1, 4, sharey=True, figsize=(5, 4))
    clr = '#9c4b50'
    for i, sys in enumerate('ABCD'):
        ax = axes[i]
        ax.axhspan(p5, p95, color=clr, alpha=0.2, edgecolor=None)
        ax.axhspan(p25, p75, color=clr, alpha=0.2)
        ax.axhline(y=p50, color=clr, linewidth=0.5)
        data = E_use.loc[:, idx[:, sys]].to_numpy()
        left = data[:,0][~np.isnan(data[:,0])]
        right = data[:,1][~np.isnan(data[:,1])]
        ax.boxplot([left, right], showmeans=True, labels=['',''], 
                   flierprops=flierprops, meanprops=meanprops,
                   medianprops=medianprops)
        parts = ax.violinplot([left, right], showextrema=False)
        for p, c in zip(parts['bodies'], ('#60c1cf', '#F98F60')):
            p.set_facecolor(c)
            p.set_alpha(1)
        ax.tick_params(axis='y', which='both', direction='inout')
        ax.set_ylim(0, 10)
        ax.set_title(sys)
    fig.subplots_adjust(wspace=0)
    fig.savefig(ospath.join(figures_path, 'EprCOD'), dpi=300,
                facecolor='white')
    
    

#%% SA on sysC (non-selective) net operation energy (MCF)

import seaborn as sns
from math import ceil
from scipy.stats import kstest

def plot_cdf_bygroup(x_df, group, save_to):
    mpl.rcParams['xtick.minor.visible'] = True
    n_param = x_df.shape[1]
    ncol = 3
    nrow = ceil(n_param/ncol)
    fig, axes = plt.subplots(nrow, ncol, sharey=True, figsize=(ncol*2, nrow*2.5))
    for col, ax in zip(x_df, axes.ravel()):
        sns.ecdfplot(data=x_df, x=col, hue=group,  
                     palette=['#a280b9', '#f3c354'],
                     legend=False, ax=ax)
        ax.tick_params(axis='both', which='both', direction='inout')
        ax.set_xlabel('')
        ax.set_ylabel('')
    fig.subplots_adjust(hspace=0.4, wspace=0.05, bottom=0.2)
    fig.savefig(ospath.join(figures_path, save_to), dpi=300, facecolor='white')
    

def KStest(seed, yname, threshold, sys='sysC', scenario='nonselect', plot_save_to='cdf.png'):
    df = load_data(ospath.join(results_path, f'{sys}_{scenario}_table_{seed}.xlsx'),
                   index_col=0, header=[0,1])
    ys = df.xs(key=yname, axis=1, level='Feature').to_numpy()
    highx = df.loc[ys > threshold, idx[['Anaerobic CSTR-R1C', 'ADM1'], :]]
    lowx = df.loc[ys <= threshold, idx[['Anaerobic CSTR-R1C', 'ADM1'], :]]
    stats = {}
    sig_cols = []
    for col in highx.columns:
        x = col[1].split(' [')[0]
        D, p = kstest(highx.loc[:, col], lowx.loc[:, col])
        stats[x] = (D, p)
        if p < 0.05: sig_cols.append(col)
    group = ['high']*highx.shape[0] + ['low']*lowx.shape[0]
    xs = pd.concat([highx, lowx])[sig_cols]
    plot_cdf_bygroup(xs, group, plot_save_to)
    return stats, sig_cols

#%%
if __name__ == '__main__':
    seed = 123
    yname = 'Net operation energy [kW]'
    metrics = load_metrics(seed)
    plot_all_metrics(metrics)
    plot_E_per_rCOD(metrics)
    stats, sig_xs = KStest(seed, yname, threshold=-1.15)
