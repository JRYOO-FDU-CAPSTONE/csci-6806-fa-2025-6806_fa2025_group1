#!/usr/bin/env python

import datetime
import glob
import os
import pickle
import platform
import random
import sys
import time
import traceback
from collections import Counter
from importlib import reload
from pathlib import Path
from pprint import pprint

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns
from IPython.display import HTML, display
from tqdm.notebook import tqdm  # or use tqdm.tqdm for non-notebook

# Add project to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Core simulation modules
# import seaborn as sns
import os
from importlib import reload

import pandas as pd
from IPython.display import HTML, display

from BCacheSim import cachesim, episodic_analysis
from BCacheSim.cachesim import dynamic_features as dfeature
from BCacheSim.cachesim import utils
from BCacheSim.cachesim.sim_cache import Timestamp, _lookup_episode

# Episodic analysis modules
from BCacheSim.episodic_analysis import (
    adaptors,
    ep_utils,
    episodes,
    experiments,
    local_cluster,
    policies,
    trace_utils,
)
from BCacheSim.episodic_analysis import monitor_exps as monitor
from BCacheSim.episodic_analysis.ep_utils import flatten
from BCacheSim.episodic_analysis.episodes import Episode
from BCacheSim.episodic_analysis.exps import factory as ef
from BCacheSim.episodic_analysis.exps import results
from BCacheSim.episodic_analysis.monitor_exps import filter_df_dct

# Plotting modules
from BCacheSim.episodic_analysis.plotting import (
    contexts,
    loader,
    maps,
    processors,
    styles,
)
from BCacheSim.episodic_analysis.plotting.maps import add_fig_label

result_cols = [
    "AP Threshold",
    "Avg Eviction Age (s)",
    "Write Rate (MB/s)",
    "ServiceTimeSavedRatio",
    "ServiceTimeSavedRatio1",
    "IOPSSavedRatio",
]

display(HTML("<style>.container { width:100% !important; }</style>"))

reload(monitor)
filter_df = monitor.filter_df_dct

os.environ["SOURCE_DATE_EPOCH"] = "1631030919"
pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 1000)
pd.set_option("display.max_colwidth", None)
import matplotlib.pyplot as plt

filter_df = filter_df_dct
# add_fig_label, etc is inside
from BCacheSim.episodic_analysis.plotting import contexts, styles

filter_df = filter_df_dct
# add_fig_label, etc is inside
from BCacheSim.episodic_analysis.plotting import contexts, styles

contexts.use("wide")
# Used by results
from BCacheSim.episodic_analysis.plotting import loader, processors

COLS = [
    "ShortLabel",
    "RegionLabel",
    maps.l_wr,
    "P100ServiceTimeUtil@10m",
    "P99.9ServiceTimePercent1",
    "P99.9ServiceTimeUtil@10m",
    "P99ServiceTimeUtil@10m",
    "P50ServiceTimeUtil@10m",
    "AP Threshold",
    "Assumed Eviction Age (s)",
    "Converged",
    "Iteration",
    "SampleStart",
    "SampleRatio",
    "Trace",
    "ExperimentName",
    "Filename",
]

savefig = maps.savefig


def load_df(filename):
    dfc_raw_old = pd.read_csv(filename, low_memory=False)
    dfc_raw_old["Target Write Rate"] = pd.to_numeric(
        dfc_raw_old["Target Write Rate"], errors="coerce"
    )
    dfc_raw_old["TraceGroup"] = dfc_raw_old["TraceGroup"].astype("str")
    return dfc_raw_old


def combine_dfs(*args):
    return pd.concat(args).copy()


l_ST = "DT"
reload(maps)


def get_df(filename="../../data/results_release.csv.gz"):
    dfc_raw_ = pd.read_csv(f"{filename}", low_memory=False)
    dfc_raw_["TraceGroup"] = dfc_raw_["TraceGroup"].astype("str")
    dfc_raw_["Target Cache Size (TB)"] = dfc_raw_["Target Cache Size"] / 1000
    try:
        dfc_raw_, _ = maps.postproc(dfc_raw_)
    except:
        print("postproc failed")
        raise
    # dfc_raw_ = proc_canon(dfc_raw_)
    return dfc_raw_


