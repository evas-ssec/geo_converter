#!/usr/bin/env python
# encoding: utf-8
"""

Top-level routines to convert Geocat output from hdf4 to netCDF4.


Created by evas April 2015.
Copyright (c) 2015 University of Wisconsin SSEC. All rights reserved.
"""

import os, sys, logging, re, pkg_resources
from constants import *

# import the appropriate file handling modules
from netCDF4 import Dataset          # used to process output netCDF4 files
from pyhdf.SD import SD,SDC, SDS     # used to process input hdf4 files

LOG = logging.getLogger(__name__)

# TODO, these utility and file processing functions / constants should probably move to other files in the future

def clean_path(string_path) :
    """
    Return a clean form of the path without things like '.', '..', or '~'
    """
    path_to_return = None
    if string_path is not None :
        path_to_return = os.path.abspath(os.path.expanduser(string_path))

    return path_to_return

def setup_dir_if_needed(dirPath, descriptionName) :
    """
    create the directory if that is needed, if not don't
    """
    if not (os.path.isdir(dirPath)) :
        LOG.info("Specified " + descriptionName + " directory (" + dirPath + ") does not exist.")
        LOG.info("Creating " + descriptionName + " directory.")
        os.makedirs(dirPath)

def search_for_input_files(starting_file_path, input_types=INPUT_TYPES) :
    """
    given a list of file paths, search down through any directories
    and find files that are of the appropriate input types
    """

    file_paths_to_return = set([ ])

    # make sure the path is fully expanded
    clean_file_path = clean_path(starting_file_path)

    # if this is a single file, test it to see if it's an acceptable input file
    if os.path.isfile(clean_file_path) :

        # check that the file is of the correct type
        file_ext = os.path.splitext(os.path.split(clean_file_path)[-1])[-1][1:]
        if file_ext in input_types :
            file_paths_to_return.update(clean_file_path)
        else :
            LOG.warn("Input file type (" + file_ext + ") is not the expected input type for this program. "
                     "File path will not be processed: " + clean_file_path)

    # otherwise, if it's a directory, expand it and test anything we find
    elif os.path.isdir(clean_file_path) :

        for in_file in os.listdir(clean_file_path) :
            temp_paths = search_for_input_files(os.path.join(clean_file_path, in_file))
            file_paths_to_return.update(temp_paths)

    else :

        LOG.warn("Input path is neither an existing file nor a directory. " +
                 "Path will not be processed: " + starting_file_path)


    return file_paths_to_return

def read_hdf4_info(input_file_path) :
    """
    get information about variable names and attributes (both global and variable specific) from the
    given file. The file is assumed to exist and be a valid hdf4 file

    returns something in the form:

        {
            GLOBAL_ATTRS_KEY    : a dictionary of attribute values keyed by the attribute names
            VAR_LIST_KEY        : [list of variable names]
            VAR_INFO_KEY        :   {
                                        <var_name> :    {
                                                            SHAPE_KEY: (shape of variable data)
                                                            VAR_ATTRS_KEY: a dictionary of attribute values keyed by the attribute names
                                                        }
                                    }

        }

        TODO, depending on what changes need to be made for CF compliance this data structure may need to change a lot
    """

    file_info = { }

    # open the file
    file_object = SD(input_file_path, SDC.READ)

    # get information on the global attributes in the file
    global_attrs = file_object.attributes()
    file_info[GLOBAL_ATTRS_KEY] = global_attrs

    # get information on the variables in the file
    variable_list = file_object.datasets().keys()
    file_info[VAR_LIST_KEY] = variable_list

    # for each variable in a file, get more specific information about it
    file_info[VAR_INFO_KEY] = { }
    sets_temp = file_object.datasets()
        # this should return a dictionary with entries for each variable in the form
        #       <variable name>: ((dimension names), (data shape), type, index num)
    for var_name in variable_list :
        var_object = file_object.select(var_name)
        var_attrs  = var_object.attributes()
        file_info[VAR_INFO_KEY][var_name] = {
                                                SHAPE_KEY: sets_temp[var_name][1],
                                                VAR_ATTRS_KEY: var_attrs,
                                            }

    return file_info, file_object

