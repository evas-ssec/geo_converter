#!/usr/bin/env python
# encoding: utf-8
"""

Top-level routines to convert Geocat output from hdf4 to netCDF4.


Created by evas April 2015.
Copyright (c) 2015 University of Wisconsin SSEC. All rights reserved.
"""

import os, sys, logging

# import the appropriate file handling modules
#import pycdf # TODO, for netCDF files, looks less maintained, remove once we confirm that netCDF4 works for our needs
import netCDF4                              # used to process output netCDF4 files
from pyhdf.SD import SD,SDC, SDS, HDF4Error # used to process input hdf4 files

LOG = logging.getLogger(__name__)

VERSION = 0.1

# TODO, these utility and file processing functions / constants should probably move to other files in the future

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

def main():
    import argparse

    # TODO, the usage is not described the way I would like on the command line, it's missing the list of commands

    # create the argument parser
    parser = argparse.ArgumentParser(description='Manage input for geo_converter.')

    # add arguments to represent user command line options
    parser.add_argument('command', type=str, nargs=1, default=None,
                        help='which command you want to execute in the converter')
    parser.add_argument('files', type=str, nargs=argparse.REMAINDER,
                        help='file or list of files to be processed') # todo, option to load all files from directories
    parser.add_argument('-o', '--out', dest='out', type=str,
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

        # TODO, check that the output directory and the input directories are not the same (or will these be the same sometimes?)

        # warn the user if no files were given as input
        if len(args.files) <= 0 :
            LOG.warn("No files were listed in the command line input. No file processing will be done.")

        # process each file the user wants converted separately
        for file_path in args.files :

            # make sure the path is fully expanded
            clean_file_path = clean_path(file_path)

            # check to make sure the file exists
            if os.path.exists(clean_file_path) :

                # check that the file is of the correct type
                file_ext = os.path.split(clean_file_path)[-1].split('.')[-1]
                if file_ext in INPUT_TYPES :

                    LOG.info("Attempting to convert file: " + clean_file_path)

                    # extract file information
                    in_file_info, in_file_object = read_hdf4_info(clean_file_path)

                    print("file info: " + str(file_info)) # TEMP for debugging

                    # TODO, make any changes needed for CF compliance

                    # TODO, create the output file

                    # TODO, write the appropriate data and attributes to the new file

                    # TODO, close both the old and new files
                    in_file_object.end()

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