def get_data(
    dfc_raw_=None,
    default_sample_ratio=0.1,
    default_cl_o_ratio=1,
    default_sc_ratio=5,
    verbose=0,
    skipna=True,
    star_y="P100ServiceTimeUtil@10m",
):
    dfc_raw_ = dfc_raw_ if dfc_raw_ is not None else get_df()
    common_filter = {
        "CanonExp": True,
        "DWPDNotFar": True,
        "Target Cache Size": ef.DEFAULT_CSIZE,
        "Trace": [
            "201910/Region1",
            "201910/Region3",
            "201910/Region2",
            "202110/Region4",
            "20230325/Region7",
            "20230325/Region6",
            "20230325/Region5",
        ],
    }
    df_exp = filter_df(dfc_raw_, common_filter)

    df_cl = filter_df(
        dfc_raw_,
        {
            "Target Cache Size": ef.DEFAULT_CSIZE,
            "DWPDNotFar": True,
            "Region": ["Region1"],
            "SampleRatio": default_cl_o_ratio,
        },
    )
    df_o = filter_df(
        dfc_raw_,
        {
            "Target Cache Size": ef.DEFAULT_CSIZE,
            "DWPDNotFar": True,
            "Region": ["Region2"],
            "SampleRatio": default_cl_o_ratio,
        },
    )
    df_sc = filter_df(
        dfc_raw_,
        {
            "Target Cache Size": ef.DEFAULT_CSIZE,
            "DWPDNotFar": True,
            "Region": ["Region3"],
            "SampleRatio": default_sc_ratio,
        },
    )
    df_rest = df_exp[
        (df_exp["Region"] != "Region1")
        & (df_exp["Region"] != "Region3")
        & (df_exp["Region"] != "Region2")
    ]
    print(len(df_rest))
    df_rest = filter_df(df_rest, {"SampleRatio": default_sample_ratio})
    assert df_rest["SampleRatio"].nunique() == 1
    df_exp_sampledright = pd.concat([df_cl, df_sc, df_o, df_rest])
    df_exp_for_star = filter_df(df_exp_sampledright, {"PracticalAP": True})

    df_exp34 = filter_df(df_exp_sampledright, {"Target DWPD": 7.5})
    df_exp34_for_star = filter_df(df_exp_for_star, {"Target DWPD": 7.5})

    df_star34 = add_pfbest(df_exp34_for_star, y=star_y, verbose=verbose, skipna=skipna)
    df_exp34_all = pd.concat([df_exp34, df_star34])
    df_exp34_for_plot = filter_df(
        df_exp34_all,
        {
            "ShortLabel": [
                "RejectX",
                "CoinFlip",
                "NoEps-ML",
                "Baleen (No Prefetch)",
                "Baleen",
            ],
            "PracticalAP": True,
        },
        use_glob=False,
    )
    df_exp34_for_cmp = filter_df(
        df_exp34_all,
        {
            "ShortLabel": [
                "RejectX",
                "CoinFlip",
                "NoEps-ML",
                "Baleen (No Prefetch)",
                "Baleen",
                "Baleen (ML Prefetch)",
                "Baleen (ML-Range on Partial Hit)",
                "Baleen (All on Partial Hit)",
                "OPT AP (OPT Prefetch)",
            ],
        },
        use_glob=False,
    )

    df_star = add_pfbest(
        df_exp_for_star,
        y=star_y,
        columns=["Region", "Target DWPD"],
        verbose=verbose,
        skipna=True,
    )
    df_all = pd.concat([df_exp_sampledright, df_star])
    df_exp_for_plot = filter_df(
        df_all,
        {
            "ShortLabel": [
                "RejectX",
                "CoinFlip",
                "NoEps-ML",
                "Baleen (No Prefetch)",
                "Baleen",
            ],
            "PracticalAP": True,
        },
        use_glob=False,
    )
    df_exp_for_cmp = filter_df(
        df_all,
        {
            "ShortLabel": [
                "RejectX",
                "CoinFlip",
                "NoEps-ML",
                "Baleen (No Prefetch)",
                "Baleen",
                "Baleen (ML Prefetch)",
                "OPT AP (OPT Prefetch)",
            ],
        },
        use_glob=False,
    )

    return {
        "raw": dfc_raw_,
        "exp_": df_exp_sampledright,
        # 'exp': df_exp_sampledright,
        "exp": df_all,
        "exp_canon": df_exp_for_plot,
        "exp_cmp": df_exp_for_cmp,
        "exp34": df_exp34_all,
        "exp34_canon": df_exp34_for_plot,
        "exp34_cmp": df_exp34_for_cmp,
    }


