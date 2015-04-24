#!/usr/bin/env python
# encoding: utf-8
"""

Top-level routines to convert Geocat output from hdf4 to netCDF4.


Created by evas April 2015.
Copyright (c) 2015 University of Wisconsin SSEC. All rights reserved.
"""

import os, sys, logging, re

# import the appropriate file handling modules
from netCDF4 import Dataset                     # used to process output netCDF4 files
from pyhdf.SD import SD,SDC, SDS, HDF4Error     # used to process input hdf4 files

LOG = logging.getLogger(__name__)

VERSION = 0.1

# TODO, these utility and file processing functions / constants should probably move to other files in the future

OUT_FILE_SUFFIX = ".nc"

LINES_DIM_NAME = "lines"
ELEMS_DIM_NAME = "elements"

# a list of variables of special dimensions, with their expected shape and dimension names
SPECIAL_VARIABLES = {
                        r".*?_planck"            :   [(2, 16),          ("cal_dim_temp1", "channel_num")],
                        r"calibration_.*?"       :   [(2, 16),          ("cal_dim_temp1", "channel_num")],
                        r".*?_wavenumber"        :   [(2, 16),          ("cal_dim_temp1", "channel_num")],
                        r"scan_line_time"        :   [(None,),          (LINES_DIM_NAME,)],
                        r".*?_quality_flags1"    :   [(None, None, 3),  (LINES_DIM_NAME, ELEMS_DIM_NAME, "qf_depth1")],
                        r".*?_cloud_mask_packed" :   [(None, None, 7),  (LINES_DIM_NAME, ELEMS_DIM_NAME, "packed_bytes1")],
                        r".*?_cloud_type_packed" :   [(None, None, 6),  (LINES_DIM_NAME, ELEMS_DIM_NAME, "packed_bytes2")],
                    }

INPUT_TYPES = ['hdf']

def clean_path(string_path) :
    """
    Return a clean form of the path without things like '.', '..', or '~'
    """
    clean_path = None
    if string_path is not None :
        clean_path = os.path.abspath(os.path.expanduser(string_path))

    return clean_path

GLOBAL_ATTRS_KEY = "global_attributes"
VAR_LIST_KEY     = "variable_list"
VAR_INFO_KEY     = "variable_info"
SHAPE_KEY        = "shape"
VAR_ATTRS_KEY    = "attributes"

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

        is_special = False
        for special_var_pattern in SPECIAL_VARIABLES.keys() :
            if re.match(special_var_pattern, var_name) :
                vars_to_process_last.append(var_name)
                is_special = True

        # if the variable isn't a special case, process it now
        if not is_special :
            # get the variable shape
            shape_temp = in_file_info[VAR_INFO_KEY][var_name][SHAPE_KEY]

            # if it isn't a special var and it's 2 sized, then we expect (lines, elements)
            if len(shape_temp) is 2 :

                if lines_num is None :
                    lines_num = shape_temp[0]
                    dimensions[LINES_DIM_NAME] = lines_num
                else :
                    assert (lines_num == shape_temp[0])

                if elements_num is None :
                    elements_num = shape_temp[1]
                    dimensions[ELEMS_DIM_NAME] = elements_num
                else :
                    assert (elements_num == shape_temp[1])

                variable_dim_info[var_name] = (LINES_DIM_NAME, ELEMS_DIM_NAME)

            else :
                LOG.warn("Unexpected dimensions for variable " + var_name + " of " + str(shape_temp) + ".")

    # now match up any special variables
    for var_name in vars_to_process_last :

        expected_dims_size  = None
        expected_dims_names = None
        for special_var_pattern in SPECIAL_VARIABLES.keys() :

            if re.match(special_var_pattern, var_name) :

                expected_dims_size  = SPECIAL_VARIABLES[special_var_pattern][0]
                expected_dims_names = SPECIAL_VARIABLES[special_var_pattern][1]

        # todo, handle the failure case more gently
        assert (expected_dims_names is not None)

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
        out_var_obj = out_file.createVariable(var_name, data_type, variable_dimensions_info[var_name], fill_value=fill_value_temp)
        out_var_obj.set_auto_maskandscale(False)

        # set the variable attributes
        for attr_key in variable_attr_info.keys() :
            if attr_key != "_FillValue" :
                setattr(out_var_obj, attr_key, variable_attr_info[attr_key])

        # set the variable data
        out_var_obj[:] = raw_data

    return out_file

