
from pyIEM import iemAccessDatabase
import os
iemdb = iemAccessDatabase.iemAccessDatabase()

rs = iemdb.query("SELECT station from current WHERE network = 'IACOCORAHS' and \
  valid > 'TODAY' ORDER by pday DESC").dictresult()
dict = {}
dict['sid1'] = rs[0]['station']
dict['sid2'] = rs[1]['station']
dict['sid3'] = rs[2]['station']
dict['sid4'] = rs[3]['station']
dict['sid5'] = rs[4]['station']
dict['q'] = "%Q"

out = open('coco_top5rain.scn', 'w')

out.write("""<?xml version="1.0" ?>
<scene_file magic="Weather Central :LIVE Scene File" version="1.0" name="Unnamed" >
<scene type="BasicScene" name="Top 5 Rain" autoadvance="0" audio_file="" use_audio="0" Skip="0" GpiTrigger="0" EnableForegroundKeyer="0" useVideoInputAudio="0" Updateable="0" crosspoint="0" SegmentStart="-1" SegmentPassThru="0" RouterAdvance="0" JumpTarget="0" >
<Gpi GpiAdvance="0" />
<Gpi GpiAdvance="0" />
<Gpi GpiAdvance="0" />
<Gpi GpiAdvance="0" />
<Gpi GpiAdvance="0" />
<Gpi GpiAdvance="0" />
<Gpi GpiAdvance="0" />
<Gpi GpiAdvance="0" />
<element type="QuickTime" name="E:\live\content\movies\\00_BG2.mov" looprepeats="10" transistioninplay="0" transistionoutplay="0" startdwell="0" enddwell="0" startpause="0" playspeed="0" backward="0" updatable="0" elementname="" loopatframe="0" useloopatframe="0" usepausepoints="1" onlyshowpausepoints="0" timedpauses="0" stillduration="0" movieduration="0" leftside="0" width="1" height="1" bottomside="0" />
<element type="Image" name="E:\live\content\images\overlays\\banners\\rainfall.tif" noimage="0" updatable="0" duration="5" elementname="" />
<element type="StatsPage" name="" duration="5" gridXStart="0.1" gridYStart="0.1" gridXStize="0.01" gridYStize="0.01" use_grid="1" show_grid="0" motion_type="0" order_type="0" motion_duration="0" motion_fade_on="0" >
<observation table_file="cocorahs" field_name="Precip Total" station="%(sid1)s" x_position="460.8" y_position="325.62" plotted="1" style="Text" BlankValue="" prefix="" suffix="%(q)s" from_unit="0" to_unit="0" filter_places="2" metline="1" continuous="1" alternate_name="Rainfall 1" data="3.30" ShowBlankPrefix="0" >
<text text_font="Arial" text_size="35" text_size_y="35" text_justify="0" text_alignment="0" text_shadow_distance="2" text_direction_="135" item_name="" item_active="1" use_outline="1" text_seperation="2" rotate="0" font_italic="0" font_bold="0" text_align_on_data="0" >
<text_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
<text_shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
<outline_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
</text>
<cutout cutout_mapping_file="" cutout_scale_x="1" cutout_scale_y="1" item_name="" item_active="1" cutout_justify="4" cutout_opacity="1" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</cutout>
<flipbook flipbook_name="" flipbook_scale_x="1" flipbook_scale_y="1" item_name="" item_active="1" flipbook_justify="4" flipbook_opacity="1" dwell="0" startdelay="0" enddelay="0" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</flipbook>
</observation>
<observation table_file="cocorahs" field_name="Precip Total" station="%(sid2)s" x_position="460.8" y_position="272.16" plotted="1" style="Text" BlankValue="" prefix="" suffix="%(q)s" from_unit="0" to_unit="0" filter_places="2" metline="1" continuous="1" alternate_name="Rainfall 2" data="3.27" ShowBlankPrefix="0" >
<text text_font="Arial" text_size="35" text_size_y="35" text_justify="0" text_alignment="0" text_shadow_distance="2" text_direction_="135" item_name="" item_active="1" use_outline="1" text_seperation="2" rotate="0" font_italic="0" font_bold="0" text_align_on_data="0" >
<text_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
<text_shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
<outline_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
</text>
<cutout cutout_mapping_file="" cutout_scale_x="1" cutout_scale_y="1" item_name="" item_active="1" cutout_justify="4" cutout_opacity="1" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</cutout>
<flipbook flipbook_name="" flipbook_scale_x="1" flipbook_scale_y="1" item_name="" item_active="1" flipbook_justify="4" flipbook_opacity="1" dwell="0" startdelay="0" enddelay="0" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</flipbook>
</observation>
<observation table_file="cocorahs" field_name="Precip Total" station="%(sid3)s" x_position="460.8" y_position="213.84" plotted="1" style="Text" BlankValue="" prefix="" suffix="%(q)s" from_unit="0" to_unit="0" filter_places="2" metline="1" continuous="1" alternate_name="Rainfall 3" data="2.47" ShowBlankPrefix="0" >
<text text_font="Arial" text_size="35" text_size_y="35" text_justify="0" text_alignment="0" text_shadow_distance="2" text_direction_="135" item_name="" item_active="1" use_outline="1" text_seperation="2" rotate="0" font_italic="0" font_bold="0" text_align_on_data="0" >
<text_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
<text_shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
<outline_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
</text>
<cutout cutout_mapping_file="" cutout_scale_x="1" cutout_scale_y="1" item_name="" item_active="1" cutout_justify="4" cutout_opacity="1" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</cutout>
<flipbook flipbook_name="" flipbook_scale_x="1" flipbook_scale_y="1" item_name="" item_active="1" flipbook_justify="4" flipbook_opacity="1" dwell="0" startdelay="0" enddelay="0" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</flipbook>
</observation>
<observation table_file="cocorahs" field_name="Precip Total" station="%(sid4)s" x_position="460.8" y_position="160.38" plotted="1" style="Text" BlankValue="" prefix="" suffix="%(q)s" from_unit="0" to_unit="0" filter_places="2" metline="1" continuous="1" alternate_name="Rainfall 4" data="2.25" ShowBlankPrefix="0" >
<text text_font="Arial" text_size="35" text_size_y="35" text_justify="0" text_alignment="0" text_shadow_distance="2" text_direction_="135" item_name="" item_active="1" use_outline="1" text_seperation="2" rotate="0" font_italic="0" font_bold="0" text_align_on_data="0" >
<text_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
<text_shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
<outline_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
</text>
<cutout cutout_mapping_file="" cutout_scale_x="1" cutout_scale_y="1" item_name="" item_active="1" cutout_justify="4" cutout_opacity="1" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</cutout>
<flipbook flipbook_name="" flipbook_scale_x="1" flipbook_scale_y="1" item_name="" item_active="1" flipbook_justify="4" flipbook_opacity="1" dwell="0" startdelay="0" enddelay="0" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</flipbook>
</observation>
<observation table_file="cocorahs" field_name="Precip Total" station="%(sid5)s" x_position="460.8" y_position="106.92" plotted="1" style="Text" BlankValue="" prefix="" suffix="%(q)s" from_unit="0" to_unit="0" filter_places="2" metline="1" continuous="1" alternate_name="Rainfall 5" data="2.07" ShowBlankPrefix="0" >
<text text_font="Arial" text_size="35" text_size_y="35" text_justify="0" text_alignment="0" text_shadow_distance="2" text_direction_="135" item_name="" item_active="1" use_outline="1" text_seperation="2" rotate="0" font_italic="0" font_bold="0" text_align_on_data="0" >
<text_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
<text_shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
<outline_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
</text>
<cutout cutout_mapping_file="" cutout_scale_x="1" cutout_scale_y="1" item_name="" item_active="1" cutout_justify="4" cutout_opacity="1" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</cutout>
<flipbook flipbook_name="" flipbook_scale_x="1" flipbook_scale_y="1" item_name="" item_active="1" flipbook_justify="4" flipbook_opacity="1" dwell="0" startdelay="0" enddelay="0" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</flipbook>
</observation>
<observation table_file="cocorahs" field_name="CityName" station="%(sid1)s" x_position="79.2" y_position="320.76" plotted="1" style="Text" BlankValue="" prefix="" suffix="" from_unit="0" to_unit="0" filter_places="0" metline="1" continuous="1" alternate_name="City 1" data="Manson" ShowBlankPrefix="0" >
<text text_font="HelveticaNeue LT 85 Heavy" text_size="35" text_size_y="35" text_justify="0" text_alignment="0" text_shadow_distance="2" text_direction_="135" item_name="" item_active="1" use_outline="1" text_seperation="2" rotate="0" font_italic="0" font_bold="0" text_align_on_data="0" >
<text_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
<text_shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
<outline_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
</text>
<cutout cutout_mapping_file="" cutout_scale_x="1" cutout_scale_y="1" item_name="" item_active="1" cutout_justify="4" cutout_opacity="1" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</cutout>
<flipbook flipbook_name="" flipbook_scale_x="1" flipbook_scale_y="1" item_name="" item_active="1" flipbook_justify="4" flipbook_opacity="1" dwell="0" startdelay="0" enddelay="0" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</flipbook>
</observation>
<observation table_file="cocorahs" field_name="CityName" station="%(sid2)s" x_position="79.2" y_position="272.16" plotted="1" style="Text" BlankValue="" prefix="" suffix="" from_unit="0" to_unit="0" filter_places="0" metline="1" continuous="1" alternate_name="City 2" data="Fort Dodge" ShowBlankPrefix="0" >
<text text_font="HelveticaNeue LT 85 Heavy" text_size="35" text_size_y="35" text_justify="0" text_alignment="0" text_shadow_distance="2" text_direction_="135" item_name="" item_active="1" use_outline="1" text_seperation="2" rotate="0" font_italic="0" font_bold="0" text_align_on_data="0" >
<text_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
<text_shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
<outline_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
</text>
<cutout cutout_mapping_file="" cutout_scale_x="1" cutout_scale_y="1" item_name="" item_active="1" cutout_justify="4" cutout_opacity="1" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</cutout>
<flipbook flipbook_name="" flipbook_scale_x="1" flipbook_scale_y="1" item_name="" item_active="1" flipbook_justify="4" flipbook_opacity="1" dwell="0" startdelay="0" enddelay="0" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</flipbook>
</observation>
<observation table_file="cocorahs" field_name="CityName" station="%(sid3)s" x_position="79.2" y_position="218.7" plotted="1" style="Text" BlankValue="" prefix="" suffix="" from_unit="0" to_unit="0" filter_places="0" metline="1" continuous="1" alternate_name="City 3" data="Ankeny" ShowBlankPrefix="0" >
<text text_font="HelveticaNeue LT 85 Heavy" text_size="35" text_size_y="35" text_justify="0" text_alignment="0" text_shadow_distance="2" text_direction_="135" item_name="" item_active="1" use_outline="1" text_seperation="2" rotate="0" font_italic="0" font_bold="0" text_align_on_data="0" >
<text_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
<text_shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
<outline_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
</text>
<cutout cutout_mapping_file="" cutout_scale_x="1" cutout_scale_y="1" item_name="" item_active="1" cutout_justify="4" cutout_opacity="1" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</cutout>
<flipbook flipbook_name="" flipbook_scale_x="1" flipbook_scale_y="1" item_name="" item_active="1" flipbook_justify="4" flipbook_opacity="1" dwell="0" startdelay="0" enddelay="0" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</flipbook>
</observation>
<observation table_file="cocorahs" field_name="CityName" station="%(sid4)s" x_position="79.2" y_position="160.38" plotted="1" style="Text" BlankValue="" prefix="" suffix="" from_unit="0" to_unit="0" filter_places="0" metline="1" continuous="1" alternate_name="City 4" data="Webster City" ShowBlankPrefix="0" >
<text text_font="HelveticaNeue LT 85 Heavy" text_size="35" text_size_y="35" text_justify="0" text_alignment="0" text_shadow_distance="2" text_direction_="135" item_name="" item_active="1" use_outline="1" text_seperation="2" rotate="0" font_italic="0" font_bold="0" text_align_on_data="1" >
<text_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
<text_shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
<outline_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
</text>
<cutout cutout_mapping_file="" cutout_scale_x="1" cutout_scale_y="1" item_name="" item_active="1" cutout_justify="4" cutout_opacity="1" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</cutout>
<flipbook flipbook_name="" flipbook_scale_x="1" flipbook_scale_y="1" item_name="" item_active="1" flipbook_justify="4" flipbook_opacity="1" dwell="0" startdelay="0" enddelay="0" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</flipbook>
</observation> 
<observation table_file="cocorahs" field_name="CityName" station="%(sid5)s" x_position="79.2" y_position="102.06" plotted="1" style="Text" BlankValue="" prefix="" suffix="" from_unit="0" to_unit="0" filter_places="0" metline="1" continuous="1" alternate_name="City 5" data="Nevada" ShowBlankPrefix="0" >
<text text_font="HelveticaNeue LT 85 Heavy" text_size="35" text_size_y="35" text_justify="0" text_alignment="0" text_shadow_distance="2" text_direction_="135" item_name="" item_active="1" use_outline="1" text_seperation="2" rotate="0" font_italic="0" font_bold="0" text_align_on_data="1" >
<text_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
<text_shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
<outline_color color_red="1" color_green="1" color_blue="1" color_alpha="1" />
</text>
<cutout cutout_mapping_file="" cutout_scale_x="1" cutout_scale_y="1" item_name="" item_active="1" cutout_justify="4" cutout_opacity="1" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</cutout>
<flipbook flipbook_name="" flipbook_scale_x="1" flipbook_scale_y="1" item_name="" item_active="1" flipbook_justify="4" flipbook_opacity="1" dwell="0" startdelay="0" enddelay="0" shadow_distance="2" shadow_direction="135" rotate="0" >
<shadow_color color_red="0.1" color_green="0.1" color_blue="0.1" color_alpha="0.3" />
</flipbook>
</observation>
</element>
<element type="Telestrate" reveal="2" />
<transition type="BasicTransition" transiton_type="1" duration="1" default_x="0.5" default_y="0.5" use_default="1" auto_advance="1" rotation="3" softness="1" reverse="0" elementname="" />
</scene>
</scene_file>""" % dict )

out.close()

os.system("/home/ldm/bin/pqinsert coco_top5rain.scn")
os.remove("coco_top5rain.scn")