def latex_macros(dct, suffix="\%"):
    for k, v in dct.items():
        print("\\newcommand{{\{}}}{{{:.1f}{}}}".format(k, v, suffix))


def add_pfbest(
    df_summary,
    y,
    order=None,
    idx=["ShortLabel"],
    columns=["Region"],
    verbose=1,
    skipna=True,
):
    """Pick best option for each Region"""
    dcz = monitor.filter_df_dct(df_summary, {"PracticalAP": True})
    # dcz = sampleright(dcz, idx=['ShortLabel', 'AdmissionPolicyLabel', 'Prefetching', 'Target Write Rate', 'Target DWPD'])
    dfs_real = pd.pivot_table(
        dcz, values=[y], index=["AdmissionPolicyLabel", "Prefetching"], columns=columns
    )
    # TODO: Check explicitly for the prefetching options we expect?
    if verbose >= 2:
        display(dfs_real)
    best_pf_option = dfs_real.reset_index(0).groupby("AdmissionPolicyLabel")
    if "Saved" in y:
        best_pf_option_ = best_pf_option.idxmax(skipna=skipna)
        best_pf_option = best_pf_option.max()
    else:
        best_pf_option_ = best_pf_option.idxmin(skipna=skipna)
        best_pf_option = best_pf_option.min()
    if verbose >= 2:
        display(best_pf_option)
        display(best_pf_option_)

    rows = []
    dqr = best_pf_option_[y]
    for i in range(len(columns)):
        dqr = dqr.stack()
    for hdr, bestpf in dqr.items():
        ap = hdr[0]
        filter_ = {"AdmissionPolicyLabel": ap, "Prefetching": bestpf}
        for i, col in enumerate(columns):
            filter_[col] = hdr[-1 - i]
        bestz = monitor.filter_df_dct(dcz, filter_)
        bestz["ShortLabel"] = bestz["AdmissionPolicyLabel"] + (
            "*" if ap != "Baleen" else ""
        )
        bestz["PlotLabel"] = bestz["AdmissionPolicyLabel"] + "*"
        rows.append(bestz)
    return pd.concat(rows)


reload(maps)


def plot_bar(
    df_,
    y=None,
    hue="ShortLabel",
    max_y=None,
    max_wr=80,
    regions=maps.REGIONS_CANON,
    points=False,
    legend=True,
    **kwargs,
):
    assert len(df_)
    df_ = df_.reset_index(drop=True)
    if regions is not None:
        df_ = df_[df_["Region"].isin(regions)]
    if hue == "ShortLabel":
        if all(k in maps.SHORT_COLORMAP for k in df_[hue]):
            kwargs["palette"] = maps.SHORT_COLORMAP
            kwargs["hue_order"] = [
                k for k in maps.SHORT_COLORMAP.keys() if k in df_["ShortLabel"].values
            ]
        else:
            print("Missing - not using SHORT_COLORMAP")
            print(set([k for k in df_[hue] if k not in maps.SHORT_COLORMAP]))
            # print({k: k in maps.SHORT_COLORMAP for k in df_[hue]})
    else:
        if all(k in maps.DEFAULT_COLORMAP for k in df_[hue]):
            kwargs["palette"] = maps.DEFAULT_COLORMAP
            kwargs["hue_order"] = [
                k for k in maps.DEFAULT_COLORMAP.keys() if k in df_["PlotLabel"].values
            ]

    if points:
        sns.stripplot(
            data=df_,
            y=y,
            x="RegionLabel",
            hue=hue,
            dodge=True,
            jitter=True,
            legend=False,
            size=15,
            marker="$\circ$",
            zorder=0,
            **kwargs,
        )
    g = sns.barplot(
        data=df_,
        x="RegionLabel",
        order=[maps.region_labels[x] for x in regions],
        y=y,
        hue=hue,
        linewidth=3,
        # elinewidth=2,
        errwidth=2.5,
        capsize=0.03,
        **kwargs,
    )
    if points:
        for patch in g.patches:
            clr = patch.get_facecolor()
            patch.set_edgecolor(clr)
            patch.set_facecolor((0, 0, 0, 0))

    if regions is None or len(regions) >= 3:
        plt.xticks(rotation=90)
    if legend:
        g.get_legend().set_title(None)
        plt.legend(frameon=True, loc="lower right")

    ax = plt.gca()
    plt.xlabel("Trace")
    y = nice_ylabel(y)
    plt.ylabel(y, loc="top")
    plt.grid(True, axis="y")


