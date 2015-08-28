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
PACKED_BYTES_1_DIM_NAME = "bytes_cloud_mask_packed"
PACKED_BYTES_2_DIM_NAME = "bytes_cloud_type_packed"
TEMP_DIM_NAME           = "temp_dim_"

# a list of variables of special dimensions, with their expected shape and dimension names
SPECIAL_VARIABLES = {
                        r".*?_planck"            :   [(None, None),     (DETECTOR_DIM_NAME, CHANNEL_IDX_DIM_NAME)],
                        r"calibration_.*?"       :   [(None, None),     (DETECTOR_DIM_NAME, CHANNEL_IDX_DIM_NAME)],
                        r".*?_wavenumber"        :   [(None, None),     (DETECTOR_DIM_NAME, CHANNEL_IDX_DIM_NAME)],
                        r"scan_line_time"        :   [(None,),          (LINES_DIM_NAME,)],
                        r".*?_quality_flags1"    :   [(None, None, 3),  (LINES_DIM_NAME, ELEMS_DIM_NAME, QF_DEPTH_DIM_NAME)],
                        r".*?_cloud_mask_packed" :   [(None, None, 7),  (LINES_DIM_NAME, ELEMS_DIM_NAME, PACKED_BYTES_1_DIM_NAME)],
                        r".*?_cloud_type_packed" :   [(None, None, 6),  (LINES_DIM_NAME, ELEMS_DIM_NAME, PACKED_BYTES_2_DIM_NAME)],
                    }

# file input and output type related constants
INPUT_TYPES      = ['hdf']
OUT_FILE_SUFFIX  = ".nc"

# keys for managing information about the input file
GLOBAL_ATTRS_KEY = "global_attributes"
VAR_LIST_KEY     = "variable_list"
VAR_INFO_KEY     = "variable_info"
SHAPE_KEY        = "shape"
VAR_ATTRS_KEY    = "attributes"

# attribute name keys
FILL_VALUE_KEY   = "_FillValue"

# constants for the process of making the file more CF compliant
IMAGE_DATE_ATTR_NAME     = "Image_Date"
IMAGE_TIME_ATTR_NAME     = "Image_Time"
IMAGE_DATETIME_ATTR_NAME = "Image_Date_Time"
ISO_OUT_TIME_FORMAT      = "%Y-%m-%dT%H:%M:%SZ" # the format for ISO standard datetime
LIB_VERSION_ATTR_NAME    = "Output_Library_Version"
SCAN_LINE_TIME_VAR_NAME  = "scan_line_time"
VARS_TO_DELETE           = [SCAN_LINE_TIME_VAR_NAME,] # variables to remove from the file
BAD_UNITS_SET            = set(["no units", "none"])
CONVERT_ATTRS_MAP        = {    # this is a map of old attribute values to their new converted values
                                "mWm-2sr-1(cm-1)-1": "mW m-2 sr-1 (cm-1)-1", # for the things with units of "mWm-2sr-1(cm-1)-1" change it to "mW m-2 sr-1 (cm-1)-1"
                           }
