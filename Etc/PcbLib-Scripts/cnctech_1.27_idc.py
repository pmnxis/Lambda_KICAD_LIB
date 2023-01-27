#!/usr/bin/env python3

import sys
import os
import math

sys.path.append(os.path.join(sys.path[0], "kicad-footprint-generator")) # to import `KicadModTree`
sys.path.append(os.path.join(sys.path[0], "kicad-footprint-generator", "scripts", "tools")) # to load `footprint_scripts_pin_headers.py`

from KicadModTree import *  # NOQA
from drawing_tools import *  # NOQA

# modified from footprint_scripts_pin_headers.py (kicad-footprint-generator.git)
def makeIdcHeaderCustomDescription(rows, cols, rm, coldist, body_width, overlen_top, overlen_bottom, body_offset, ddrill, pad,
                        mating_overlen, wall_thickness, notch_width,
                        orientation, latching,
                        latch_len=0, latch_width=0,
                        mh_ddrill=0, mh_pad=[0,0], mh_overlen=0, mh_offset=0, mh_number='MP',
                        tags_additional=[], extra_description=False, lib_name="Connector_IDC", classname="IDC-Header", classname_description="IDC box header", offset3d=[0, 0, 0], scale3d=[1, 1, 1],
                        rotate3d=[0, 0, 0], model3d_path_prefix="${KICAD7_3DMODEL_DIR}", custom_description=""):

    crt_offset = 0.5 # different for connectors
    txt_offset = 1
    slk_offset = 0.11    
    # If ddrill is zero, then create a SMD footprint:
    #     SMT pads are created.
    #     rm is row pitch
    #     coldist is pad pitch for columns

    pin_size = 0.64 # square pin side length; this appears to be the same for all connectors so use a fixed internal value
    
    mh_present = True if mh_ddrill > 0 and mh_pad[0] > 0 and mh_pad[1] > 0 and mh_overlen > 0 else False
    mh_y = [-mh_overlen, (rows - 1) * rm + mh_overlen]
    
    h_fab = (rows - 1) * rm + overlen_top + overlen_bottom
    w_fab = body_width
    if ddrill == 0:
        # Body should be centered for SMT footprints
        l_fab = - w_fab / 2 if body_offset == 0 else body_offset
        t_fab = -overlen_top - (rows-1)*rm/2
    else:
        l_fab = (coldist * (cols - 1) - w_fab) / 2 if body_offset == 0 else body_offset
        t_fab = -overlen_top
    
    h_slk = h_fab + 2 * slk_offset
    w_slk = max(w_fab + 2 * slk_offset, coldist * (cols - 1) - pad[0] - 4 * slk_offset)
    l_slk = (coldist * (cols - 1) - w_slk) / 2 if body_offset == 0 else body_offset
    t_slk = -overlen_top - slk_offset
    
    # these calculations are so tight that new body styles will probably break them
    h_crt = max(max(h_fab, (rows - 1) * rm + pad[1]) + 2 * latch_len, (rows - 1) * rm + 2 * mh_overlen + mh_pad[1]) + 2 * crt_offset
    w_crt = max(body_width, coldist * (cols - 1) + pad[0]) + 2 * crt_offset if body_offset <= 0 else pad[0] / 2 + body_offset + body_width + 2 * crt_offset
    if ddrill == 0:
        # Courtyard should be centered for SMT footprints
        l_crt =  -pad[0] / 2 - coldist/2- crt_offset
        t_crt = min(t_fab - latch_len, -mh_overlen - mh_pad[1] / 2) - crt_offset
    else:
        l_crt = l_fab - crt_offset if body_offset <= 0 else -pad[0] / 2 - crt_offset
        t_crt = min(t_fab - latch_len, -mh_overlen - mh_pad[1] / 2) - crt_offset
    #if orientation == 'Horizontal' and latching and mh_ddrill > 0:
    if mh_present and (mh_offset - mh_pad[0] / 2 < l_fab):
        # horizontal latching with mounting holes is a special case
        l_crt = mh_offset - mh_pad[0] / 2 - crt_offset
        w_crt = -l_crt + body_width + body_offset + crt_offset
    
    if ddrill == 0:
        # center is [0, 0] for SMD footprints
        center_fab = [0, 0]
        center_fp = [0,0]
    else:
        # center of the body (horizontal: middle pin or the center of the middle pins for vertical)
        center_fab = [coldist * (cols - 1) / 2 if orientation == 'Vertical' else body_offset + body_width / 2, t_fab + h_fab / 2]
        center_fp = [l_crt + w_crt / 2, center_fab[1]]
    
    text_size = w_fab*0.6
    fab_text_size_max = 1.0
    if text_size < fab_text_size_min:
        text_size = fab_text_size_min
    elif text_size > fab_text_size_max:
        text_size = fab_text_size_max
    text_size = round(text_size, 2)
    text_size = [text_size,text_size]
    text_t = text_size[0] * 0.15
    
    footprint_name = "{3}_{0}x{1:02}{7}_P{2:03.2f}mm{4}{5}_{6}{8}".format(cols, rows, rm, classname, "_Latch" if latching else "", "{0:03.1f}mm".format(latch_len) if latch_len > 0 else "", orientation, "-1MP" if mh_present else "", "_SMD"if ddrill==0 else "")
    #footprint_name = footprint_name_base + "_MountHole" if mh_present else footprint_name_base
    
    if cols == 1:
        description_rows = "single row"
        tags_rows = "single row"
    elif cols == 2:
        description_rows = "double rows"
        tags_rows = "double row"
    elif cols == 3:
        description_rows = "triple rows"
        tags_rows = "triple row"
    elif cols == 4:
        description_rows = "quadruple rows"
        tags_rows = "quadruple row"
    
    if ddrill == 0:
      description = "SMD"
      tags = "SMD"
      mounting_type = ""
    else:
      description = "Through hole"
      tags = "Through hole"
      mounting_type = "THT"

    description = description + " {3}, {0}x{1:02}, {2:03.2f}mm {8}, {4}{5}{6}{7}".format(cols, rows, rm, classname_description, description_rows, ", {0:03.1f}mm".format(latch_len) if latch_len > 0 else "", " latches" if latching else "", ", mounting holes" if mh_present else "", orientation.lower(), custom_description)
    tags = tags + " {5} {3} {6} {0}x{1:02} {2:03.2f}mm {4}".format(cols, rows, rm, classname_description, tags_rows, orientation.lower(), mounting_type)
    
    if (len(tags_additional) > 0):
        for t in tags_additional:
            footprint_name = footprint_name + "_" + t
            description = description + ", " + t
            tags = tags + " " + t
    
    if extra_description:
        description = description + ", " + extra_description
    
    print(footprint_name)
    
    # init kicad footprint
    kicad_mod = Footprint(footprint_name)
    kicad_mod.setDescription(description)
    kicad_mod.setTags(tags)

    if ddrill == 0:
        kicad_mod.setAttribute('smd')
    
    # instantiate footprint (SMD origin at center, THT at pin 1)
    kicad_modg = Footprint(footprint_name)
    kicad_mod.append(kicad_modg)
    
    # set general values
    kicad_modg.append(Text(type='reference', text='REF**', at=[center_fp[0], t_crt - text_size[1] / 2], layer='F.SilkS'))
    kicad_modg.append(Text(type='user', text='${REFERENCE}', at=[center_fab[0], center_fab[1]], rotation=90, layer='F.Fab', size=text_size, thickness=text_t))
    kicad_modg.append(Text(type='value', text=footprint_name, at=[center_fp[0], t_crt + h_crt + text_size[1] / 2], layer='F.Fab'))
    
    # for shrouded headers, fab and silk layers have very similar geometry
    # can use the same code to build lines on both layers with slight changes in values between layers
    # zip together lists with fab and then silk layer settings as the list elements so the same code can draw both layers
    for layer, line_width, lyr_offset, chamfer in zip(['F.Fab', 'F.SilkS'], [lw_fab, lw_slk], [0, slk_offset], [min(1, w_fab / 4), 0]):
        # body outline
        if orientation == 'Horizontal' and latching:
            # body outline taken from existing KiCad footprint
            body_polygon = [{'x':body_offset - lyr_offset, 'y':t_fab - lyr_offset}, {'x':l_fab + 6.98 + lyr_offset, 'y':t_fab - lyr_offset},
                {'x':l_fab + w_fab + lyr_offset, 'y':t_fab + 3.17 - lyr_offset}, {'x':l_fab + w_fab + lyr_offset, 'y':t_fab + 6.99 + lyr_offset},
                {'x':l_fab + 12.7 + lyr_offset, 'y':t_fab + 9.14 + lyr_offset}, {'x':l_fab + 12.7 + lyr_offset, 'y':t_fab + h_fab - 9.14 - lyr_offset},
                {'x':l_fab + w_fab + lyr_offset, 'y':t_fab + h_fab - 6.99 - lyr_offset}, {'x':l_fab + w_fab + lyr_offset, 'y':t_fab + h_fab - 3.17 + lyr_offset},
                {'x':l_fab + 6.98 + lyr_offset, 'y':t_fab + h_fab + lyr_offset}, {'x':body_offset - lyr_offset, 'y':t_fab + h_fab + lyr_offset}]
            # body outline taken from simplified 3M 3000 model (also modify arguments: body_offset=-1.24 and body_width=1.24+15.53)
            # https://www.3m.com/3M/en_US/company-us/all-3m-products/~/3M-Four-Wall-Header-3000-Series/?N=5002385+3290316872&preselect=8709318+8710652+8733900+8734573&rt=rud
            body_polygon = [{'x':body_offset - lyr_offset, 'y':t_fab - lyr_offset}, {'x':l_fab + 7.11 + lyr_offset, 'y':t_fab - lyr_offset},
                {'x':l_fab + 16.77 + lyr_offset, 'y':t_fab + 3.47 - lyr_offset}, {'x':l_fab + 16.77 + lyr_offset, 'y':t_fab + 7.44 + lyr_offset},
                {'x':l_fab + 13.21 + lyr_offset, 'y':t_fab + 8.07 + lyr_offset}, {'x':l_fab + 13.21 + lyr_offset, 'y':t_fab + h_fab - 8.07 - lyr_offset},
                {'x':l_fab + 16.77 + lyr_offset, 'y':t_fab + h_fab - 7.44 - lyr_offset}, {'x':l_fab + 16.77 + lyr_offset, 'y':t_fab + h_fab - 3.47 + lyr_offset},
                {'x':l_fab + 7.11 + lyr_offset, 'y':t_fab + h_fab + lyr_offset}, {'x':body_offset - lyr_offset, 'y':t_fab + h_fab + lyr_offset}]
            kicad_mod.append(PolygoneLine(polygone=body_polygon, layer=layer, width=line_width))
            # now draw the left side vertical line, which may be broken on the silk layer around mounting holes
            if layer == 'F.SilkS' and mh_present and mh_pad[0]/2 - mh_offset > -body_offset + slk_offset * 1.5:
                body_polygon = [{'x':body_offset - lyr_offset, 'y':t_fab - lyr_offset}, {'x':body_offset - lyr_offset, 'y':mh_y[0] - mh_pad[0]/2}]
                kicad_mod.append(PolygoneLine(polygone=body_polygon, layer=layer, width=line_width))
                body_polygon = [{'x':body_offset - lyr_offset, 'y':mh_y[0] + mh_pad[0]/2}, {'x':body_offset - lyr_offset, 'y':mh_y[1] - mh_pad[0]/2}]
                kicad_mod.append(PolygoneLine(polygone=body_polygon, layer=layer, width=line_width))
                body_polygon = [{'x':body_offset - lyr_offset, 'y':mh_y[1] + mh_pad[0]/2}, {'x':body_offset - lyr_offset, 'y':t_fab + h_fab + lyr_offset}]
                kicad_mod.append(PolygoneLine(polygone=body_polygon, layer=layer, width=line_width))
            else:
                body_polygon = [{'x':body_offset - lyr_offset, 'y':t_fab + h_fab + lyr_offset}, {'x':body_offset - lyr_offset, 'y':t_fab - lyr_offset}]
                kicad_mod.append(PolygoneLine(polygone=body_polygon, layer=layer, width=line_width))
        else:
            # body outline silk lines need to clear the mounting hole on vertical headers
            if mh_present and layer == 'F.SilkS':
                body_polygon = [{'x':mh_offset + mh_pad[0]/2 - lyr_offset, 'y':t_fab - lyr_offset}, {'x':l_fab + w_fab + lyr_offset, 'y':t_fab - lyr_offset},
                    {'x':l_fab + w_fab + lyr_offset, 'y':t_fab + h_fab + lyr_offset}, {'x':mh_offset + mh_pad[0]/2 - lyr_offset, 'y':t_fab + h_fab + lyr_offset}]
                kicad_mod.append(PolygoneLine(polygone=body_polygon, layer=layer, width=line_width))
                body_polygon = [{'x':mh_offset - mh_pad[0]/2 + lyr_offset, 'y':t_fab - lyr_offset}, {'x':l_fab - lyr_offset, 'y':t_fab - lyr_offset},
                    {'x':l_fab - lyr_offset, 'y':t_fab + h_fab + lyr_offset}, {'x':mh_offset - mh_pad[0]/2 + lyr_offset, 'y':t_fab + h_fab + lyr_offset}]
                kicad_mod.append(PolygoneLine(polygone=body_polygon, layer=layer, width=line_width))
            else:
                if layer == 'F.SilkS' and ddrill == 0:
                    # Break silkscreen for SMD pads
                    body_polygon = [{'x':l_fab - lyr_offset, 'y':-((rows-1)*rm/2)-pad[1]/2-0.5}, {'x':l_fab - lyr_offset, 'y':t_fab - lyr_offset},
                        {'x':l_fab + w_fab + lyr_offset, 'y':t_fab - lyr_offset}, {'x':l_fab +w_fab + lyr_offset, 'y':-((rows-1)*rm/2)-pad[1]/2-0.5}]
                    kicad_mod.append(PolygoneLine(polygone=body_polygon, layer=layer, width=line_width))
                    body_polygon = [{'x':l_fab - lyr_offset, 'y':((rows-1)*rm/2)+pad[1]/2+0.5}, {'x':l_fab - lyr_offset, 'y':t_fab + h_fab + lyr_offset},
                        {'x':l_fab + w_fab + lyr_offset, 'y':t_fab +h_fab + lyr_offset}, {'x':l_fab +w_fab + lyr_offset, 'y':((rows-1)*rm/2)+pad[1]/2+0.5}]
                    kicad_mod.append(PolygoneLine(polygone=body_polygon, layer=layer, width=line_width))
                else:
                    body_polygon = [{'x':l_fab + chamfer - lyr_offset, 'y':t_fab - lyr_offset}, {'x':l_fab + w_fab + lyr_offset, 'y':t_fab - lyr_offset},
                        {'x':l_fab + w_fab + lyr_offset, 'y':t_fab + h_fab + lyr_offset}, {'x':l_fab - lyr_offset, 'y':t_fab + h_fab + lyr_offset},
                        {'x':l_fab - lyr_offset, 'y':t_fab + chamfer - lyr_offset}]
                    kicad_mod.append(PolygoneLine(polygone=body_polygon, layer=layer, width=line_width))
        if chamfer > 0 and not (orientation == 'Horizontal' and latching):
            kicad_modg.append(Line(start=[l_fab, t_fab + chamfer], end=[l_fab + chamfer, t_fab], layer=layer, width=line_width))
        
        # vertical mating connector outline (this is the same for both layers)
        if orientation == 'Vertical':
            if ddrill == 0:
                mating_conn_polygon = [{'x':l_fab - lyr_offset, 'y':center_fab[1] - notch_width/2}, {'x':l_fab + wall_thickness, 'y':center_fab[1] - notch_width/2},
                    {'x':l_fab + wall_thickness, 'y':t_fab+wall_thickness}, {'x':l_fab + w_fab - wall_thickness, 'y':t_fab+wall_thickness},
                    {'x':l_fab + w_fab - wall_thickness, 'y':t_fab+h_fab-wall_thickness}, {'x':l_fab + wall_thickness, 'y':t_fab+h_fab-wall_thickness},
                    {'x':l_fab + wall_thickness, 'y':center_fab[1] + notch_width/2}, {'x':l_fab + wall_thickness, 'y':center_fab[1] + notch_width/2},
                    {'x':l_fab - lyr_offset, 'y':center_fab[1] + notch_width/2}]
                if layer == "F.Fab":
                    # Only append mating connector outline in F.Fab for SMD footprints (silkscreen would be on top of pads)
                    kicad_mod.append(PolygoneLine(polygone=mating_conn_polygon, layer=layer, width=line_width))
            else:
                mating_conn_polygon = [{'x':l_fab - lyr_offset, 'y':center_fab[1] - notch_width/2}, {'x':l_fab + wall_thickness, 'y':center_fab[1] - notch_width/2},
                    {'x':l_fab + wall_thickness, 'y':-mating_overlen}, {'x':l_fab + w_fab - wall_thickness, 'y':-mating_overlen},
                    {'x':l_fab + w_fab - wall_thickness, 'y':(rows - 1) * rm + mating_overlen}, {'x':l_fab + wall_thickness, 'y':(rows - 1) * rm + mating_overlen},
                    {'x':l_fab + wall_thickness, 'y':center_fab[1] + notch_width/2}, {'x':l_fab + wall_thickness, 'y':center_fab[1] + notch_width/2},
                    {'x':l_fab - lyr_offset, 'y':center_fab[1] + notch_width/2}]
                kicad_mod.append(PolygoneLine(polygone=mating_conn_polygon, layer=layer, width=line_width))
        
        # horizontal mating connector 'notch' lines
        if orientation == 'Horizontal' and not latching:
            kicad_modg.append(Line(start=[body_offset - lyr_offset, center_fab[1] - notch_width / 2], end=[l_fab + w_fab + lyr_offset, center_fab[1] - notch_width / 2], layer=layer, width=line_width))
            kicad_modg.append(Line(start=[body_offset - lyr_offset, center_fab[1] + notch_width / 2], end=[l_fab + w_fab + lyr_offset, center_fab[1] + notch_width / 2], layer=layer, width=line_width))
        
        # vertical latches (horizontal latches are off the PCB and not shown)
        if orientation == 'Vertical' and latching and latch_len > 0:
            # body outline silk lines need to clear the mounting hole on vertical headers
            if mh_present and layer == 'F.SilkS':
                # top latch
                latch_top_polygon = [{'x':center_fab[0] - latch_width/2 - lyr_offset, 'y':mh_y[0] - mh_pad[1]/2 + lyr_offset}, {'x':center_fab[0] - latch_width/2 - lyr_offset, 'y':t_fab - latch_len - lyr_offset},
                    {'x':center_fab[0] + latch_width/2 + lyr_offset, 'y':t_fab - latch_len - lyr_offset}, {'x':center_fab[0] + latch_width/2 + lyr_offset, 'y':mh_y[0] - mh_pad[1]/2 + lyr_offset}]
                kicad_mod.append(PolygoneLine(polygone=latch_top_polygon, layer=layer, width=line_width))
                # bottom latch
                latch_bottom_polygon = [{'x':center_fab[0] - latch_width/2 - lyr_offset, 'y':mh_y[1] + mh_pad[1]/2 - lyr_offset}, {'x':center_fab[0] - latch_width/2 - lyr_offset, 'y':t_fab + h_fab + latch_len + lyr_offset},
                    {'x':center_fab[0] + latch_width/2 + lyr_offset, 'y':t_fab + h_fab + latch_len + lyr_offset}, {'x':center_fab[0] + latch_width/2 + lyr_offset, 'y':mh_y[1] + mh_pad[1]/2 - lyr_offset}]
                kicad_mod.append(PolygoneLine(polygone=latch_bottom_polygon, layer=layer, width=line_width))
            else:
                # top latch
                latch_top_polygon = [{'x':center_fab[0] - latch_width/2 - lyr_offset, 'y':t_fab - lyr_offset}, {'x':center_fab[0] - latch_width/2 - lyr_offset, 'y':t_fab - latch_len - lyr_offset},
                    {'x':center_fab[0] + latch_width/2 + lyr_offset, 'y':t_fab - latch_len - lyr_offset}, {'x':center_fab[0] + latch_width/2 + lyr_offset, 'y':t_fab - lyr_offset}]
                kicad_mod.append(PolygoneLine(polygone=latch_top_polygon, layer=layer, width=line_width))
                # bottom latch
                latch_bottom_polygon = [{'x':center_fab[0] - latch_width/2 - lyr_offset, 'y':t_fab + h_fab + lyr_offset}, {'x':center_fab[0] - latch_width/2 - lyr_offset, 'y':t_fab + h_fab + latch_len + lyr_offset},
                    {'x':center_fab[0] + latch_width/2 + lyr_offset, 'y':t_fab + h_fab + latch_len + lyr_offset}, {'x':center_fab[0] + latch_width/2 + lyr_offset, 'y':t_fab + h_fab + lyr_offset}]
                kicad_mod.append(PolygoneLine(polygone=latch_bottom_polygon, layer=layer, width=line_width))
    
    # horizontal pin outlines (only applies if the body is right of the leftmost pin row)
    #if orientation == 'Horizontal' and not latching:
    if body_offset > 0:
        for row in range(rows):
            horiz_pin_polygon = [{'x':body_offset, 'y':rm * row - pin_size / 2}, {'x':-pin_size / 2, 'y':rm * row - pin_size / 2},
                {'x':-pin_size / 2, 'y':rm * row + pin_size / 2}, {'x':body_offset, 'y':rm * row + pin_size / 2}]
            kicad_modg.append(PolygoneLine(polygone=horiz_pin_polygon, layer='F.Fab', width=lw_fab))
    
    # silk pin 1 mark (triangle to the left of pin 1)
    slk_mark_height = 1
    slk_mark_width = 1
    if ddrill == 0:
        slk_polygon = [{'x':l_fab - lyr_offset, 'y':-((rows-1)*rm/2)-pad[1]/2-0.5}, {'x':l_fab - lyr_offset-1.5, 'y':-((rows-1)*rm/2)-pad[1]/2-0.5}]
    else:
        slk_mark_tip = min(l_fab, -pad[0] / 2) - 0.5 # offset 0.5mm from pin 1 or the body
        slk_polygon = [{'x':slk_mark_tip, 'y':0}, {'x':slk_mark_tip - slk_mark_width, 'y':-slk_mark_height / 2},
            {'x':slk_mark_tip - slk_mark_width, 'y':slk_mark_height / 2}, {'x':slk_mark_tip, 'y':0}]
    kicad_mod.append(PolygoneLine(polygone=slk_polygon, layer='F.SilkS', width=lw_slk))
    
    # create courtyard
    if ddrill == 0 and orientation == 'Vertical' and not latching:
      #         l_crt =  -pad[0] / 2 - coldist/2- crt_offset
        crt_polygon = [ {'x': roundCrt(l_fab - crt_offset), 'y':roundCrt(t_crt)},
            {'x': roundCrt(l_fab - crt_offset), 'y': roundCrt(-((rows-1)*rm/2)-pad[1]/2 - crt_offset)},
            {'x': roundCrt(l_crt), 'y': roundCrt(-((rows-1)*rm/2)-pad[1]/2 - crt_offset)},
            {'x': roundCrt(l_crt), 'y': roundCrt(((rows-1)*rm/2)+pad[1]/2 + crt_offset)},
            {'x': roundCrt(l_fab - crt_offset), 'y': roundCrt(((rows-1)*rm/2)+pad[1]/2 + crt_offset)},
            {'x': roundCrt(l_fab - crt_offset), 'y':roundCrt(-t_crt)},
            {'x': roundCrt(-l_fab + crt_offset), 'y':roundCrt(-t_crt)},
            {'x': roundCrt(-l_fab + crt_offset), 'y': roundCrt(((rows-1)*rm/2)+pad[1]/2 + crt_offset)},
            {'x': roundCrt(-l_crt), 'y': roundCrt(((rows-1)*rm/2)+pad[1]/2 + crt_offset)},
            {'x': roundCrt(-l_crt), 'y': roundCrt(-((rows-1)*rm/2)-pad[1]/2 - crt_offset)},
            {'x': roundCrt(-l_fab + crt_offset), 'y': roundCrt(-((rows-1)*rm/2)-pad[1]/2 - crt_offset)},
            {'x': roundCrt(-l_fab + crt_offset), 'y':roundCrt(t_crt)},
            {'x': roundCrt(l_fab - crt_offset), 'y':roundCrt(t_crt)}]
        kicad_mod.append(PolygoneLine(polygone=crt_polygon, layer='F.CrtYd', width=lw_crt))
    else:
        kicad_mod.append(RectLine(start=[roundCrt(l_crt), roundCrt(t_crt)], end=[roundCrt(l_crt + w_crt),
                    roundCrt(t_crt + h_crt)], layer='F.CrtYd', width=lw_crt))
    
    # create pads (first the left row then the right row)
    if ddrill == 0:
        pad_type = Pad.TYPE_SMT
        pad_shape = Pad.SHAPE_ROUNDRECT
        pad_layers = Pad.LAYERS_SMT
    else:
        pad_type = Pad.TYPE_THT
        pad_shape = Pad.SHAPE_OVAL
        pad_layers = Pad.LAYERS_THT

    if ddrill == 0:
        # For SMD footprints, pad 1 location is not (0,0)
        for start_pos, initial in zip([-coldist/2, coldist/2], range(1, cols + 1)):
            kicad_modg.append(PadArray(pincount=rows, spacing=[0,rm], start=[start_pos,-(rows-1)*rm/2], initial=initial, increment=cols,
                type=pad_type, shape=pad_shape, size=pad, drill=ddrill, layers=pad_layers))
    else:
        for start_pos, initial in zip([0, coldist], range(1, cols + 1)):
            kicad_modg.append(PadArray(pincount=rows, spacing=[0,rm], start=[start_pos,0], initial=initial, increment=cols,
                type=pad_type, shape=pad_shape, size=pad, drill=ddrill, layers=pad_layers))

    # create mounting hole pads
    if mh_present:
        for mh_y_offset in mh_y:
            kicad_modg.append(Pad(number=mh_number, type=Pad.TYPE_THT, shape=Pad.SHAPE_OVAL, at=[mh_offset, mh_y_offset], size=mh_pad,
                drill=mh_ddrill, layers=Pad.LAYERS_THT))
    
    # add model (even if there are mounting holes on the footprint do not include that in the 3D model)
    kicad_modg.append(Model(filename="{0}/{1}.3dshapes/{2}.wrl".format(model3d_path_prefix, lib_name, footprint_name), at=offset3d, scale=scale3d, rotate=rotate3d))
    
    # print render tree
    # print(kicad_mod.getRenderTree())
    # print(kicad_mod.getCompleteRenderTree())
    
    # write file
    output_dir = '{lib_name:s}.pretty/'.format(lib_name=lib_name)
    if not os.path.isdir(output_dir): #returns false if path does not yet exist!! (Does not check path validity)
        os.makedirs(output_dir)
    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile('{outdir:s}{fp_name:s}.kicad_mod'.format(outdir=output_dir, fp_name=footprint_name))

# 3220-XX-0100-00
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
        for mh_ddrill, mh_pad, mh_overlen in zip([0, mh_ddrill], [[0,0], mh_pad], [0, mh_overlen]):
        #for mh_ddrill, mh_pad, mh_overlen in zip([0], [[0,0]], [0]):
            part_num = "%s%s%02u%s" % (part_num_left_left, part_num_left, rows*cols, part_num_right)
            class_desc = "IDC header %s%02u%s" % (part_num_left, rows*cols, part_num_right)
            makeIdcHeaderCustomDescription(rows, cols, rm, cm, body_width,
                                body_overlen, body_overlen, body_offset,
                                ddrill, pad,
                                mating_overlen, wall_thickness, notch_width,
                                orientation, latching,
                                latch_lengths, latch_width,
                                mh_ddrill, mh_pad, mh_overlen, mh_offset, mh_number,
                                tags_additional, extra_description, "Connector_IDC_1.27mm_Extended", part_num, class_desc,
                                [0, 0, 0], [1, 1, 1], [0, 0, 0], "${KICAD7_3DMODEL_DIR}")
