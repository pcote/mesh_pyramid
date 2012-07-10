import bpy
import bmesh
from bpy.props import FloatProperty, IntProperty
from math import pi
from mathutils import Quaternion, Vector
from pdb import set_trace

def make_step(initial_size, step_height, height_offset, num_sides):
    
    axis = [0, 0, -1]
    PI2 = pi * 2
    rad = initial_size / 2.0
    
    bottom_list = []
    
    for i, cur_side in enumerate(range(num_sides)):
        quat = Quaternion(axis, (cur_side / num_sides) * PI2)
        vec_data =  quat * Vector([rad,0, height_offset])
        vec_data = vec_data.x, vec_data.y, vec_data.z
        bottom_list.append(vec_data)
    
    top_list = [[b[0], b[1], b[2]+step_height] for b in bottom_list]
    full_list = bottom_list + top_list
    return full_list, [] # TODO: Implement faces


def create_mesh_data(init_size, height, height_offset, num_sides, num_steps):
        from functools import reduce
        from operator import concat
        
        z_data = [[x]*num_sides*2 for x in range(num_steps+1)]
        z_data = reduce(concat, z_data)
        z_data = z_data[num_sides : -num_sides]
        data_set = [(0,0,z) for z in z_data]
        
        axis = [0,0,-1]
        PI2 = pi * 2
        rad = init_size / 2
        
        """
        make quaternion angles out of current side, num_sides, and pi*2
        make a list of side values. (where by side i mean a corner actually)
        """
        quat_angles = [(cur_side/num_sides) * PI2 
                            for cur_side in range(num_sides)]
        quaternions = [Quaternion(axis, quat_angle) 
                            for quat_angle in quat_angles]
        init_vectors = [Vector([rad, 0, height_offset]) 
                        for quat in quaternions]
        
        quat_vector_pairs = list(zip(quaternions, init_vectors))
        vectors = [quaternion * vec for quaternion, vec in quat_vector_pairs]
        # TODO: Figure out the rest of this.
        
        
        
        
        return data_set

class AddPyramid(bpy.types.Operator):
    '''Add a mesh pyramid'''
    bl_idname = "mesh.pyramid_add"
    bl_label = "Add Pyramid"
    bl_options = {'REGISTER', 'UNDO'}

    initial_size = FloatProperty(
                   name="Initial_Size", 
                   description="Initial Size",
                   min = 1.0, max = 10.0
                   )
    num_sides = IntProperty(
                    name="Number Sides",
                    description = "Number of Sides",
                    min = 4, max = 8, default=4
                )
    num_steps = IntProperty(
                    name="Number of Steps",
                    description="Number of Steps",
                    min=1, max=3, default=2)
                
    width = FloatProperty(
            name="Width",
            description="Step Width",
            min=0.01, max=100.0,
            default=1.0
            )
            
    height = FloatProperty(
            name="Height",
            description="Step Height",
            min=0.01, max=100.0,
            default=1.0
            )
            
    reduce_by = FloatProperty(
                name="Reduce By", description = "Reduce By",
                min=.1, max = 2.0, default=.2) 
    

    def execute(self, context):
        height_offset = 1 # placeholder variable.
        
        verts_loc = create_mesh_data(self.initial_size, 
                              self.height, height_offset,
                              self.num_sides, self.num_steps)
        
        mesh = bpy.data.meshes.new("Pyramid")
        bm = bmesh.new()

        for v_co in verts_loc:
            bm.verts.new(v_co)
        
        #for f in faces_info:
        #    bm.faces.new(f)

        bm.to_mesh(mesh)
        mesh.update()

        scn = bpy.context.scene
        ob = bpy.data.objects.new("pyramid_ob", mesh)
        scn.objects.link(ob)
        
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddPyramid.bl_idname, icon='PLUGIN')


def register():
    bpy.utils.register_class(AddPyramid)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddPyramid)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()