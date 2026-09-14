import sys
import os
import math
import bpy
import mathutils

def main():
    print("=== Starting 3D Puzzle Builder in Blender ===")
    
    # Check input files gracefully
    svg_base = os.path.abspath("sheet_1_base_plate.svg")
    svg_tiles = os.path.abspath("sheet_2_frame_and_tiles.svg")
    
    if not os.path.exists(svg_base):
        raise FileNotFoundError(f"Required input file missing: {svg_base}")
    if not os.path.exists(svg_tiles):
        raise FileNotFoundError(f"Required input file missing: {svg_tiles}")

    # 1. Environment Initialization
    # Clear default scene objects
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    
    # Configure unit system to METRIC
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'
    
    # Configure render engine (CYCLES)
    try:
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 128
        scene.cycles.use_denoiser = False
        scene.cycles.use_preview_denoising = False
        if len(scene.view_layers) > 0 and hasattr(scene.view_layers[0], "cycles"):
            scene.view_layers[0].cycles.use_denoising = False
        scene.cycles.device = 'CPU'
    except Exception as e:
        print(f"Cycles engine setup fallback to EEVEE: {e}")
        scene.render.engine = 'BLENDER_EEVEE'

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

    print("Render engine configured:", scene.render.engine)

    # 3. Create Materials
    # Base Plate Material: Matte White Acrylic (#F0F0F0, Roughness 0.25, Specular 0.5)
    mat_base = bpy.data.materials.new(name="MatteWhiteAcrylic")
    mat_base.use_nodes = True
    bsdf_base = mat_base.node_tree.nodes.get("Principled BSDF")
    if bsdf_base:
        bsdf_base.inputs["Base Color"].default_value = (0.94, 0.94, 0.94, 1.0)
        bsdf_base.inputs["Roughness"].default_value = 0.25
        bsdf_base.inputs["Specular"].default_value = 0.5

    # Main Body / Bottom Material: Opaque Matte Black (#1A1A1A, Roughness 0.3)
    mat_black = bpy.data.materials.new(name="MatteBlackAcrylic")
    mat_black.use_nodes = True
    bsdf_black = mat_black.node_tree.nodes.get("Principled BSDF")
    if bsdf_black:
        bsdf_black.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1.0)
        bsdf_black.inputs["Roughness"].default_value = 0.3
        bsdf_black.inputs["Specular"].default_value = 0.5

    # Top Face Material: Dual-Tone Top Face (#E8E8E8, Roughness 0.2)
    mat_top = bpy.data.materials.new(name="TopFaceWhiteAcrylic")
    mat_top.use_nodes = True
    bsdf_top = mat_top.node_tree.nodes.get("Principled BSDF")
    if bsdf_top:
        bsdf_top.inputs["Base Color"].default_value = (0.91, 0.91, 0.91, 1.0)
        bsdf_top.inputs["Roughness"].default_value = 0.2
        bsdf_top.inputs["Specular"].default_value = 0.5

    # Surface / Table Material: Neutral Wood / Studio Backdrop (#5A544D, Roughness 0.4)
    mat_table = bpy.data.materials.new(name="StudioTableBackdrop")
    mat_table.use_nodes = True
    bsdf_table = mat_table.node_tree.nodes.get("Principled BSDF")
    if bsdf_table:
        bsdf_table.inputs["Base Color"].default_value = (0.35, 0.33, 0.30, 1.0)
        bsdf_table.inputs["Roughness"].default_value = 0.4

    # 2. SVG Import & 3D Extrusion
    # --- Sheet 1: Base Plate ---
    print(f"Importing {svg_base}...")
    bpy.ops.import_curve.svg(filepath=svg_base)
    
    base_curve = None
    for o in scene.objects:
        if o.name == 'outer_frame_perimeter':
            base_curve = o
            break
            
    if not base_curve:
        raise ValueError("Could not find 'outer_frame_perimeter' in sheet_1_base_plate.svg")

    base_curve.data.dimensions = '2D'
    base_curve.data.fill_mode = 'BOTH'
    base_curve.data.extrude = 0.0015  # 3.0 mm total extrusion height (0.0015 top + 0.0015 bottom)
    base_curve.data.bevel_depth = 0.0002  # 0.2 mm bevel depth
    
    base_curve.select_set(True)
    bpy.context.view_layer.objects.active = base_curve
    bpy.ops.object.convert(target='MESH')
    base_obj = base_curve
    base_obj.name = "Base_Plate"
    base_obj.location.z = 0.0015
    base_obj.data.materials.append(mat_base)

    # --- Sheet 2: Frame & Tiles ---
    print(f"Importing {svg_tiles}...")
    bpy.ops.import_curve.svg(filepath=svg_tiles)

    sheet2_objs = [o for o in scene.objects if o != base_obj]
    
    frame_curve = None
    delta_boundary = None
    tile_cuts = []

    for o in sheet2_objs:
        if o.name.startswith('outer_frame_perimeter'):
            frame_curve = o
        elif o.name.startswith('delta_2_outer_boundary'):
            delta_boundary = o
        elif o.name.startswith('internal_tile_cut_'):
            tile_cuts.append(o)

    # --- Create Outer Frame Mesh ---
    print("Building 3D Outer Frame...")
    bpy.ops.object.select_all(action='DESELECT')
    delta_boundary.select_set(True)
    bpy.ops.object.duplicate()
    frame_cutout = bpy.context.active_object
    
    frame_cutout.select_set(True)
    frame_curve.select_set(True)
    bpy.context.view_layer.objects.active = frame_curve
    bpy.ops.object.join()

    frame_curve.data.dimensions = '2D'
    frame_curve.data.fill_mode = 'BOTH'
    frame_curve.data.extrude = 0.0015
    frame_curve.data.bevel_depth = 0.0002
    
    bpy.ops.object.convert(target='MESH')
    frame_obj = frame_curve
    frame_obj.name = "Outer_Frame"
    frame_obj.location.z = 0.0045  # Staked 3mm above base plate
    frame_obj.data.materials.append(mat_black)
    frame_obj.data.materials.append(mat_top)
    
    for p in frame_obj.data.polygons:
        if p.normal.z > 0.8:
            p.material_index = 1

    # --- Create Tiles Mesh ---
    print("Building 3D Spectre Tiles...")
    bpy.ops.object.select_all(action='DESELECT')
    for c in tile_cuts:
        c.select_set(True)
    delta_boundary.select_set(True)
    bpy.context.view_layer.objects.active = delta_boundary
    bpy.ops.object.join()

    delta_boundary.data.dimensions = '2D'
    delta_boundary.data.fill_mode = 'BOTH'
    delta_boundary.data.extrude = 0.0015
    delta_boundary.data.bevel_depth = 0.0002

    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')

    tile_objs = [o for o in scene.objects if o.name.startswith('delta_2_outer_boundary')]
    print(f"Generated {len(tile_objs)} individual tile meshes.")

    for i, tile in enumerate(tile_objs):
        tile.name = f"Spectre_Tile_{i+1}"
        tile.location.z = 0.0045
        tile.data.materials.append(mat_black)
        tile.data.materials.append(mat_top)
        
        for p in tile.data.polygons:
            if p.normal.z > 0.8:
                p.material_index = 1

    # Center puzzle geometry to origin (0, 0, 0)
    bbox_corners = [base_obj.matrix_world @ mathutils.Vector(corner) for corner in base_obj.bound_box]
    center_x = sum(c.x for c in bbox_corners) / 8.0
    center_y = sum(c.y for c in bbox_corners) / 8.0

    print(f"Centering scene from ({center_x:.4f}, {center_y:.4f}) to origin...")
    all_puzzle_objs = [base_obj, frame_obj] + tile_objs
    for o in all_puzzle_objs:
        o.location.x -= center_x
        o.location.y -= center_y

    # --- Surface / Table Backdrop ---
    print("Adding table backdrop plane...")
    bpy.ops.mesh.primitive_plane_add(size=3.0, location=(0, 0, 0))
    table = bpy.context.active_object
    table.name = "Table_Backdrop"
    table.data.materials.append(mat_table)

    # 4. Lighting & Camera Setup
    print("Setting up 3-point studio lighting & camera...")
    # Key Light
    key_light_data = bpy.data.lights.new(name="KeyLight", type='AREA')
    key_light_data.energy = 80.0
    key_light_data.size = 0.8
    key_light_obj = bpy.data.objects.new(name="KeyLight", object_data=key_light_data)
    scene.collection.objects.link(key_light_obj)
    key_light_obj.location = (0.4, -0.5, 0.6)
    
    # Fill Light
    fill_light_data = bpy.data.lights.new(name="FillLight", type='AREA')
    fill_light_data.energy = 30.0
    fill_light_data.size = 1.2
    fill_light_obj = bpy.data.objects.new(name="FillLight", object_data=fill_light_data)
    scene.collection.objects.link(fill_light_obj)
    fill_light_obj.location = (-0.5, -0.3, 0.4)

    # Rim Light
    rim_light_data = bpy.data.lights.new(name="RimLight", type='SPOT')
    rim_light_data.energy = 50.0
    rim_light_data.spot_size = math.radians(45)
    rim_light_obj = bpy.data.objects.new(name="RimLight", object_data=rim_light_data)
    scene.collection.objects.link(rim_light_obj)
    rim_light_obj.location = (0.2, 0.6, 0.5)

    # Camera Setup
    cam_data = bpy.data.cameras.new(name="PuzzleCamera")
    cam_obj = bpy.data.objects.new(name="PuzzleCamera", object_data=cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Position camera focused at 3/4 isometric angle looking at [0, 0, 0]
    cam_location = mathutils.Vector((0.35, -0.35, 0.40))
    target_location = mathutils.Vector((0.0, 0.0, 0.003))
    
    cam_obj.location = cam_location
    direction = target_location - cam_location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    cam_data.lens = 50

    # 5. Outputs (Headless Execution)
    render_img_path = os.path.abspath("puzzle_render.png")
    glb_model_path = os.path.abspath("puzzle_model.glb")
    blend_file_path = os.path.abspath("puzzle_scene.blend")

    print(f"Rendering camera view to {render_img_path}...")
    scene.render.filepath = render_img_path
    bpy.ops.render.render(write_still=True)
    print("Render complete!")

    print(f"Exporting 3D scene model to {glb_model_path}...")
    bpy.ops.export_scene.gltf(filepath=glb_model_path, export_format='GLB')
    print("Export complete!")

    print(f"Saving native Blender scene to {blend_file_path}...")
    bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)
    print("Save complete!")

    print("=== All 3D Puzzle operations finished successfully ===")

if __name__ == "__main__":
    main()