def determine_dimensions (in_file_info) :
    """
    given an input file and a list of the variables in the file, determine what dimensions
    it has.

    Note: This function makes the assumption that most data will be in two dimensional
    arrays that are indexed by [line, element] and the number of lines and elements will
    be the same for each 2D variable in the file. Any variables that we expect not to
    match this pattern will be defined in the SPECIAL_VARIABLES dictionary.
    """

    # an array to hold the dimensions we will return
    # this will be filled in the format:
    #       dimensions["dimension name"] = dimension size or None for unlimited dimensions
    dimensions = { }
    variable_dim_info = { }

    # some variables we will need to process after we've looked through the simple standard ones
    vars_to_process_last = [ ]

    # look through the variables, determining the expected dimensions
    elements_num = None
    lines_num    = None
    for var_name in in_file_info[VAR_LIST_KEY] :

        # if this is one of our special variables, process it later
        is_special = False
        for special_var_pattern in SPECIAL_VARIABLES.keys() :
            if re.match(special_var_pattern, var_name) :
                vars_to_process_last.append(var_name)
                is_special = True

        # if the variable isn't a special case, try to process it now
        if not is_special :

            # get the variable shape
            shape_temp = in_file_info[VAR_INFO_KEY][var_name][SHAPE_KEY]

            # if it isn't a special var and it's 2 sized, then we expect (lines, elements)
            if len(shape_temp) is 2 :

                # if we don't have an expected number of lines, assume this is it
                mismatched_lines = False
                if lines_num is None :
                    lines_num = shape_temp[0]
                    dimensions[LINES_DIM_NAME] = lines_num
                else :
                    # check if the dim we assume is lines matches the number of lines we have
                    if lines_num != shape_temp[0] :
                        LOG.warn("The first dimension of the two dimensional variable " + var_name +
                                 " does not correspond to the expected number of lines for this data.")
                        vars_to_process_last.append(var_name)
                        mismatched_lines = True

                if not mismatched_lines :

                    # if we don't have an expected number of elements, assume this is it
                    mismatched_elems = False
                    if elements_num is None :
                        elements_num = shape_temp[1]
                        dimensions[ELEMS_DIM_NAME] = elements_num
                    else :
                        # check if the dim we assume is elements matches the number of elements we have
                        if elements_num != shape_temp[1] :
                            LOG.warn("The second dimension of the two dimensional variable " + var_name +
                                     " does not correspond to the expected number of elements for this data.")
                            vars_to_process_last.append(var_name)
                            mismatched_elems = True

                    # if the lines and elements match, add the assumed dims to our list of dims
                    if not mismatched_elems :
                        variable_dim_info[var_name] = (LINES_DIM_NAME, ELEMS_DIM_NAME)

            else :
                LOG.warn("Unexpected dimensions for variable " + var_name + " of " + str(shape_temp) + ".")
                vars_to_process_last.append(var_name) # deal with the complex variables later

    # now match up any special variables and handle any cases we couldn't classify
    temp_dim_index_counter = 1
    for var_name in vars_to_process_last :

        # look through the special variables info and see if this variable matches one of them
        expected_dims_size  = None
        expected_dims_names = None
        for special_var_pattern in SPECIAL_VARIABLES.keys() :

            if re.match(special_var_pattern, var_name) :

                expected_dims_size  = SPECIAL_VARIABLES[special_var_pattern][0]
                expected_dims_names = SPECIAL_VARIABLES[special_var_pattern][1]

        # if the variable was not described in the special variables info, make it some temp dim names
        if expected_dims_names is None :

            LOG.warn("Unable to find information about variable " + var_name + ". " +
                     "Temporary dimension names will be created for this variable.")

            expected_dims_names = [ ]
            expected_dims_size  = [ ]

            # get the variable shape
            shape_temp = in_file_info[VAR_INFO_KEY][var_name][SHAPE_KEY]

            # generate temporary dimensions
            for temp_index in range(len(shape_temp)) :

                dim_name = TEMP_DIM_NAME + temp_dim_index_counter
                temp_dim_index_counter += 1
                dim_size = shape_temp[temp_index]

                expected_dims_names.append(dim_name)
                expected_dims_size.append(dim_size)

            expected_dims_names = tuple(expected_dims_names)
            expected_dims_size  = tuple(expected_dims_size)

        # process each dimension for this variable
        for temp_index in range(len(expected_dims_names)) :

            dim_name = expected_dims_names[temp_index]
            dim_size = expected_dims_size[temp_index]

            if dim_name in dimensions.keys() :
                assert((dim_size is dimensions[dim_name]) or (dim_size is None))
            else :
                dimensions[dim_name] = dim_size

        variable_dim_info[var_name] = expected_dims_names

    return dimensions, variable_dim_info