LONG_NAME_ATTR_NAME      = "long_name"
STANDARD_NAME_ATTR_NAME  = "standard_name"
VALID_MIN_ATTR_NAME      = "valid_min"
VALID_MAX_ATTR_NAME      = "valid_max"
VALID_RANGE_ATTR_NAME    = "valid_range"
ANC_VARS_ATTR_NAME       = "ancillary_variables"
FLAG_VALS_ATTR_NAME      = "flag_values"
FLAG_MEANINGS_ATTR_NAME  = "flag_meanings"
CH_REFL_VAR_PATTERN      = r"(.+?)_channel_(\d+?)_reflectance"
CH_EMIS_VAR_PATTERN      = r"(.+?)_channel_(\d+?)_emissivity"
CH_BT_VAR_PATTERN        = r"(.+?)_channel_(\d+?)_brightness_temperature"
CHANNEL_DATA_PATTERNS    = set([CH_REFL_VAR_PATTERN, CH_EMIS_VAR_PATTERN, CH_BT_VAR_PATTERN])
LONG_NAME_MAP            = \
        {
            "bc1_planck":                   "calibration coefficients “a”, for each channel",
            "bc2_planck":                   "calibration coefficients “b”, for each channel",
            "calibration_offset":           "calibration constant offset",
            "calibration_slope":            "calibration constant slope",
            "calibration_slope_degrade":    "calibration constant slope degrade",
            "calibration_solar_constant":   "calibration constant solar constant",
            "channel_wavenumber":           "instrument-specific wavenumbers, for each channel",
            "fk1_planck":                   "planck constant 1",
            "fk2_planck":                   "planck constant 2",
            CH_REFL_VAR_PATTERN:            "pixel-resolution array of reflectances for channel %s from %s", # %s's represent channel number and instrument
            CH_EMIS_VAR_PATTERN:            "pixel-resolution array of emissivities for channel %s from %s", # %s's represent channel number and instrument
            CH_BT_VAR_PATTERN:              "pixel-resolution array of brightness temperatures for channel %s from %s", # %s's represent channel number and instrument
            "pixel_ecosystem_type":         "pixel-resolution array of ecosystem types, from a static ancillary file.",
            "pixel_latitude":               "pixel-resolution array of latitudes",
            "pixel_longitude":              "pixel-resolution array of longitudes",
            "pixel_relative_azimuth_angle": "pixel-resolution array of relative azimuth angles",
            "pixel_satellite_zenith_angle": "pixel-resolution array of satellite zenith angles",
            "pixel_solar_zenith_angle":     "pixel-resolution array of solar zenith angles",
            "pixel_surface_type":           "pixel-resolution array of surface types, from a static ancillary file.",
            "nwp_x_index":                  "the x indices into the NWP data array that correspond with each pixel, "
                                            "or fill values if NWP data was not read in",
            "nwp_y_index":                  "the y indices into the NWP data array that correspond with each pixel, "
                                            "or fill values if NWP data was not read in",
        }
SHORT_RANGE_DEFAULT      = [-32768, 32767]
RANGE_LIMS_MAP           = \
        {
            CH_REFL_VAR_PATTERN:                        [-32767, 32767],
            CH_BT_VAR_PATTERN:                          [-32767, 32767],
            "pixel_ecosystem_type":                     [0, 100],
            "pixel_relative_azimuth_angle":             [-32767, 32767],
            "pixel_satellite_zenith_angle":             [-32767, 32767],
            "pixel_solar_zenith_angle":                 [-32767, 32767],
            "pixel_surface_type":                       [0, 13],
        }