figlabels = {
    "peak-st-util": "P100ServiceTimeUtil@10m",
    "median-st-util": "P50ServiceTimeUtil@10m",
    "mean-st-util": "MeanServiceTimeUtil",
    "peak-st-ratio": "P100ServiceTimePercent@10m",
    "median-st-ratio": "P50ServiceTimePercent@10m",
    "mean-st-ratio": "MeanServiceTimeUsedPercent",
    "iops-miss-ratio": maps.l_iop_f,
    "bw-miss-ratio": maps.l_bw_f,
}
niceylabel = {
    "P100ServiceTimeUtil@10m": "Peak Backend Load (%)",
    "P50ServiceTimeUtil@10m": "Median Backend Load (%)",
    "MeanServiceTimeUtil": "Mean Backend Load (%)",
    "P100ServiceTimePercent@10m": "Peak Backend Load\n(% of no cache)",
    "P50ServiceTimePercent@10m": "Median Backend Load\n(% of no cache)",
    "MeanServiceTimeUsedPercent": "Mean Backend Load\n(% of no cache)",
    maps.l_iop_f: maps.l_iop_f,
    maps.l_bw_f: maps.l_bw_f,
}


def nice_ylabel(y):
    if y in niceylabel:
        y = niceylabel[y]
    elif "ServiceTime" in y and "@" in y:
        ptile, dg = y.split("ServiceTime")
        metric, window = dg.split("@")
        y = f"ST {metric} (%)\n({ptile} @ {window})"
    return y


def sampleright(
    df_,
    idx=["ShortLabel", "AdmissionPolicyLabel", "Prefetching"],
    all_ys=[maps.l_wr, "DWPD"],
    verbose=0,
):
    cols = all_ys + [
        c
        for c in df_.columns
        if (c.startswith("P") and "@" in c)
        or c.startswith("MeanServiceTime")
        or ("Ratio" in c and c != "SampleRatio")
        or "%" in c
    ]
    if verbose > 0:
        print(len(df_))
    df_ = (
        df_.groupby(idx + ["Region", "RegionLabel", "SampleRatio", "SampleStart"])[cols]
        .mean()
        .reset_index()
    )
    if verbose > 0:
        print(len(df_))
    df_ = (
        df_.groupby(idx + ["Region", "RegionLabel", "SampleRatio"])[cols]
        .mean()
        .reset_index()
    )
    if verbose > 0:
        print(len(df_))
    df_ = df_.groupby(idx + ["Region", "RegionLabel"])[cols].mean().reset_index()
    if verbose > 0:
        print(len(df_))
    return df_


def get_kwargs(df_, y, hue="ShortLabel", errs=True):
    kwargs = dict(
        hue=hue,
        style=hue,
        markers=True,
        dashes=False,
    )
    if errs:
        kwargs.update(
            dict(
                err_kws=dict(capsize=10),
                linewidth=3,
                err_style="bars",
            )
        )
    if hue == "ShortLabel":
        if all(k in maps.SHORT_COLORMAP for k in df_[hue]):
            kwargs["palette"] = maps.SHORT_COLORMAP
            kwargs["hue_order"] = [
                k for k in maps.SHORT_COLORMAP.keys() if k in df_["ShortLabel"].values
            ]
        else:
            print("Missing - not using SHORT_COLORMAP")
            print(set([k for k in df_[hue] if k not in maps.SHORT_COLORMAP]))
        if all(k in maps.SHORT_MARKERMAP for k in df_[hue]):
            kwargs["markers"] = maps.SHORT_MARKERMAP
        else:
            print("Missing - not using SHORT_MARKERMAP")
            print(set([k for k in df_[hue] if k not in maps.SHORT_MARKERMAP]))
    else:
        if all(k in maps.DEFAULT_COLORMAP for k in df_[hue]):
            kwargs["palette"] = maps.DEFAULT_COLORMAP
            kwargs["hue_order"] = [
                k for k in maps.DEFAULT_COLORMAP.keys() if k in df_["PlotLabel"].values
            ]
    return kwargs