# TODO, set up proper return codes in case there are file access problems
def write_netCDF4_file (in_file_obj, in_file_info, output_path) :
    """
    given an input file to get raw variable data from, a structure describing the variables and
    attributes in the file, and the path to put output in, create an output netCDF4 file
    """

    # make the output file
    out_file = Dataset(output_path, mode='w', format='NETCDF4')

    # figure out what dimensions we expect
    dimensions_info, variable_dimensions_info = determine_dimensions (in_file_info)
    #  create the dimensions in the netCDF file
    for dim_name in dimensions_info.keys() :

        out_file.createDimension(dim_name, dimensions_info[dim_name])

    # put the global attributes in the file
    global_attrs_temp = in_file_info[GLOBAL_ATTRS_KEY]
    for attr_key in global_attrs_temp.keys() :
        setattr(out_file, attr_key, global_attrs_temp[attr_key])

    # put each of the variables in the file
    for var_name in variable_dimensions_info.keys() :

        # get the raw data from the input file; FUTURE, abstract file access more
        in_var_obj = in_file_obj.select(var_name)
        raw_data   = in_var_obj[:]
        data_type  = raw_data.dtype
        SDS.endaccess(in_var_obj)

        # get the fill value
        variable_attr_info = in_file_info[VAR_INFO_KEY][var_name][VAR_ATTRS_KEY]
        # TODO, this needs to be case insensitive
        fill_value_temp = variable_attr_info["_FillValue"] if "_FillValue" in variable_attr_info else None

        # create the variable with the appropriate dimensions
        out_var_obj = out_file.createVariable(var_name, data_type, variable_dimensions_info[var_name],
                                              fill_value=fill_value_temp)
        out_var_obj.set_auto_maskandscale(False)

        # set the variable attributes
        for attr_key in variable_attr_info.keys() :
            if attr_key != "_FillValue" :
                setattr(out_var_obj, attr_key, variable_attr_info[attr_key])

        # set the variable data
        out_var_obj[:] = raw_data

    return out_file

def hdf4_2_netcdf4(out_path, files_list):
    """convert Geocat output hdf4 file(s) to netcdf4 file(s)
    Given a list of files that are output hdf4 files from Geocat,
    convert them to netcdf4 files and save them in the output directory.

    Note: It is assumed that all the files given in files_list are existing
    files of the appropriate hdf4 format.
    """

    # warn the user if no files were given as input
    if len(files_list) <= 0 :
        LOG.warn("No files were listed in the command line input. No file processing will be done.")

    # process each file the user wants converted separately
    for file_path in files_list :

        # check that the output directory and the input directories are not the same
        # for now just warn the user if they are
        in_dir  = os.path.split(file_path)[0]
        in_file_name = os.path.split(file_path)[1]
        out_dir = clean_path(out_path)
        if in_dir == out_dir :
            LOG.warn("Output file will be placed in the same directory used for input: " + in_dir)

        LOG.info("Attempting to convert file: " + file_path)

        # extract file information
        in_file_info, in_file_object = read_hdf4_info(file_path)

        # TODO, make any changes needed for CF compliance

        # figure out the full path (with name) for the new output file
        new_file_name = os.path.splitext(in_file_name)[0] + OUT_FILE_SUFFIX
        new_file_path = os.path.join(out_dir, new_file_name)

        out_file_object = None
        if os.path.exists(new_file_path) :
            LOG.warn("Output file already exists, file will not be processed: " + new_file_path)
        else:
            # create the output file and write the appropriate data and attributes to the new file
            out_file_object = write_netCDF4_file (in_file_object, in_file_info, new_file_path)

        # close both the old and new files
        in_file_object.end()
        if out_file_object is not None:
            out_file_object.close()

def main():
    import argparse
    description_text = """
    Convert Geocat hdf4 output files to the netCDF4 format.
    """

    # create the argument parser
    parser = argparse.ArgumentParser(description=description_text)

    # add arguments to represent user command line options
    parser.add_argument('files', type=str, nargs=argparse.REMAINDER,
                        help='file or list of files to be processed')
    parser.add_argument('-o', '--out', dest='out', type=str, default="./",
                        help='the path to the output directory; will be created if it does not exist')
    parser.add_argument('-d', '--dirs', dest='do_search_dirs', default=False, action='store_true',
                        help='search any directories given in the files list for files that can be processed')
    parser.add_argument('-n', '--version', dest='version', action='store_true', default=False,
                        help='display the version number of the installed version of the program')

    # logging related options
    parser.add_argument('-v', '--verbose', dest='verbosity', action="count", default=0,
                        help='each occurrence increases verbosity 1 level through ERROR-WARNING-INFO-DEBUG (default ERROR)')
    parser.add_argument('--debug', dest="debug_mode", default=False, action='store_true',
                        help="Enter debug mode. Overrides the verbose command line.")

    # FUTURE, add command line options to handle data aggregation

    # parse the arguments
    args = parser.parse_args()

    # set up the logging level based on the options the user selected on the command line
    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    lvl = levels[min(3, args.verbosity)]
    if args.debug_mode : lvl = logging.DEBUG # override if the user specifically asked for debug
    logging.basicConfig(level = lvl)

    # display the version
    if args.version :
        version_num = pkg_resources.require('geocat_converter')[0].version
        print ("geo_converter version " + str(version_num) + '\n')

    # create the output path if it doesn't exist
    out_path = clean_path(args.out)
    setup_dir_if_needed(out_path, "output")

    # process through the input files and search any directories for files we can process
    # Note: this is a recursive search
    input_files = set([ ])
    for in_file_path in args.files :
        input_files.update(search_for_input_files(in_file_path))
    input_files = list(input_files)

    # try to do the conversion
    return_code = hdf4_2_netcdf4(out_path, input_files)

    return 0 if return_code is None else return_code

if __name__=='__main__':
    sys.exit(main())