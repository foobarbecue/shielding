import csv
import bpy
from mathutils.bvhtree import BVHTree  
from mathutils import Vector
origin = Vector((0,0,0))

class Sample:
    def __init__(self, location):
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
        self.empty = bpy.context.object
        self.ray_intersections = []
        self.in_rock_lengths = []

class Shielding_scene:
    def __init__(self, mesh_filepath, samples_filepath):
        bpy.ops.import_mesh.stl(filepath = mesh_filepath)
        self.mesh = bpy.context.object
        #BVH tree is a technique for speeding up the ray - mesh intersections
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
    def intersect_cosrays(self, n=3000, sample=sample):
        #Make a sphere twice the diameter of the mesh, with n vertices.
        #The number of vertices is 10*4**n+2, so need log((n-2)/10,4) subdivs to make them.
        #The sphere constructor will round this to the nearest number of subdivisions.
        bpy.ops.mesh.primitive_ico_sphere_add(
            location = sample.empty.location,
            size = max(self.mesh.dimensions)*2,
            subdivisions = log((n-2)/10,4)
            )
        bounding_sphere=bpy.context.object
        for vert in bounding_sphere.data.vertices:
            sample.ray_intersections.append(get_ray_mesh_intersections(self.mesh, vert.co, sample.empty.location))

def get_ray_mesh_intersections(rock_mesh, ray_source, sample_loc):
    #It seems the the first argument of ray_cast must be inside the object, i.e. the rays have to go outwards.
    intersections = [sample_loc] #first element is sample location because it makes length calculation easier later
    hit, intersection_pt, face_normal, face_ind = rock_mesh.ray_cast(sample_loc, ray_source)
    intersections.append(intersection_pt)
    #After each intersection, move a tiny bit along the same vector and call ray_cast() again
    epsilon = ray_source * 1e-6
    while hit:
        intersections.append(intersection_pt)
        ray_target = intersection_pt + epsilon
        hit, intersection_pt, face_normal, face_ind = rock_mesh.ray_cast(ray_target, ray_source)
    return intersections

def get_lengths_from_intersections(intersections):
    lengths=[]
    for ray in intersections:
        evens = ray[::2]
        odds = ray[1::2]
        rock_segment_lengths = [(seg[0]-seg[1]).length for seg in zip(evens, odds)]
        lengths.append(sum(rock_segment_lengths))
    return lengths

#def get_shielding_factor_from_lengths(lengths):
pbrs = Shielding_scene(mesh_filepath = r"D:\aaron\sfm\parmelee_cosmogenic\shielding\src\gv01_everything.stl",
    samples_filepath = r"D:\aaron\sfm\parmelee_cosmogenic\shielding\src\gv2_samples.csv")