def postplot(df_, target=True, target_v=None, targetlabel=True, figlabel=True):
    ax = plt.gca()

    if ax.get_legend():
        ax.legend()
        # g.get_legend().set_title(None)

    ax.set_ylim(0, None)
    ax.set_xlim(0, None)
    y = ax.get_ylabel()
    y = nice_ylabel(y)
    ax.set_ylabel(y, loc="top")
    fig_labels = []
    if "SampleRatio" in df_.columns:
        if df_["SampleRatio"].nunique() == 1:
            fig_labels.append(f"{df_['SampleRatio'].unique()[0]:g}%")
        else:
            print("Multiple SampleRatio:", df_["SampleRatio"].unique())
    if "RegionLabel" in df_.columns:
        if df_["RegionLabel"].nunique() == 1:
            fig_labels.append(str(df_["RegionLabel"].unique()[0]))
    if fig_labels and figlabel:
        add_fig_label(", ".join(fig_labels))
    if target:
        ax.axvline(target_v, ls=":", c="black")
    if targetlabel:
        maps.add_target_label(twr=target_v, fmt="3 DWPD")


import matplotlib.ticker as ticker


def add_leg_to_subplot(loc=(2, 4, 4)):
    ax_0 = plt.subplot(loc[0], loc[1], 1)
    handles, labels = ax_0.get_legend_handles_labels()
    ax_0.get_legend().remove()
    ax = plt.subplot(*loc)
    ax.legend(handles, labels, loc="center", title="Policy")
    ax.set_axis_off()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)


def postsubplot_wr(ax, i):
    if i == 0:
        ax.xaxis.set_major_locator(ticker.MaxNLocator(3))
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_major_locator(ticker.MaxNLocator(3))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))
    ax.tick_params(which="major", length=6)
    ax.tick_params(which="minor", length=4)
    ax.set_ylabel("")
    ax.set_xlabel("")


reload(maps)
contexts.use("single")


def plot_wrs_grid(
    df=None, y="P100ServiceTimeUtil@10m", hue="ShortLabel", x="Target DWPD"
):
    num_traces = df["RegionLabel"].nunique()

    fig, ax = plt.subplots(
        nrows=2,
        ncols=4,
        sharex=True,
        sharey=False,
        figsize=(7 * 2, 3 * 2),
        layout="constrained",
    )
    for i, (region, df_) in enumerate(df.groupby("RegionLabel")):
        ax = plt.subplot(2, 4, i + 1 + (1 if i > 2 else 0))
        sns.lineplot(
            data=df_, x=x, y=y, **get_kwargs(df_, y, hue=hue), ax=ax, legend=i == 0
        )
        postplot(df_, target=False, targetlabel=False)
        postsubplot_wr(ax, i)
    add_leg_to_subplot((2, 4, 4))
    if "Write Rate" in x:
        fig.supxlabel(maps.l_wr)
    elif "DWPD" in x:
        fig.supxlabel("DWPD (Drive Writes Per Day)")
    fig.supylabel(nice_ylabel(y))


def fillright(
    df_,
    idx=[
        "ShortLabel",
        "AdmissionPolicyLabel",
        "Prefetching",
        "Target Cache Size",
        "Target Cache Size (TB)",
    ],
    verbose=False,
    all_ys=[maps.l_wr, "DWPD"],
):
    cols = all_ys + [
        c
        for c in df_.columns
        if (c.startswith("P") and "@" in c)
        or c.startswith("MeanServiceTime")
        or ("Ratio" in c and c != "SampleRatio")
        or "%" in c
    ]
    df_ = df_.pivot(index=idx, columns=["Region", "RegionLabel"], values=cols)
    if verbose:
        display(df_)
    df_ = df_.fillna(method="ffill")
    if verbose:
        display(df_)
    df_ = df_.stack().stack().reset_index()
    return df_


