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
from scipy.special import erf
from utils import get_list_from_csv
### TODO: 以下を変更 ###
BIN_WIDTH = 0.01
SHOWS_GRAPH = True
#######################

PATH = "../../working/"
ERR_DIST_FILE = PATH + "err_dist_report.csv" 
ERR_DIST_FILE_MARGIN = PATH + "err_dist_report_margin.csv" 
OUTPUT_FILE = PATH + "ideal_err_dist.txt"

def Gaussian(x, mu, sigma):
    #  x = abs(x)
    return np.exp(-(x-mu)**2/(2*sigma**2)) / (math.sqrt(2 * math.pi) * sigma)

# def get_theoretical_err_dist(a, mu, sigma):

def integral_Gaussian(x, mu, sigma):
    # return a / 2 * erf(- (x - mu) / (np.sqrt(2) * sigma) )  
    return 1 / 2 * ( 1 + erf((x - mu) / (np.sqrt(2) * sigma)))

def get_r_squared(hist, fitting):
    residuals =  hist - fitting
    rss = np.sum(residuals**2)  # residual sum of squares = rss
    tss = np.sum((hist-np.mean(hist))**2)  # total sum of squares = tss
    r_squared = 1 - (rss / tss)
    return r_squared

def fit_pdf(err_dist_list, bin_num):
    pass
def fit_cdf(err_dist_list, bin_num):
    hist, bins = np.histogram(err_dist_list, bin_num)
    hist = hist / sum(hist)
    bins = bins[:-1]
    cdf = np.cumsum(hist)  # cdf生成(既出の値を足し合わせる)
    # integral_Gaussianにフィルタリングを行い、最適パラメータ算出
    popt, pcov = curve_fit(integral_Gaussian, bins, cdf ,p0 = [10, 5] ) # pot: 最適パラメータ, pcov: 従来パラメータ
    print("Estimated Param [mu, sigma]:", popt)
    fitting = integral_Gaussian(bins, popt[0], popt[1])  # フィルタリングCDF取得
    pdf = Gaussian(bins, popt[0], popt[1])  # フィルタリングCDFからPDF導出
    # フィッチングの確からしさを検証するため、R^2値の導出
    r_squared_cdf = get_r_squared(cdf, fitting)  # CDFのR^2値導出
    r_squared_pdf = get_r_squared(hist, pdf)  # PDFのR^2値導出
    ideal_err_list = bins * pdf / sum(pdf)
    ideal_err_dist = sum(ideal_err_list) 
    print("ideal error distance: ", ideal_err_dist)
    if SHOWS_GRAPH:
        show_graph(bins, hist, pdf / sum(pdf), ["error_distance (m)", "PDF"], r_squared_pdf)
        show_graph(bins, cdf, fitting, ["error_distance (m)", "CDF"], r_squared_cdf) 
    return ideal_err_dist
    

def show_graph(bins, hist, fitting, labels, r_squared):
    fig, ax = plt.subplots()
    # ax.bar(bins,cdf,width=100/100,alpha=0.5,color='m',align='edge')
    ax.bar(bins,hist, width = BIN_WIDTH ,color='m',align='edge')
    ax.plot(bins,fitting,'k')
    # popt, pcov = curve_fit(Gaussian, bins, cdf)
    # mu = popt[1]
    # ax.annotate("theoretical error dist =" + str(ideal_err_dist)[0:5] + "m", xy=(0.5, 0.5), xycoords='axes fraction')
    ax.annotate("$R^2$="+str(r_squared)[0:5], xy=(0.5, 0.6), xycoords='axes fraction')
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])
    plt.show()

def examine_err_dist(err_dist_file):
    def get_err_dist_list(err_dist_file, exists_margin):
        err_dist_matrix = get_list_from_csv(err_dist_file)
        err_dist_list = []
        for err_dist in err_dist_matrix:
            if not(exists_margin) or (exists_margin and not (float(err_dist[0]) - 0.0) < 0.001):
                err_dist_list.extend([float(err_dist[0])]*int(err_dist[1]))
        return err_dist_list
    
    def output_result(ideal_err_dist):
        with open(OUTPUT_FILE, 'a') as f:
            text = str(ideal_err_dist) + "\n"
            f.write(text)


    # err_dist_list = get_err_dist_list(ERR_DIST_FILE, exsits_margin = False)
    err_dist_list_margin = get_err_dist_list(ERR_DIST_FILE_MARGIN, True)
    
    bin_num = int((max(err_dist_list_margin) - min(err_dist_list_margin)) / BIN_WIDTH )
    ideal_err_dist = fit_cdf(err_dist_list_margin, bin_num)
    output_result(ideal_err_dist)


