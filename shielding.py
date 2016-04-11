import csv
import bpy
from mathutils.bvhtree import BVHTree  
from mathutils import Vector
origin = Vector((0,0,0))

class shielding_scene:
    def __init__(self, filepath, samples_filepath):
        bpy.ops.import_mesh.stl(filepath = filepath)
        self.mesh = bpy.context.object
        #BVH tree is a technique for speeding up the ray - mesh intersections
        self.tree = BVHTree.FromObject(self.mesh, bpy.context.scene)
        self.samples = []
        self.intersections = []
        self.bounding_sphere = None
        self.read_samples(self, samples_filepath)
    def intersect_cosrays(self, n=3000, sample_loc=origin):
        if not self.bounding_sphere:
            #Make a sphere twice the diameter of the mesh, with n vertices.
            #The number of vertices is 10*4**n+2, so need log((n-2)/10,4) subdivs to make them.
            #The sphere constructor will round this to the nearest number of subdivisions.
            bpy.ops.mesh.primitive_ico_sphere_add(
                location = origin,
                size = max(self.mesh.dimensions)*2,
                subdivisions = log((n-2)/10,4)
                )
            self.bounding_sphere=bpy.context.object
        for vert in self.bounding_sphere.data.vertices:
            self.intersections.append(get_ray_mesh_intersections(self.mesh, vert.co))
    def read_samples(self, samples_filepath=None):
        samples_filepath = samples_filepath or self.samples_filepath
        with open(samples_filepath) as samplesfile:
            rdr = csv.reader(samplesfile, quoting=csv.QUOTE_NONNUMERIC)
            for line in rdr:
                self.samples.append(Vector(line))

def get_ray_mesh_intersections(rock_mesh, ray_source, sample_loc):
    #It seems the the first argument of ray_cast must be inside the object, i.e. the rays have to go outwards.
    intersections = [origin,]
    hit, intersection_pt, face_normal, face_ind = rock_mesh.ray_cast(origin, ray_source)
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
        evens = [origin] + ray[1::2]
        odds = ray[::2]
        rock_segment_lengths = [(seg[0]-seg[1]).length for seg in zip(evens, odds)]
        lengths.append(sum(rock_segment_lengths))
    return lengths

#def get_shielding_factor_from_lengths(lengths):
pbrs = shielding_scene(filepath = r"D:\aaron\sfm\parmelee_cosmogenic\shielding\src\gv01_everything_cntrd.stl",
    samples_filepath = r"D:\aaron\sfm\parmelee_cosmogenic\shielding\src\gv2_samples.csv")
