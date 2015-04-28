#!/usr/bin/env python
# encoding: utf-8
"""

Useful constants.


Created by evas April 2015.
Copyright (c) 2015 University of Wisconsin SSEC. All rights reserved.
"""

# dimension names
LINES_DIM_NAME          = "lines"
ELEMS_DIM_NAME          = "elements"
DETECTOR_DIM_NAME       = "detector"
CHANNEL_IDX_DIM_NAME    = "channel_index"
QF_DEPTH_DIM_NAME       = "qf_depth"
PACKED_BYTES_1_DIM_NAME = "packed_bytes_1"
PACKED_BYTES_2_DIM_NAME = "packed_bytes_2"
TEMP_DIM_NAME           = "temp_dim_"

# a list of variables of special dimensions, with their expected shape and dimension names
# TODO, should this go somewhere else?
SPECIAL_VARIABLES = {
                        r".*?_planck"            :   [(None, 16),       (DETECTOR_DIM_NAME, CHANNEL_IDX_DIM_NAME)],
                        r"calibration_.*?"       :   [(None, 16),       (DETECTOR_DIM_NAME, CHANNEL_IDX_DIM_NAME)],
                        r".*?_wavenumber"        :   [(None, 16),       (DETECTOR_DIM_NAME, CHANNEL_IDX_DIM_NAME)],
                        r"scan_line_time"        :   [(None,),          (LINES_DIM_NAME,)],
                        r".*?_quality_flags1"    :   [(None, None, 3),  (LINES_DIM_NAME, ELEMS_DIM_NAME, QF_DEPTH_DIM_NAME)],
                        r".*?_cloud_mask_packed" :   [(None, None, 7),  (LINES_DIM_NAME, ELEMS_DIM_NAME, PACKED_BYTES_1_DIM_NAME)],
                        r".*?_cloud_type_packed" :   [(None, None, 6),  (LINES_DIM_NAME, ELEMS_DIM_NAME, PACKED_BYTES_2_DIM_NAME)],
                    }

# file input and output type related constants
INPUT_TYPES     = ['hdf']
OUT_FILE_SUFFIX = ".nc"

# keys for managing information about the input file
GLOBAL_ATTRS_KEY = "global_attributes"
VAR_LIST_KEY     = "variable_list"
VAR_INFO_KEY     = "variable_info"
SHAPE_KEY        = "shape"
VAR_ATTRS_KEY    = "attributes"