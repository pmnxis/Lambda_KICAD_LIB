#!/usr/bin/env python3

import sys
import os
import math

sys.path.append(os.path.join(sys.path[0], "kicad-footprint-generator")) # to import `KicadModTree`
sys.path.append(os.path.join(sys.path[0], "kicad-footprint-generator", "scripts", "tools")) # to load `footprint_scripts_pin_headers.py`

from KicadModTree import *  # NOQA
from modified_footprint_scripts_pin_headers import * # Custom

# 3220-XX-0100-00

def gen_3220_XX_0100_00():
    tags_additional = []
    extra_description = 'http://www.cnctech.us/pdfs/3220-XX-0100-00_.pdf'

    rm=1.27
    cm=1.27
    cols = 2
    ddrill=0.65 # datasheet recommendation was 0.7, but include max margin of error, sqrt((0.42**2)*2)=0.5939
    pad=[1,1] #[1.7,1.7]
    
    orientation='Vertical'
    latching = False
    body_width=5
    body_overlen=3.81 # (Dim.C-(1.27*(rows-1)))/2
    body_offset=0
    mating_overlen=3.01 
    wall_thickness=0.8  # (Dim.C-Dim.B)/2
    notch_width=2.1
    latch_lengths=0 # no latch
    latch_width=0 # no latch
    # latch_lengths = [0,6.5,9.5,12] # these values roughly represent the referenced parts with the latch open
    # latch_width=4.4 # large enough to handle all referenced parts and measured empirically
    mh_ddrill=0 # no mount-hole
    mh_pad=[0,0] # no mount-hole
    mh_overlen=0 # no mount-hole
    mh_offset=0 # no mount-hole
    mh_number='MP' # no mount-hole
    part_num_left_left = "CNCTech_IDC-Header_"
    part_num_left = "3220-"
    part_num_right = "-0100"

    for rows in [3,4,5,6,7,8,10,12,13,15,17,20,22,25,30,38]:
        # for latch_len in latch_lengths:
        offset3d = [0.65 / 25.4, (-2.54-((rows-5)*(0.635))) / 25.4, 2.54 / 25.4]
        rotate3d = [0, -180, 180]
        for mh_ddrill, mh_pad, mh_overlen in zip([0, mh_ddrill], [[0,0], mh_pad], [0, mh_overlen]):
        #for mh_ddrill, mh_pad, mh_overlen in zip([0], [[0,0]], [0]):
            part_num = "%s%s%02u%s" % (part_num_left_left, part_num_left, rows*cols, part_num_right)
            class_desc = "IDC header %s%02u%s" % (part_num_left, rows*cols, part_num_right)
            file_name = "3220-%02u-0100-00 3D.stp" %  (rows*cols)
            makeIdcHeaderCustom(rows, cols, rm, cm, body_width,
                                body_overlen, body_overlen, body_offset,
                                ddrill, pad,
                                mating_overlen, wall_thickness, notch_width,
                                orientation, latching,
                                latch_lengths, latch_width,
                                mh_ddrill, mh_pad, mh_overlen, mh_offset, mh_number,
                                tags_additional, extra_description, "Connector_IDC_1.27mm_Extended",
                                part_num, class_desc, offset3d, [1, 1, 1], rotate3d,
                                "${LAMBDA_LIB_DIR}/3DShapes/", "../../PcbLib/", "", file_name)

def gen_3220_XX_0200_00():
    tags_additional = []
    extra_description = 'http://www.cnctech.us/pdfs/3220-XX-0200-00_.pdf'

    rm=1.27
    cm=1.27
    cols = 2
    ddrill=0.65 # datasheet recommendation was 0.7, but include max margin of error, sqrt((0.42**2)*2)=0.5939
    pad=[1,1] #[1.7,1.7]
    
    orientation='Vertical'
    latching = False
    body_width=5
    body_overlen=3.81 # (Dim.C-(1.27*(rows-1)))/2
    body_offset=0
    mating_overlen=3.01 
    wall_thickness=0.8  # (Dim.C-Dim.B)/2
    notch_width=2.1
    latch_lengths=0 # no latch
    latch_width=0 # no latch
    # latch_lengths = [0,6.5,9.5,12] # these values roughly represent the referenced parts with the latch open
    # latch_width=4.4 # large enough to handle all referenced parts and measured empirically
    mh_ddrill=0 # no mount-hole
    mh_pad=[0,0] # no mount-hole
    mh_overlen=0 # no mount-hole
    mh_offset=0 # no mount-hole
    mh_number='MP' # no mount-hole

    orientation='Horizontal'
    body_offset=2.07 # distance from pin 1 row to the closest edge of the plastic body
    part_num_left_left = "CNCTech_IDC-Header_"
    part_num_left = "3220-"
    part_num_right = "-0200"

    for rows in [3,4,5,6,7,8,10,12,13,15,17,20,22,25,30,38]:
        # for latch_len in latch_lengths:
        offset3d = [4.6 / 25.4, (-2.3-((rows-5)*(0.635))) / 25.4, 2.54 / 25.4]
        rotate3d = [0, -90, 180]
        for mh_ddrill, mh_pad, mh_overlen in zip([0, mh_ddrill], [[0,0], mh_pad], [0, mh_overlen]):
        #for mh_ddrill, mh_pad, mh_overlen in zip([0], [[0,0]], [0]):
            part_num = "%s%s%02u%s" % (part_num_left_left, part_num_left, rows*cols, part_num_right)
            class_desc = "IDC header %s%02u%s" % (part_num_left, rows*cols, part_num_right)
            file_name = "3220-%02u-0200-00 3D.stp" %  (rows*cols)
            makeIdcHeaderCustom(rows, cols, rm, cm, body_width,
                                body_overlen, body_overlen, body_offset,
                                ddrill, pad,
                                mating_overlen, wall_thickness, notch_width,
                                orientation, latching,
                                latch_lengths, latch_width,
                                mh_ddrill, mh_pad, mh_overlen, mh_offset, mh_number,
                                tags_additional, extra_description, "Connector_IDC_1.27mm_Extended",
                                part_num, class_desc, offset3d, [1, 1, 1], rotate3d,
                                "${LAMBDA_LIB_DIR}/3DShapes/", "../../PcbLib/", "", file_name)

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='use confing .yaml files to create footprints.')
    # parser.add_argument('--global_config', type=str, nargs='?', help='the config file defining how the footprint will look like. (KLC)', default='./config_KLCv3.0.yaml')
    # parser.add_argument('--series_config', type=str, nargs='?', help='the config file defining series parameters.', default='./conn_config_KLCv3.yaml')
    # args = parser.parse_args()

    # with open(args.global_config, 'r') as config_stream:
    #     try:
    #         configuration = yaml.safe_load(config_stream)
    #     except yaml.YAMLError as exc:
    #         print(exc)

    # with open(args.series_config, 'r') as config_stream:
    #     try:
    #         configuration.update(yaml.safe_load(config_stream))
    #     except yaml.YAMLError as exc:
    #         print(exc)
    # for pins_per_row in pins_per_row_range:
    #     generate_one_footprint(pins_per_row, configuration)
    # gen_3220_XX_0100_00()
    gen_3220_XX_0200_00()

