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


def split_list(l, n):
    """
    split the blocks up.  Credit to oremj for this one.
    http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    """
    n *= 2
    returned_list = [l[i:i+n] for i in range(0, len(l), n)]
    return returned_list
    


def get_connector_pairs(lst, n_sides):
    # chop off the verts that get used for the base and top
    lst = lst[n_sides:]
    lst = lst[:-n_sides]
    lst = split_list(lst, n_sides)
    return lst


class AddPyramid(bpy.types.Operator):
    '''Add a mesh pyramid'''
    bl_idname = "mesh.pyramid_add"
    bl_label = "Add Pyramid"
    bl_options = {'REGISTER', 'UNDO'}

    
    num_sides = IntProperty(
                    name="Number Sides",
                    description = "Number of Sides",
                    min = 3, max = 20, default=4
                )
    num_steps = IntProperty(
                    name="Number of Steps",
                    description="Number of Steps",
                    min=1, max=20, default=10)
                
    width = FloatProperty(
            name="Width",
            description="Step Width",
            min=0.01, max=100.0,
            default=2
            )
            
    height = FloatProperty(
            name="Height",
            description="Step Height",
            min=0.01, max=100.0,
            default=0.1
            )
            
    reduce_by = FloatProperty(
                name="Reduce By", description = "Reduce By",
                min=.01, max = 2.0, default= .20
                ) 
    

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
        
        
        # do the sides.
        n = self.num_sides
        
        def add_faces(n, block_vert_sets):
            for bvs in block_vert_sets:
                for i in range(self.num_sides-1):
                    bm.faces.new([bvs[i], bvs[i+n], bvs[i+n+1], bvs[i+1]])
                bm.faces.new([bvs[n-1], bvs[(n*2)-1], bvs[n], bvs[0]])
                
        
        # get the base and cap faces done.
        bm.faces.new(bm.verts[0:self.num_sides])
        bm.faces.new(bm.verts[-self.num_sides:])
        
        # side faces
        block_vert_sets = split_list(bm.verts, self.num_sides)
        add_faces(self.num_sides, block_vert_sets)
        
        # connector faces between faces and faces of the block above it.
        connector_pairs = get_connector_pairs(bm.verts, self.num_sides)
        add_faces(self.num_sides, connector_pairs)
        
        bm.to_mesh(mesh)
        mesh.update()
        scn = bpy.context.scene
        ob = bpy.data.objects.new("pyramid_ob", mesh)
        scn.objects.link(ob)
        ob.select = True
        
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