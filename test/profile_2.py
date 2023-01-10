from PIL import Image
import numpy as np
import math
import scipy.ndimage
import matplotlib.pyplot as plt
import csv

def lineprofile():
    dem_pixel_list = []
    dem_value_list = []
    generated_pixel_list = []
    generated_value_list = []

    with open("./dtm_2.csv") as f:
        reader = csv.reader(f,delimiter=",")
        l = [row for row in reader]
        dem_pixel_list = np.array([x[0] for x in l])
        dem_value_list = np.array([float(x[1]) for x in l])
    
    with open("./generated_2.csv") as f:
        reader = csv.reader(f,delimiter=",")
        l = [row for row in reader]
        generated_pixel_list = np.array([x[0] for x in l])
        generated_value_list = np.array([float(x[1]) for x in l])

    DEM_RANGE = [1881.8425,4735.1977]
    dem_value_list = (dem_value_list - dem_value_list.min())/(dem_value_list.max() - dem_value_list.min())
    dem_value_list = (dem_value_list*DEM_RANGE[1] - dem_value_list*DEM_RANGE[0]+DEM_RANGE[0])
    generated_value_list = (generated_value_list - generated_value_list.min())/(generated_value_list.max() - generated_value_list.min())
    generated_value_list = (generated_value_list*DEM_RANGE[1] - generated_value_list*DEM_RANGE[0]+DEM_RANGE[0])

    dem_pixel_list = [int(x)*55 for x in dem_pixel_list]
    plt.rcParams["font.size"] = 18
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_yticks([np.amin(dem_value_list),np.mean(dem_value_list),np.amax(dem_value_list)+50])
    ax.set_xticks([0, 128*55, 285*55])
    ax.set_xlabel("Distance [m]")
    ax.set_ylabel("Height [m]")
    ax.plot(dem_pixel_list,dem_value_list,color = "blue", label="LRO NAC DEM")
    ax.plot(dem_pixel_list,generated_value_list,color="red",label="Generated DEM")
    ax.legend()
    plt.show()

if __name__ == "__main__":
    lineprofile()