import os
from osgeo import ogr, osr


def convert_gis_file_geojson(input_file, output_file):
    output_file_path = convert_single_file(input_file, output_file)
    return output_file_path


def convert_single_file(input_file, output_file):
    # Get the driver for the input file format
    in_driver_name = ogr.GetDriverByName('GeoJSON')

    # Open the input data source
    in_data_source = in_driver_name.Open(input_file, 0)
    if in_data_source is None:
        print(f"Error opening input file '{input_file}'.")
        return

    # Get the input layer
    in_layer = in_data_source.GetLayer()

    # Get the driver for the output file format (GeoJSON)
    out_driver_name = ogr.GetDriverByName('GeoJSON')

    # Create the output data source
    if os.path.exists(output_file):
        out_driver_name.DeleteDataSource(output_file)
    out_data_source = out_driver_name.CreateDataSource(output_file)
    if out_data_source is None:
        print(f"Error creating output file '{output_file}'.")
        return

    # Create the output layer with the same name as the input layer
    input_layer_name = in_layer.GetName()
    out_layer = out_data_source.CreateLayer(
        input_layer_name, in_layer.GetSpatialRef(), geom_type=in_layer.GetGeomType())

    # Copy the input layer's fields to the output layer
    in_layer_def = in_layer.GetLayerDefn()
    for i in range(in_layer_def.GetFieldCount()):
        field_def = in_layer_def.GetFieldDefn(i)
        out_layer.CreateField(field_def)

    # Copy the input layer's features to the output layer
    for feature in in_layer:
        out_feature = ogr.Feature(out_layer.GetLayerDefn())
        out_feature.SetFrom(feature)
        out_layer.CreateFeature(out_feature)
        out_feature.Destroy()

    # Copy metadata
    in_metadata = in_layer.GetMetadata()
    out_layer.SetMetadata(in_metadata)

    # Cleanup
    in_data_source.Destroy()
    out_data_source.Destroy()

    return output_file
