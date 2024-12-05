import numpy as np
import math as m
import sys
from skspatial.objects import Line, Sphere

# Functions used inside Generate_Step_files_for_layer.py

def change_event_series_for_build_pre_heat(self):
    #This method changes the event series file for the build plate pre-heat step
    
    #read event series from files:
    path = self.scanpath_folder / f"Heat_Series_ly1.csv"
    scanpath_comp_series = np.loadtxt(path, delimiter=",")

    path = self.module_path / f"Heat_Series_pre_heat_meander.csv"
    scanpath_pre_heat_series = np.loadtxt(path, delimiter=",")

    path = self.scanpath_folder / f"Roller_Series_ly1.csv"
    roller_series = np.loadtxt(path, delimiter=",")

    ## 1.remove extra scans from scanpath_pre_heat_series
    # Get the first column of the array
    first_column = scanpath_pre_heat_series[:, 0]
    # Create a boolean mask where the first column values are less than or equal to the pre-heat time requested by the user
    mask = first_column <= self.input_file_dict["bp_pre_heat_time"]
    # Apply the mask to the array to get the filtered array
    final_h_event_series = scanpath_pre_heat_series[mask]
    # remove heat from last row to ensure it laser is off at the end
    final_h_event_series[-1, -1] = 0
    
    ## 2. add component scanpath to event series
    #add pre_heating time to component scanpath:
    scanpath_comp_series[:,0] += self.input_file_dict["bp_pre_heat_time"]
    # concatenate to final event series
    final_h_event_series = np.concatenate((final_h_event_series, scanpath_comp_series), axis=0)

    ## 3. modify roller series
    #add heating time to roller series:
    roller_series[:,0] += self.input_file_dict["bp_pre_heat_time"]

    ##4. Save files to output folder to be read by Abaqus
    np.savetxt(self.Output_Path / "Event_series_Heat_mm.inp", final_h_event_series, delimiter=",")
    np.savetxt(self.Output_Path / "Event_series_Roller_mm.inp", roller_series, delimiter=",")

def change_event_series_for_layer_post_heat(self,layer_number):
    #This method changes the event series file to add layer post-heating
    
    #read event series from files:
    path = self.scanpath_folder / f"Heat_Series_ly{layer_number}.csv"
    scanpath_comp_series = np.loadtxt(path, delimiter=",")

    # make a copy of the scanpath for the rescan
    scanpath_rescan = scanpath_comp_series.copy()
    # remove the dosing time
    scanpath_rescan[:,0] -= self.input_file_dict["dosing_time"]
    #change power to rescan power specified by user
    power_column = scanpath_rescan[:, -1]
    power_column[power_column > self.eps] = self.input_file_dict["post_heat_power"]
    scanpath_rescan[:, -1] = power_column

    scanpath_rescan_cur = scanpath_rescan.copy()

    for i in range(0, self.input_file_dict["post_heat_n_rescans"]):
        scanpath_rescan_cur[:,0] = scanpath_rescan[:,0] + scanpath_comp_series[-1,0] + Calculate_distance(scanpath_comp_series[-1,1:3],scanpath_comp_series[0,1:3])/self.input_file_dict["jump_speed"]
        scanpath_comp_series = np.concatenate((scanpath_comp_series, scanpath_rescan_cur), axis=0)

    ##4. Save files to output folder to be read by Abaqus
    np.savetxt(self.Output_Path / "Event_series_Heat_mm.inp", scanpath_comp_series, delimiter=",")

def Calculate_distance(coords0,coords1): #Calculate distance between two points
        return np.sqrt((coords1[0]-coords0[0])**2 + (coords1[1]-coords0[1])**2)

def inSphere(point, centre, radius):
        #Checks if point is inside a sphere with centre and radius

        # Calculate the difference between the reference and measuring point
        diff = np.subtract(point, centre)

        # Calculate square length of vector (distance between ref and point)^2
        dist = np.sum(np.power(diff, 2))

        # If dist is less than radius^2, return True, else return False
        return dist < radius ** 2
    