def main():
    import argparse

    # TODO, the usage is not described the way I would like on the command line, it's missing the list of commands

    # create the argument parser
    parser = argparse.ArgumentParser(description='Manage input for geo_converter.')

    # TODO, the order of the arguments is currently important, can I fix this?

    # add arguments to represent user command line options
    parser.add_argument('command', type=str, nargs=1, default=None,
                        help='which command you want to execute in the converter')
    parser.add_argument('files', type=str, nargs=argparse.REMAINDER,
                        help='file or list of files to be processed') # todo, option to load all files from directories
    parser.add_argument('-o', '--out', dest='out', type=str, default="./",
                        help='the path to the output directory') # todo, add creation of output directory if it doesn't exist
    parser.add_argument('-v', '--version', dest='version', action='store_true', default=False,
                        help='display the version number of the installed version of the program')

    # FUTURE todo, add command line options to handle logging levels and data aggregation

    # parse the arguments
    args = parser.parse_args()

    # TODO, set up the appropriate argparse options to configure logging
    # set up the logging level based on the options the user selected on the command line
    lvl = logging.DEBUG #logging.WARNING
    #if options.debug: lvl = logging.DEBUG
    #elif options.verbose: lvl = logging.INFO
    #elif options.quiet: lvl = logging.ERROR
    logging.basicConfig(level = lvl)

    # display the version
    if args.version :
        print ("geo_converter version " + str(VERSION) + '\n')

    commands = {}
    prior = None
    prior = dict(locals())

    """
    The following functions represent available command selections.
    """

    def hdf4_2_netcdf4(args):
        """convert Geocat output hdf4 file(s) to netcdf4 file(s)
        Given a list of files that are output hdf4 files from Geocat,
        convert them to netcdf4 files and save them in the output directory.
        """

        # warn the user if no files were given as input
        if len(args.files) <= 0 :
            LOG.warn("No files were listed in the command line input. No file processing will be done.")

        # process each file the user wants converted separately
        for file_path in args.files :

            # make sure the path is fully expanded
            clean_file_path = clean_path(file_path)

            # check that the output directory and the input directories are not the same
            # (or will these be the same sometimes?)
            in_dir  = os.path.split(clean_file_path)[0]
            in_file_name = os.path.split(clean_file_path)[1]
            out_dir = clean_path(args.out)
            if in_dir == out_dir :
                LOG.warn("Output file will be placed in the same directory used for input: " + in_dir)

            # check to make sure the file exists
            if os.path.exists(clean_file_path) :

                # check that the file is of the correct type
                file_ext = os.path.splitext(os.path.split(clean_file_path)[-1])[-1][1:]
                if file_ext in INPUT_TYPES :

                    LOG.info("Attempting to convert file: " + clean_file_path)

                    # extract file information
                    in_file_info, in_file_object = read_hdf4_info(clean_file_path)

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

                else:
                    LOG.warn("File type (" + file_ext + ") is not the expected input type for this program. "
                             "File path will not be converted: " + clean_file_path)
            else :
                LOG.warn("Unable to process input because file does not exist. " +
                         "File path will not be converted: " + clean_file_path)

    def help(command=None):
        """print help for a specific command or list of commands
        e.g. help stats
        """
        if command is None:
            # print first line of docstring
            for cmd in commands:
                ds = commands[cmd].__doc__.split('\n')[0]
                print "%-16s %s" % (cmd,ds)
        else:
            print commands[command].__doc__

    # all the local public functions are considered part of glance, collect them up
    commands.update(dict(x for x in locals().items() if x[0] not in prior))

    # if what the user asked for is not one of our existing functions, print the help
    if (args.command[0] is None) or (args.command[0] not in commands):
        parser.print_help()
        help()
        return 9
    else:
        # call the function the user named, given the arguments from the command line
        rc = locals()[args.command[0]](args)
        return 0 if rc is None else rc

    return 0 # it shouldn't be possible to get here any longer

if __name__=='__main__':
    sys.exit(main())