def postsubplot_csize(ax, i):
    if i == 0:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.2))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(3))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))
    ax.tick_params(which="major", length=6)
    ax.tick_params(which="minor", length=4)
    ax.set_ylabel("")
    ax.set_xlabel("")


def plot_csize_grid(
    df=None, y="P100ServiceTimeUtil@10m", hue="ShortLabel", x="Target Cache Size"
):
    num_traces = df["RegionLabel"].nunique()

    fig, ax = plt.subplots(
        nrows=2,
        ncols=4,
        sharex=True,
        sharey=False,
        figsize=(7 * 2, 3 * 2),
        layout="constrained",
    )
    for i, (region, df_) in enumerate(df.groupby("RegionLabel")):
        ax = plt.subplot(2, 4, i + 1 + (1 if i > 2 else 0))
        sns.lineplot(
            data=df_,
            x=x,
            y=y,
            **get_kwargs(df_, y, hue=hue, errs=False),
            ax=ax,
            legend=i == 0,
        )
        plt.axvline(0.4, ls=":", c="black", label="400GB")
        postplot(df_, target=False, targetlabel=False)
        postsubplot_csize(ax, i)
    add_leg_to_subplot((2, 4, 4))
    fig.supxlabel("Cache Size (TB)")
    fig.supylabel(nice_ylabel(y))
    # plt.xlim(0, 3000)
    plt.xlim(0, 2)


# fig-09
def stats(
    df_summary,
    y,
    idx="ShortLabel",
    cmp="Baleen",
    agg="RegionLabel",
    verbose=0,
    show=True,
    bar=True,
):
    if verbose >= 3:
        display(
            pd.pivot_table(
                df_summary,
                values=[y],
                index=idx,
                columns=agg,
                margins=True,
                margins_name="Avg",
                aggfunc="count",
            )
        )
    drt2 = pd.pivot_table(
        df_summary, values=[y], index=idx, columns=agg, margins=True, margins_name="Avg"
    )
    drt2.drop("Avg", inplace=True)
    drtk = (drt2.loc[cmp] / drt2) * 100
    drtk = -(drtk - 100)
    drtk.drop(cmp, inplace=True)
    if agg:
        drtk.loc[:, (y, "Avg%")] = drtk[drtk.columns[:-1]].mean(axis=1)
    if verbose >= 2:
        print("Raw")
        with pd.option_context("display.float_format", "{:.2f}".format):
            display(drt2)
    if show:
        with pd.option_context("display.float_format", "{:.2f}%".format):
            print(f"Savings over {cmp}")
            if bar:
                display(
                    (-drtk)
                    .style.format("{:.2f}%")
                    .bar(color=["green", "red"], axis=0, vmin=-50, vmax=50)
                )
            else:
                display(drtk)
    return drt2, drtk


resultfiles = {
    "LRU": "runs/example/lru/acceptall-1_lru_366.475GB/full_0_0.1_cache_perf.txt.lzma",
    "DT-SLRU": "runs/example/dt-slru/acceptall-1_lru_366.475GB/full_0_0.1_cache_perf.txt.lzma",
    "EDE": "runs/example/ede/acceptall-1_lru_366.475GB/full_0_0.1_cache_perf.txt.lzma",
}

res = {}
for label, filename in resultfiles.items():
    print(f"\n{label}: {filename}")
    # Use absolute path based on PROJECT_ROOT instead of relative path
    full_path = str(PROJECT_ROOT / filename)
    print(f"  Full path: {full_path}")
    print(f"  Exists: {os.path.exists(full_path)}")
    res[label] = results.get({"Region": "Region1", "Filename": full_path})

print(res["DT-SLRU"])
print(res["DT-SLRU"].summary)

"""
rows = []
for label, resv in res.items():
    resv.summary["Label"] = label
    rows.append(resv.summary)
df = pd.concat(rows)

print(df)
"""

ax = plt.gca()
for label, resv in res.items():
    d_ = res[label].progress["GET+PUT"][600]
    d_["Days"] = d_["Elapsed Trace Time"] / 3600 / 24
    d_.plot(x="Days", y="Util", ax=ax, label=label)

# res['Baleen (ML-Range on Partial-Hit)'].progress['GET+PUT'][600].plot(x='Elapsed Trace Time', y='Util', ax=ax)"
plt.savefig("output.png", dpi=300, bbox_inches="tight")
plt.show()
