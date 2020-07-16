import sys
import os
from math import sqrt
import argparse
import yaml
from KicadModTree import *

def _roundToBase(value, base):
    return round(value/base) * base

def _getTextFieldDetails(field_definition, body_edges, courtyard, text_y_inside_position = 'center', allow_rotation = False):
    body_size = [body_edges['right'] - body_edges['left'], body_edges['bottom'] - body_edges['top']]
    body_center = [(body_edges['right'] + body_edges['left'])/2, (body_edges['bottom'] + body_edges['top'])/2]

    position_y = field_definition['position_y']
    at = body_center.copy()


    if body_size[0] < body_size[1] and allow_rotation and position_y == 'inside':
        rotation = 1
    else:
        rotation = 0

    if 'size' in field_definition:
        size = field_definition['size']
        fontwidth = field_definition['fontwidth']
    elif 'size_min' in field_definition and 'size_max' in field_definition:
        # We want at least 3 char reference designators space. If we can't fit these we move the reverence to the outside.
        size_max = field_definition['size_max']
        size_min = field_definition['size_min']
        if body_size[rotation] >= 4*size_max[1]:
            if body_size[0] >= 4*size_max[1]:
                rotation = 0
            size = size_max
        elif body_size[rotation] < 4*size_min[1]:
            size = size_min
            if body_size[rotation] < 3*size_min[1]:
                if position_y == 'inside':
                    rotation = 0
                    position_y = 'outside_top'
        else:
            fs = _roundToBase(body_size[rotation]/4, 0.01)
            size = [fs, fs]

        if size[1] > body_size[(rotation+1)%2]-0.2:
            fs = max(body_size[(rotation+1)%2]-0.2, size_min[1])
            size = [fs, fs]

        fontwidth = _roundToBase(field_definition['thickness_factor']*size[0], 0.01)
    else:
        rotation = 0
        position_y = 'outside_top'
        size = [1,1]
        fontwidth = 0.15

    if position_y == 'inside':
        if text_y_inside_position == 'top':
            position_y = 'inside_top'
        elif text_y_inside_position == 'bottom':
            position_y = 'inside_bottom'
        elif text_y_inside_position == 'left':
            position_y = 'inside_left'
        elif text_y_inside_position == 'right':
            position_y = 'inside_right'
        elif isinstance(text_y_inside_position,int) or isinstance(text_y_inside_position,float):
            at[1] = text_y_inside_position

    text_edge_offset = size[0]/2+0.2
    if position_y == 'outside_top':
        at = [body_center[0], courtyard['top']-text_edge_offset]
    elif position_y == 'inside_top':
        at = [body_center[0], body_edges['top']+text_edge_offset]
    elif position_y == 'inside_left':
        at = [body_edges['left'] + text_edge_offset, body_center[1]]
        rotation = 1
    elif position_y == 'inside_right':
        at = [body_edges['right'] - text_edge_offset, body_center[1]]
        rotation = 1
    elif position_y == 'outside_bottom':
        at = [body_center[0], courtyard['bottom']+text_edge_offset]
    elif position_y == 'inside_bottom':
        at = [body_center[0], body_edges['bottom']-text_edge_offset]


    at = [_roundToBase(at[0],0.01), _roundToBase(at[1],0.01)]
    return {'at': at, 'size': size, 'layer': field_definition['layer'], 'thickness': fontwidth, 'rotation': rotation*90}

def addTextFields(kicad_mod, configuration, body_edges, courtyard, fp_name, text_y_inside_position = 'center', allow_rotation = False):
    reference_fields = configuration['references']
    kicad_mod.append(Text(type='reference', text='REF**',
        **_getTextFieldDetails(reference_fields[0], body_edges, courtyard, text_y_inside_position, allow_rotation)))

    for additional_ref in reference_fields[1:]:
        kicad_mod.append(Text(type='user', text='%R',
        **_getTextFieldDetails(additional_ref, body_edges, courtyard, text_y_inside_position, allow_rotation)))

    value_fields = configuration['values']
    kicad_mod.append(Text(type='value', text=fp_name,
        **_getTextFieldDetails(value_fields[0], body_edges, courtyard, text_y_inside_position, allow_rotation)))

    for additional_value in value_fields[1:]:
        kicad_mod.append(Text(type='user', text='%V',
            **_getTextFieldDetails(additional_value, body_edges, courtyard, text_y_inside_position, allow_rotation)))


