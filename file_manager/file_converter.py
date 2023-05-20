import sys
import os
import zipfile
from osgeo import ogr, osr
import shutil
import tempfile


def convert_gis_file(input_file, output_file):
    # Check if the input file is a zip file
    if zipfile.is_zipfile(input_file):
        # Create a temporary directory to extract the zip file
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(input_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Find the first supported GIS file inside the temporary directory
        extracted_file = None
        driver_map = {
            'shp': 'ESRI Shapefile',
            'kml': 'KML',
            'geojson': 'GeoJSON',
            'gml': 'GML',
            'wkt': 'WKT'
        }
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_extension = file.split('.')[-1].lower()
                if file_extension in driver_map:
                    extracted_file = os.path.join(root, file)
                    break
            if extracted_file:
                break

        if not extracted_file:
            print(f"No supported GIS file found inside '{input_file}'.")
            return

        # Get the layer name from the extracted file
        in_data_source = ogr.GetDriverByName(
            driver_map[file_extension]).Open(extracted_file, 0)
        if in_data_source is None:
            print(f"Error opening input file '{extracted_file}'.")
            return
        in_layer = in_data_source.GetLayer()
        input_layer_name = in_layer.GetName()
        in_data_source.Destroy()

        # Call the conversion function with the extracted file and the input layer name
        output_file_path = convert_single_file(
            extracted_file, output_file, input_layer_name)

        # Remove the temporary directory
        shutil.rmtree(temp_dir)
    else:
        output_file_path = convert_single_file(input_file, output_file)
    return output_file_path


def convert_single_file(input_file, output_file, input_layer_name=None):
    # Dictionary for file extensions and driver names
    driver_map = {
        'shp': 'ESRI Shapefile',
        'kml': 'KML',
        'geojson': 'GeoJSON',
        'gml': 'GML',
        'wkt': 'WKT'
    }

    # Get the driver for the input file format
    input_extension = input_file.split('.')[-1].lower()
    if input_extension not in driver_map:
        print(f"Input file format '{input_extension}' not supported.")
        return
    in_driver_name = ogr.GetDriverByName(driver_map[input_extension])

    # Open the input data source
    in_data_source = in_driver_name.Open(input_file, 0)
    if in_data_source is None:
        print(f"Error opening input file '{input_file}'.")
        return

    # Get the input layer
    in_layer = in_data_source.GetLayer()

    # Get the driver for the output file format
    output_extension = output_file.split('.')[-1].lower()
    if output_extension not in driver_map:
        print(f"Output file format '{output_extension}' not supported.")
        return
    out_driver_name = ogr.GetDriverByName(driver_map[output_extension])

    # Create the output data source
    if os.path.exists(output_file):
        out_driver_name.DeleteDataSource(output_file)

    if output_extension == 'shp':
        # Create a directory for the Shapefile output
        output_dir = os.path.splitext(output_file)[0]
        os.makedirs(output_dir, exist_ok=True)
        output_file_name = os.path.splitext(os.path.basename(output_file))[0]
        output_file_path = os.path.join(
            output_dir, output_file_name + '.' + output_extension)
    else:
        output_file_path = output_file

    if os.path.exists(output_file_path):
        out_driver_name.DeleteDataSource(output_file_path)
    out_data_source = out_driver_name.CreateDataSource(output_file_path)
    if out_data_source is None:
        print(f"Error creating output file '{output_file}'.")
        return

    # Create the output layer with the same name as the input layer
    if input_layer_name is None:
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

    if output_extension == 'shp':
        output_zip = output_file
        create_zip(output_dir, output_zip)
        print(f"Output directory '{output_dir}' zipped as '{output_zip}'.")
        # Return the actual path of the zipped Shapefile
        return output_zip
    else:
        # Return the output_file_path for other formats
        return output_file_path


def create_zip(output_dir, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_dir)
                zipf.write(file_path, arcname)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python gis_file_converter.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    convert_gis_file(input_file, output_file)
    print(f"File '{input_file}' converted to '{output_file}'.")
