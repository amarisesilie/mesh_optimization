# see README for sources!

import open3d as o3d
import pymeshlab

ooi = "embryo" # object of interest
alpha_value = ("70", 4.771) # zebrafish alpha value in abs and percentage
# ooi = "mammary" # object of interest
# alpha_value = ("10", 1.430) # mammary alpha value in abs and percentage

# screened poisson
ms = pymeshlab.MeshSet()
ms.load_new_mesh(f"oriented-{ooi}-pcl.ply")
ms.generate_surface_reconstruction_screened_poisson(depth=8, samplespernode=5)
ms.save_current_mesh(f"{ooi}_3d-models/{ooi}-spn.ply")


# alpha shapes
ms = pymeshlab.MeshSet()
ms.load_new_mesh(f"{ooi}-pcl.ply")
ms.generate_alpha_shape(alpha=pymeshlab.Percentage(alpha_value[1]), filtering='Alpha Shape')
ms.save_current_mesh(f"{ooi}_3d-models/{ooi}-{alpha_value[0]}-alpha.ply") # save
# post-processing (taubin smooth)
ms.apply_coord_taubin_smoothing()
ms.save_current_mesh(f"{ooi}_3d-models/{ooi}-{alpha_value[0]}-alpha-processed.ply") # save


# read point clouds in open3d
pcl = o3d.io.read_point_cloud(f"{ooi}-pcl.ply")
oriented_pcl = o3d.io.read_point_cloud(f"oriented-{ooi}-pcl.ply")

# ball pivoting
radii = [20, 50, 80, 110]
rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
    oriented_pcl, o3d.utility.DoubleVector(radii))
# o3d.visualization.draw_geometries([oriented_pcl, rec_mesh])
o3d.io.write_triangle_mesh(f"{ooi}_3d-models/{ooi}-ba-recon.ply", rec_mesh) # saves the bpa mesh in ply format

# post-processing (select border > close holes > deselect everything > taubin smooth)
ms = pymeshlab.MeshSet()
ms.load_new_mesh(f"{ooi}_3d-models/{ooi}-ba-recon.ply")
ms.compute_selection_from_mesh_border()
ms.meshing_close_holes(maxholesize=70)
ms.set_selection_none()
ms.apply_coord_taubin_smoothing()
ms.save_current_mesh(f"{ooi}_3d-models/{ooi}-ba-recon-processed.ply")
