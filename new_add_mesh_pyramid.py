import bpy
import bmesh
from bpy.props import FloatProperty, IntProperty
from math import pi
from mathutils import Quaternion, Vector
from pdb import set_trace


def create_step(width, base_level, step_height, num_sides):
        
        
        axis = [0,0,-1]
        PI2 = pi * 2
        rad = width / 2
        
        quat_angles = [(cur_side/num_sides) * PI2 
                            for cur_side in range(num_sides)]
                            
        quaternions = [Quaternion(axis, quat_angle) 
                            for quat_angle in quat_angles]
                            
        init_vectors = [Vector([rad, 0, base_level]) 
                            for quat in quaternions]
        
        quat_vector_pairs = list(zip(quaternions, init_vectors))
        vectors = [quaternion * vec for quaternion, vec in quat_vector_pairs]
        bottom_list = [(vec.x, vec.y, vec.z) for vec in vectors]
        top_list = [(vec.x, vec.y, vec.z+step_height) for vec in vectors]
        full_list = bottom_list + top_list
        return full_list


class AddPyramid(bpy.types.Operator):
    '''Add a mesh pyramid'''
    bl_idname = "mesh.pyramid_add"
    bl_label = "Add Pyramid"
    bl_options = {'REGISTER', 'UNDO'}

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
        
        all_verts = []
        
        height_offset = 0
        cur_width = self.width
        
        for i in range(self.num_steps):
            verts_loc = create_step(cur_width, height_offset, self.height,
                                self.num_sides)
            height_offset += self.height
            cur_width -= self.reduce_by
            all_verts.extend(verts_loc)        
        
        mesh = bpy.data.meshes.new("Pyramid")
        bm = bmesh.new()

        for v_co in all_verts:
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