FLAG_INFO_MAP            = \
        {
            "pixel_ecosystem_type":
                            {
                                # from table 27 in the Geocat manual
                                FLAG_VALS_ATTR_NAME:    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 100],
                                FLAG_MEANINGS_ATTR_NAME: ["INTERRUPTED_AREAS_ECO", "URBAN_ECO", "LOW_SPARSE_GRASSLAND_ECO", "CONIFEROUS_FOREST_ECO", "DECIDUOUS_CONIFER_FOREST_ECO", "DECIDUOUS_BROADLEAF_FOREST1_ECO", "EVERGREEN_BROADLEAF_FORESTS_ECO", "TALL_GRASSES_AND_SHRUBS_ECO", "BARE_DESERT_ECO", "UPLAND_TUNDRA_ECO", "IRRIGATED_GRASSLAND_ECO", "SEMI_DESERT_ECO", "GLACIER_ICE_ECO", "WOODED_WET_SWAMP_ECO", "INLAND_WATER_ECO", "SEA_WATER_ECO", "SHRUB_EVERGREEN_ECO", "SHRUB_DECIDUOUS_ECO", "MIXED_FOREST_AND_FIELD_ECO", "EVERGREEN_FOREST_AND_FIELDS_ECO", "COOL_RAIN_FOREST_ECO", "CONIFER_BOREAL_FOREST_ECO", "COOL_CONIFER_FOREST_ECO", "COOL_MIXED_FOREST_ECO", "MIXED_FOREST_ECO", "COOL_BROADLEAF_FOREST_ECO", "DECIDUOUS_BROADLEAF_FOREST2_ECO", "CONIFER_FOREST_ECO", "MONTANE_TROPICAL_FORESTS_ECO", "SEASONAL_TROPICAL_FOREST_ECO", "COOL_CROPS_AND_TOWNS_ECO", "CROPS_AND_TOWN_ECO", "DRY_TROPICAL_WOODS_ECO", "TROPICAL_RAINFOREST_ECO", "TROPICAL_DEGRADED_FOREST_ECO", "CORN_AND_BEANS_CROPLAND_ECO", "RICE_PADDY_AND_FIELD_ECO", "HOT_IRRIGATED_CROPLAND_ECO", "COOL_IRRIGATED_CROPLAND_ECO", "COLD_IRRIGATED_CROPLAND_ECO", "COOL_GRASSES_AND_SHRUBS_ECO", "HOT_AND_MILD_GRASSES_AND_SHRUBS_ECO", "COLD_GRASSLAND_ECO", "SAVANNA_ECO", "MIRE_BOG_FEN_ECO", "MARSH_WETLAND_ECO", "MEDITERRANEAN_SCRUB_ECO", "DRY_WOODY_SCRUB_ECO", "DRY_EVERGREEN_WOODS_ECO", "VOLCANIC_ROCK_ECO", "SAND_DESERT_ECO", "SEMI_DESERT_SHRUBS_ECO", "SEMI_DESERT_SAGE_ECO", "BARREN_TUNDRA_ECO", "COOL_SOUTHERN_HEMISPHERE_MIXED_FORESTS_ECO", "COOL_FIELDS_AND_WOODS_ECO", "FOREST_AND_FIELD_ECO", "COOL_FOREST_AND_FIELD_ECO", "FIELDS_AND_WOODY_SAVANNA_ECO", "SUCCULENT_AND_THORN_SCRUB_ECO", "SMALL_LEAF_MIXED_WOODS_ECO", "DECIDUOUS_AND_MIXED_BOREAL_FOREST_ECO", "NARROW_CONIFERS_ECO", "WOODED_TUNDRA_ECO", "HEATH_SCRUB_ECO", "COASTAL_WETLAND_NW_ECO", "COASTAL_WETLAND_NE_ECO", "COASTAL_WETLAND_SE_ECO", "COASTAL_WETLAND_SW_ECO", "POLAR_AND_ALPINE_DESERT_ECO", "GLACIER_ROCK_ECO", "SALT_PLAYAS_ECO", "MANGROVE_ECO", "WATER_AND_ISLAND_FRINGE_ECO", "LAND_WATER_AND_SHORE_ECO", "LAND_AND_WATER_RIVERS_ECO", "CROP_AND_WATER_MIXTURES_ECO", "SOUTHERN_HEMISPHERE_CONIFERS_ECO", "SOUTHERN_HEMISPHERE_MIXED_FOREST_ECO", "WET_SCLEROPHYLIC_FOREST_ECO", "COASTLINE_FRINGE_ECO", "BEACHES_AND_DUNES_ECO", "SPARSE_DUNES_AND_RIDGES_ECO", "BARE_COASTAL_DUNES_ECO", "RESIDUAL_DUNES_AND_BEACHES_ECO", "COMPOUND_COASTLINES_ECO", "ROCKY_CLIFFS_AND_SLOPES_ECO", "SANDY_GRASSLAND_AND_SHRUBS_ECO", "BAMBOO_ECO", "MOIST_EUCALYPTUS_ECO", "RAIN_GREEN_TROPICAL_FOREST_ECO", "WOODY_SAVANNA_ECO", "BROADLEAF_CROPS_ECO", "GRASS_CROPS_ECO", "CROPS_GRASS_SHRUBS_ECO", "EVERGREEN_TREE_CROP_ECO", "DECIDUOUS_TREE_CROP_ECO", "NO_DATA_ECO"],
                            },
            "pixel_surface_type":
                            {
                                # from table 26 in the Geocat manual
                                FLAG_VALS_ATTR_NAME:    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
                                FLAG_MEANINGS_ATTR_NAME: ["WATER_SFC", "EVERGREEN_NEEDLE_SFC", "EVERGREEN_BROAD_SFC", "DECIDUOUS_NEEDLE_SFC", "DECIDUOUS_BROAD_SFC", "MIXED_FORESTS_SFC", "WOODLANDS_SFC", "WOODED_GRASS_SFC", "CLOSED_SHRUBS_SFC", "OPEN_SHRUBS_SFC", "GRASSES_SFC", "CROPLANDS_SFC", "BARE_SFC", "URBAN_SFC"],
                            },
        } #   (FUTURE: I need to review the information Geoff gave me about categories in the algorithm output to fill this out further.)

