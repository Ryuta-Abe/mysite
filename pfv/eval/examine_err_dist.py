# -*- coding: utf-8 -*-
# import Env
import os, sys,math
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()
from pymongo import *
client = MongoClient()
db = client.nm4bd
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import norm
from scipy.optimize import curve_fit

from utils import get_list_from_csv

BIN_WIDTH = 0.5

PATH = "../../working/"
ERR_DIST_FILE = PATH + "err_dist_report.csv" 
ERR_DIST_FILE_MARGIN = PATH + "err_dist_report_margin.csv" 

def absolute_Gaussian(x, a, mu, sigma):
    # x = abs(x)
    return a*np.exp(-(x-mu)**2/(2*sigma**2))
    # return a*np.exp(-(x-mu)**2/(2*sigma**2))

# def get_theoretical_err_dist(a, mu, sigma):


def examine_err_dist(err_dist_file):
    def get_err_dist_list(err_dist_file):
        err_dist_matrix = get_list_from_csv(err_dist_file)
        err_dist_list = []
        # print(err_dist_matrix)
        for err_dist in err_dist_matrix:
            # if not (float(err_dist[0]) - 0.0) < 0.001:
            err_dist_list.extend([float(err_dist[0])]*int(err_dist[1]))
        return err_dist_list

    err_dist_list = get_err_dist_list(ERR_DIST_FILE)
    err_dist_list_margin = get_err_dist_list(ERR_DIST_FILE_MARGIN)
    
    bin_num = int((max(err_dist_list) - min(err_dist_list)) / BIN_WIDTH )
    # fig = plt.figure()
    # ax = fig.add_subplot(1,1,1)
    # ax.hist(err_dist_list, bins = bin_num) # cumulative = True, normed = True
    # ax2 = fig.add_subplot(1,1,1)
    # ax2.hist(err_dist_list_margin, bins = bin_num) # cumulative = True, normed = True
    # labels = ['with margin', 'w/o margin']
    # plt.hist([err_dist_list, err_dist_list_margin], stacked=False, color=['orange', 'lightblue'], label=labels, bins = bin_num)
    # plt.legend()

    # param = norm.fit(err_dist_list)
    # print(param)
    # # x = np.linspace(min(err_dist_list), max(err_dist_list), 0.01)
    # x = np.arange(min(err_dist_list), max(err_dist_list), BIN_WIDTH)
    # pdf_fitted = norm.pdf(x,loc=param[0], scale=param[1])
    # # pdf = norm.pdf(x)
    # plt.figure
    # plt.title('Normal distribution')
    # # plt.plot(x, pdf_fitted, 'r-', x, pdf, 'b-')
    # plt.plot(x, pdf_fitted, 'r-')
    # # plt.hist(err_dist_list, normed=1, alpha=.3, bins = bin_num)
    # plt.hist(err_dist_list, normed=1, bins = bin_num)
    # plt.show()

    hist_1, bins = np.histogram(err_dist_list, bin_num )
    # print(hist_1, bins)
    bins = bins[:-1]
    popt, pcov = curve_fit(absolute_Gaussian, bins, hist_1, p0 = [20, 15, 3])
    print("Estimated Param:", popt)
    fitting = absolute_Gaussian(bins, popt[0],popt[1],popt[2])
    residuals =  hist_1 - fitting
    rss = np.sum(residuals**2)#residual sum of squares = rss
    tss = np.sum((hist_1-np.mean(hist_1))**2)#total sum of squares = tss
    r_squared = 1 - (rss / tss)
    ideal_err_list = bins * fitting / sum(fitting)
    # for i, one_bin in enumerate(bins):
    #     one_fitting = fitting[i]
    #     ideal_err_list.append(one_bin * one_fitting)
    ideal_err_dist = sum(ideal_err_list) 

    hist_1 = hist_1 / sum(hist_1)
    fitting = fitting / sum(fitting)

    fig, ax = plt.subplots()
    
    # ax.bar(bins,hist_1,width=100/100,alpha=0.5,color='m',align='edge')

    ax.bar(bins,hist_1,width = BIN_WIDTH ,color='m',align='edge')    
    ax.plot(bins,fitting,'k')
    popt, pcov = curve_fit(absolute_Gaussian, bins, hist_1)
    mu = popt[1]
    ax.annotate("theoretical error dist =" + str(ideal_err_dist)[0:5] + "m", xy=(0.5, 0.5), xycoords='axes fraction')
    ax.annotate("$R^2$="+str(r_squared)[0:5], xy=(0.5, 0.6), xycoords='axes fraction')
    ax.set_xlabel('error distance')
    ax.set_ylabel('frequency')
    plt.show()


    # ax.set_title('誤差距離の出現確立')
    # ax.set_xlabel('error dist')
    # ax.set_ylabel('freq')
    # plt.xlabel("マージン無")
    # plt.xlabel("マージン有")
    # plt.legend()
    # fig.show()
    plt.show()



if __name__ == "__main__":
    examine_err_dist(ERR_DIST_FILE)