#     fig = plt.figure()
#     ax = fig.add_subplot(1,1,1)
#     ax.hist(err_dist_list, bins = bin_num, cumulative = True, normed = True)
#     # print(hist_1, bins)
#  # 
#     plt.show()
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

    ###
    """
    fitting pdf
    """
    # hist_1, bins = np.histogram(err_dist_list, bin_num )
    # # print(hist_1, bins)
    # bins = bins[:-1]
    # popt, pcov = curve_fit(Gaussian, bins, hist_1, p0 = [20, 15, 3])
    # print("Estimated Param:", popt)
    # fitting = Gaussian(bins, popt[0],popt[1],popt[2])
    # residuals =  hist_1 - fitting
    # rss = np.sum(residuals**2)  #residual sum of squares = rss
    # tss = np.sum((hist_1-np.mean(hist_1))**2)  #total sum of squares = tss
    # r_squared = 1 - (rss / tss)
    # ideal_err_list = bins * fitting / sum(fitting)
    # ideal_err_dist = sum(ideal_err_list) 

    # hist_1 = hist_1 / sum(hist_1)
    # fitting = fitting / sum(fitting)

    # fig, ax = plt.subplots()
    
    # # ax.bar(bins,hist_1,width=100/100,alpha=0.5,color='m',align='edge')
    # ax.bar(bins,hist_1,width = BIN_WIDTH ,color='m',align='edge')    
    # ax.plot(bins,fitting,'k')
    # popt, pcov = curve_fit(Gaussian, bins, hist_1)
    # mu = popt[1]
    # ax.annotate("theoretical error dist =" + str(ideal_err_dist)[0:5] + "m", xy=(0.5, 0.5), xycoords='axes fraction')
    # ax.annotate("$R^2$="+str(r_squared)[0:5], xy=(0.5, 0.6), xycoords='axes fraction')
    # ax.set_xlabel('error distance')
    # ax.set_ylabel('frequency')
    # plt.show()
    
    ###
    """
    fitting cdf
    """
    # hist_1, bins = np.histogram(err_dist_list_margin, bin_num )
    # # print(hist_1, bins)
    # bins = bins[:-1]
    # cdf = np.cumsum(hist_1)
    # # cdf = cdf / max(cdf)
    # popt, pcov = curve_fit(integral_Gaussian, bins, cdf ,p0 = [500, 10, 5] ) # p0 = [20, 15, 3]
    # print("Estimated Param:", popt)
    # fitting = integral_Gaussian(bins, popt[0],popt[1], popt[2])
    # residuals =  cdf - fitting
    # rss = np.sum(residuals**2)  #residual sum of squares = rss
    # tss = np.sum((cdf-np.mean(cdf))**2)  #total sum of squares = tss
    # r_squared = 1 - (rss / tss)
    # # ideal_err_list = bins * fitting / sum(fitting)
    # # ideal_err_dist = sum(ideal_err_list) 
    # cdf = cdf / max(cdf)
    # fitting = fitting / max(fitting)
    # pdf = Gaussian(bins, popt[0],popt[1], popt[2])
    # ideal_err_list = bins * pdf / sum(pdf)
    # ideal_err_dist = sum(ideal_err_list) 

    # fig, ax = plt.subplots()
    
    # # ax.bar(bins,cdf,width=100/100,alpha=0.5,color='m',align='edge')
    # ax.bar(bins,cdf,width = BIN_WIDTH ,color='m',align='edge')    
    # ax.plot(bins,fitting,'k')
    # # popt, pcov = curve_fit(Gaussian, bins, cdf)
    # # mu = popt[1]
    # ax.annotate("theoretical error dist =" + str(ideal_err_dist)[0:5] + "m", xy=(0.5, 0.5), xycoords='axes fraction')
    # ax.annotate("$R^2$="+str(r_squared)[0:5], xy=(0.5, 0.6), xycoords='axes fraction')
    # ax.set_xlabel('error distance')
    # ax.set_ylabel('CDF')
    # plt.show()



    # ax.set_title('誤差距離の出現確立')
    # ax.set_xlabel('error dist')
    # ax.set_ylabel('freq')
    # plt.xlabel("マージン無")
    # plt.xlabel("マージン有")
    # plt.legend()
    # fig.show()
    # plt.show()




if __name__ == "__main__":
    examine_err_dist(ERR_DIST_FILE)