def roundToBase(value, base):
    if base == 0:
        return value
    return round(value/base) * base

series = 'MicroBlade'
series_long = 'MicroBlade Connector System'
manufacturer = 'Molex'
orientation = 'V'
number_of_rows = 1
datasheet = 'https://www.molex.com/pdm_docs/sd/530140410_sd.pdf'

pins_per_row_range = range(2, 15)

part_code = "53014-{n:02}00"

pitch = 2.0
drill = 0.9

pad_to_pad_clearance = 0.4
annular_ring = 1.4-0.8

pad_size = [pitch - pad_to_pad_clearance, drill + 2*annular_ring]
pad_shape=Pad.SHAPE_OVAL
if pad_size[1] == pad_size[0]:
    pad_shape=Pad.SHAPE_CIRCLE

stp_dir = '${LAMBDA_LIB_DIR}/3DShapes/Connector_Extended_Molex_53014.3dshapes/'
stp_name = "53014{n:02}10.stp"


def generate_one_footprint(pins_per_row, configuration):
    mpn = part_code.format(n=pins_per_row*number_of_rows)

    # handle arguments
    orientation_str = configuration['orientation_options'][orientation]
    footprint_name = configuration['fp_name_format_string'].format(man=manufacturer,
        series=series,
        mpn=mpn, num_rows=number_of_rows, pins_per_row=pins_per_row, mounting_pad = "",
        pitch=pitch, orientation=orientation_str)

    kicad_mod = Footprint(footprint_name)
    kicad_mod.setDescription("Molex {:s}, {:s}, {:d} Pins per row ({:s}), footgen".format(series_long, mpn, pins_per_row, datasheet))
    kicad_mod.setTags(configuration['keyword_fp_string'].format(series=series,
        orientation=orientation_str, man=manufacturer,
        entry=configuration['entry_direction'][orientation]))

    A = (pins_per_row - 1) * pitch
    B = A + 2*1.75
    C = A + 2*2.45

    #connector width
    W = 4.35
    chamfer_pin_n = {'x': 1, 'y': 1}

    off = configuration['silk_fab_offset']
    pad_silk_off = configuration['silk_pad_clearance'] + configuration['silk_line_width']/2

    body_edge={}
    body_edge['left'] = -2.56
    body_edge['right'] = pitch * (pins_per_row - 1) + 1.44
    body_edge['top'] = 1.65 - 4.35
    body_edge['bottom'] = 1.65

    bounding_box = body_edge.copy()

    # generate the pads
    optional_pad_params = {}
    #if configuration['kicad4_compatible']:
    #    optional_pad_params['tht_pad1_shape'] = Pad.SHAPE_RECT
    #else:
    optional_pad_params['tht_pad1_shape'] = Pad.SHAPE_ROUNDRECT

    kicad_mod.append(PadArray(start=[0,0], pincount=pins_per_row, x_spacing=pitch,
        type=Pad.TYPE_THT, shape=pad_shape, size=pad_size, drill=drill,
        layers=Pad.LAYERS_THT,
        **optional_pad_params))

    def generateOutline(off = 0, grid = 0):
        poly = [
                {'x': body_edge['left']-off, 'y':body_edge['top']-off},
                {'x': body_edge['left']-off, 'y':body_edge['bottom']+off},
                {'x': body_edge['right']-chamfer_pin_n['x']+off, 'y':body_edge['bottom']+off},
                {'x': body_edge['right']+off, 'y':body_edge['bottom']-chamfer_pin_n['y']+off},
                {'x': body_edge['right']+off, 'y':body_edge['top']-off},
                {'x': body_edge['left']-off, 'y':body_edge['top']-off},
            ]
        if grid == 0:
            return poly
        else:
            return [{'x':roundToBase(p['x'], grid), 'y':roundToBase(p['y'], grid)} for p in poly]

    # outline on Fab
    kicad_mod.append(PolygoneLine(polygone=generateOutline(),
        layer='F.Fab', width=configuration['fab_line_width']))

    # outline on SilkScreen
    kicad_mod.append(PolygoneLine(polygone=generateOutline(off=off),
        layer='F.SilkS', width=configuration['silk_line_width']))

    #pin-1 mark
    sl=2
    o = off + 0.3
    pin = [
        {'y': body_edge['bottom'] - sl, 'x': body_edge['left'] - o},
        {'y': body_edge['bottom'] + o, 'x': body_edge['left'] - o},
        {'y': body_edge['bottom'] + o, 'x': body_edge['left'] + sl}
    ]
    kicad_mod.append(PolygoneLine(polygone=pin,
        layer='F.SilkS', width=configuration['silk_line_width']))

    sl=1
    pin = [
        {'y': body_edge['bottom'], 'x': -sl/2},
        {'y': body_edge['bottom'] - sl/sqrt(2), 'x': 0},
        {'y': body_edge['bottom'], 'x': sl/2}
    ]
    kicad_mod.append(PolygoneLine(polygone=pin,
        width=configuration['fab_line_width'], layer='F.Fab'))

    ########################### CrtYd #################################
    poly_crtyd = generateOutline(configuration['courtyard_offset']['connector'], configuration['courtyard_grid'])
    cy1 = poly_crtyd[0]['y']
    cy2 = poly_crtyd[1]['y']
    kicad_mod.append(PolygoneLine(
        polygone=poly_crtyd,
        layer='F.CrtYd', width=configuration['courtyard_line_width']))

    ######################### Text Fields ###############################
    addTextFields(kicad_mod=kicad_mod, configuration=configuration, body_edges=body_edge,
        courtyard={'top':cy1, 'bottom':cy2},
        fp_name=footprint_name, text_y_inside_position='top')

    ##################### Output and 3d model ############################
   # model3d_path_prefix = configuration.get('3d_model_prefix','${KISYS3DMOD}/')

    # 여기 수정해야함.
    lib_name = configuration['lib_name_format_string'].format(series=series, man=manufacturer)
    #model_name = '{model3d_path_prefix:s}{lib_name:s}.3dshapes/{fp_name:s}.wrl'.format(
    #    model3d_path_prefix=model3d_path_prefix, lib_name=lib_name, fp_name=footprint_name)
    model_path = stp_dir + stp_name.format(n=pins_per_row*number_of_rows)
    model_data = Model(filename=model_path, offset=[(0.4+((pins_per_row-2)*pitch/2)), 0.5, 3.0], scale=[1,1,1], rotate=[180, 180, 0])
    kicad_mod.append(model_data)
    print(model_data)
    # output_dir = '{lib_name:s}.pretty/'.format(lib_name=lib_name)
    output_dir = './tmp/'
    if not os.path.isdir(output_dir): #returns false if path does not yet exist!! (Does not check path validity)
        os.makedirs(output_dir)
    filename =  '{outdir:s}{fp_name:s}.kicad_mod'.format(outdir=output_dir, fp_name=footprint_name)

    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile(filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='use confing .yaml files to create footprints.')
    parser.add_argument('--global_config', type=str, nargs='?', help='the config file defining how the footprint will look like. (KLC)', default='./config_KLCv3.0.yaml')
    parser.add_argument('--series_config', type=str, nargs='?', help='the config file defining series parameters.', default='./conn_config_KLCv3.yaml')
    args = parser.parse_args()

    with open(args.global_config, 'r') as config_stream:
        try:
            configuration = yaml.safe_load(config_stream)
        except yaml.YAMLError as exc:
            print(exc)

    with open(args.series_config, 'r') as config_stream:
        try:
            configuration.update(yaml.safe_load(config_stream))
        except yaml.YAMLError as exc:
            print(exc)
    for pins_per_row in pins_per_row_range:
        generate_one_footprint(pins_per_row, configuration)