def Calculate_sphere_intersection(coords0,coords1,point_of_interest, sphere_radius):
    #Calculates the two points of intersection between a scan line and a sphere around a given point of interest
    sphere = Sphere(point_of_interest, sphere_radius)
    line = Line.from_points(coords0, coords1)

    try:
        point_a, point_b = sphere.intersect_line(line)
        return point_a, point_b
    except:
        return False

def sphere_segment_intersection(P1, P2, C, r):
    x1, y1, z1 = P1
    x2, y2, z2 = P2
    cx, cy, cz = C

    # Quadratic coefficients
    A = (x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2
    B = 2 * ((x2 - x1) * (x1 - cx) + (y2 - y1) * (y1 - cy) + (z2 - z1) * (z1 - cz))
    C = (x1 - cx) ** 2 + (y1 - cy) ** 2 + (z1 - cz) ** 2 - r ** 2

    Delta = B ** 2 - 4 * A * C

    if Delta < 0:
        return False
    elif Delta == 0:
        t = -B / (2 * A)
        if 0 <= t <= 1:  # Check if intersection lies within the segment
            intersection = (x1 + t * (x2 - x1), y1 + t * (y2 - y1), z1 + t * (z2 - z1))
            return [intersection]
        else:
            return False
    else:
        t1 = (-B - m.sqrt(Delta)) / (2 * A) # this intersection is the first one
        t2 = (-B + m.sqrt(Delta)) / (2 * A) # this intersection is the second one

        intersections = []
        if 0 <= t1 <= 1:  # Check if t1 lies within the segment
            intersection1 = (x1 + t1 * (x2 - x1), y1 + t1 * (y2 - y1), z1 + t1 * (z2 - z1))
            intersections.append(intersection1)
        if 0 <= t2 <= 1:  # Check if t2 lies within the segment
            intersection2 = (x1 + t2 * (x2 - x1), y1 + t2 * (y2 - y1), z1 + t2 * (z2 - z1))
            intersections.append(intersection2)

        return intersections if intersections else False

# This class is used to store the high resolution time frames for each layer
class HrTimeFrameRecorder:
    def __init__(self):
        self.list_of_hr_frames = []  # List of high-resolution time frames for each layer
        self.current_hr_frame = []  # A list that will contain a single high-resolution time frame

    def add_time_point(self, time_frame: float):
        if len(self.current_hr_frame) == 0:
            self.current_hr_frame.append(time_frame)
        elif len(self.current_hr_frame) == 1:
            self.current_hr_frame.append(time_frame)
            self.list_of_hr_frames.append(tuple(self.current_hr_frame))
            self.current_hr_frame = []

    def clear_current_frame(self):
        self.current_hr_frame = []

    def get_list_of_frames(self):
        return self.list_of_hr_frames



    # Cases to analyse:
        # Segment intersects several spheres

def Calculate_intersection_times(self, layer_path, time, layer_height, point_of_interest):
       
    HrTFR = HrTimeFrameRecorder()

    first_coordinate = layer_path[1] #we start at 1 to skip dosing time coordinates

    if inSphere(first_coordinate, point_of_interest[:1], self.input_file_dict["radius_sphere_of_interest"]):
        HrTFR.add_time_point(time[1])

    #loop through the coordinates in the scanpath of this layer
    for c in range(1,len(layer_path)): #we start at 1 to skip dosing time coordinates
        #Calculate time of intersection with sphere of interest:

        Coord_ini = np.append(layer_path[c-1], layer_height).transpose()
        Coord_final = np.append(layer_path[c], layer_height).transpose()

        intersection = sphere_segment_intersection(Coord_ini,Coord_final, point_of_interest, self.input_file_dict["radius_sphere_of_interest"])

        if intersection is not False and layer_height >= (point_of_interest[2]-0.0000001): #If there is an intersection in the top half of the sphere
            
            for point in intersection:
                speed = Calculate_distance(Coord_final,Coord_ini) / (time[c] - time[c-1])
                time_of_intersection = time[c-1] + Calculate_distance(layer_path[c-1],point)/speed
                HrTFR.add_time_point(time_of_intersection)
    
    if inSphere(layer_path[-1], point_of_interest[:1], self.input_file_dict["radius_sphere_of_interest"]):
        HrTFR.add_time_point(time[-1])

    return HrTFR.get_list_of_frames()