import bpy
from mathutils.bvhtree import BVHTree  
from mathutils import Vector
origin = Vector((0,0,0))

class shielding_scene:
    def __init__(self, filepath, samples=None):
        bpy.ops.import_mesh.stl(filepath = filepath)
        self.mesh = bpy.context.object
        #BVH tree is a technique for speeding up the ray - mesh intersections
        self.tree = BVHTree.FromObject(self.mesh, bpy.context.scene)
        self.intersections = []
        self.bounding_sphere = None
    def intersect_cosrays(self, n=3000):
        if not self.bounding_sphere:
            #Make an sphere twice the diameter of the mesh, with n vertices.
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
        
def get_ray_mesh_intersections(rock_mesh, ray_source):
    #It seems the the first argument of ray_cast must be inside the object, i.e. the rays have to go outwards.
    intersections = []
    hit, intersection_pt, face_normal, face_ind = rock_mesh.ray_cast(origin, ray_source)
    intersections.append(intersection_pt)
    epsilon = ray_source * 1e-6
    while hit:
        ray_target = intersection_pt + epsilon
        hit, intersection_pt, face_normal, face_ind = rock_mesh.ray_cast(ray_target, ray_source)
        intersections.append(intersection_pt)
    return intersections
    
pbrs = shielding_scene(filepath = r"D:\aaron\sfm\parmelee_cosmogenic\shielding\src\gv01_everything_cntrd.stl")