#import sys
#sys.path.append(r"C:\Users\aaron2\.p2\pool\plugins\org.python.pydev_4.5.5.201603221110\pysrc")
#import pydevd
#pydevd.settrace(stdoutToServer=True, stderrToServer=True, suspend=False)
import code
import csv
import bpy
from mathutils.bvhtree import BVHTree  
from mathutils import Vector
import random
from numpy import array, pi, zeros, mean, exp, cos, sin #Use numpy functions for element-wise trig
origin = Vector((0,0,0))

class Sample:
    """
    Stores all information about a particlar sample measurement.
    This includes information about the simulation rays used to calculate shielding factor.
    """
    def __init__(self, location, n_rays=1000):
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
        self.empty = bpy.context.object
        self.n_rays = n_rays
        self.ray_intersections = []
        self.in_rock_lengths = zeros(n_rays)
    def calculate_shielding_factor(self, particle_attenuation_length=2.2, m=2.2):
        print('avg len: {}'.format(mean(self.in_rock_lengths)))
        self.shielding_factor = pi**2*mean(((cos(self.phis))**m)*sin(self.phis)*exp(-self.in_rock_lengths/particle_attenuation_length))
        self.shielding_factor = self.shielding_factor / (2*pi/(m+1)) # normalize by maximum full-sky flux
        print(self.empty.location)
        print(self.shielding_factor)

class Shielding_scene:
    def __init__(self, mesh_filepath, samples_filepath):
        bpy.ops.import_mesh.stl(filepath = mesh_filepath)
        self.mesh = bpy.context.object
        #BVH tree is a technique for speeding up the ray - mesh intersection calculations
        self.tree = BVHTree.FromObject(self.mesh, bpy.context.scene)
        self.samples = []
        with open(samples_filepath) as samplesfile:
            rdr = csv.reader(samplesfile, quoting=csv.QUOTE_NONNUMERIC)
            for line in rdr:
                new_sample = Sample(location=Vector(line))
                self.samples.append(new_sample)
        for sample in self.samples:
            self.intersect_cosrays(sample=sample)
            sample.in_rock_lengths = get_lengths_from_intersections(sample.ray_intersections)
            sample.calculate_shielding_factor(particle_attenuation_length=2.2, m=2.2)
#        code.interact(local=locals())
    def intersect_cosrays(self, sample):
        # random phis & thetas
        # phi is zenith angle, AKA elevation and goes from 0 to pi/2
        sample.phis = [random.uniform(0,pi/2) for _ in range(sample.n_rays)]
        # theta is azimuth and goes from 0 to 2*pi
        sample.thetas = [random.uniform(0,2*pi) for _ in range(sample.n_rays)]
        r = max(self.mesh.dimensions)*2 # Make ray source distances twice the longest mesh dimension
        xyzs = convert_spherical_to_xyz(sample.thetas, sample.phis, r)
        ray_sources = array(xyzs).transpose()+sample.empty.location
        for ray_source in ray_sources:
#            bpy.ops.object.empty_add(type='PLAIN_AXES',location=Vector(ray_source))
            sample.ray_intersections.append(get_ray_mesh_intersections(self.mesh, Vector(ray_source), sample.empty.location))

def get_ray_mesh_intersections(rock_mesh, ray_source, sample_loc):
    #It seems the the first argument of ray_cast must be inside the object, i.e. the rays have to go outwards.
    intersections = [sample_loc] #first element is sample location because it makes length calculation easier later
    hit, intersection_pt, face_normal, face_ind = rock_mesh.ray_cast(sample_loc, ray_source)
    intersections.append(intersection_pt)
    #After each intersection, move a tiny bit along the same vector and call ray_cast() again
    epsilon = ray_source * 1e-6
    while hit:
        ray_target = intersection_pt + epsilon
        hit, intersection_pt, face_normal, face_ind = rock_mesh.ray_cast(ray_target, ray_source)
        if hit:
            intersections.append(intersection_pt)
    return intersections

def get_lengths_from_intersections(rays):
    lengths = zeros(len(rays))
    for ray_num, ray in enumerate(rays):
        rock_segment_lengths = [(seg[1]-seg[0]).length for seg in zip(ray[::2], ray[1::2])]
        lengths[ray_num] = sum(rock_segment_lengths)
    return lengths

def convert_spherical_to_xyz(az, el, r, ):
    """ From https://github.com/numpy/numpy/issues/5228 """
    rcos_theta = r * cos(el)
    x = rcos_theta * cos(az)
    y = rcos_theta * sin(az)
    z = r * sin(el)
    return x, y, z

#def get_shielding_factor_from_lengths(lengths):
pbrs = Shielding_scene(mesh_filepath = r"D:\aaron\sfm\parmelee_cosmogenic\shielding\src\gv01_everything.stl",
    samples_filepath = r"D:\aaron\sfm\parmelee_cosmogenic\shielding\src\gv2_samples.csv")
