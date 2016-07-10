from __future__ import print_function
from openmdao.api import Component, Group, Problem

# Imported from Python standard
import sys
import os
import time
import math
import numpy
from  AVL_py import AVL

class aero_AVL(Component):
	""" Makes the appropriate run file and outputs the computed numbers """
	def __init__(self):

		super(aero_AVL, self).__init__()

		self.add_param('taper', val=0.0) # taper ratio

		self.add_output('CL', val=0.0)


		# ==================================================================
		# Define starting geometry: (Change here depending on what you want)
		# ==================================================================
		# You can either parse a geometry file (future) or specify here
		# Array definition
		geometry_file_available = 0
		geometry = []
		sections = []
		if geometry_file_available == 0:

			geometry.append('M-8_Wing')
			geometry.append(0.0) # Mach
			geometry.append(0) # Iysm
			geometry.append(0) # IZsym
			geometry.append(0) # Zsym
			geometry.append(14) # Sref (Planform Wing area)
			geometry.append(1.60) # Cref
			geometry.append(8.75) # Bref (wing span)
			geometry.append(0.296) #Xcg
			geometry.append(0) # Ycg
			geometry.append(0) #Zcy
			geometry.append(1) # Num sections

			### SURFACE (copy and paste and modift as many times as necessary)
			geometry.append('Wing') # Name of surface
			geometry.append(10) # Nchordwise 
			geometry.append(1.0) # Cspace
			geometry.append(30) # Nspanwise
			geometry.append(-2.0) # Sspace
			geometry.append(1) # COMPONENT
			geometry.append(0.0) # YDuplicate
			geometry.append(0.0) # Angle
			geometry.append(1.0) # XScale
			geometry.append(1.0) # YScale
			geometry.append(1.0) # Zscale
			geometry.append(0.0) # Translate X
			geometry.append(0.0) # Translate Y
			geometry.append(0.0) # Translate Z
			geometry.append(4) # Number of sections in this surface

			## Surface Section (copy and paste and modify as many times as necessary)
			# Wing root
			sections.append(0.0) # Xle
			sections.append(0.0) # Yle
			sections.append(0.0) # Zle
			sections.append(1.6) # Chord
			sections.append(2) # Ainc
			sections.append('ht22.dat') # AFILE
			# Aileron Start
			sections.append(0.0) # Xle
			sections.append(2.62) # Yle
			sections.append(0.0) # Zle
			sections.append(1.6) # Chord
			sections.append(2) # Ainc
			sections.append('ht22.dat') # AFILE
			# Aileron End
			sections.append(0.0) # Xle
			sections.append(4.37) # Yle
			sections.append(0.0) # Zle
			sections.append(1.6) # Chord
			sections.append(2) # Ainc
			sections.append('ht22.dat') # AFILE
			# Wing Tip
			sections.append(0.0) # Xle
			sections.append(4.375) # Yle
			sections.append(0.0) # Zle
			sections.append(1.6) # Chord
			sections.append(2) # Ainc
			sections.append('ht22.dat') # AFILE

	#	else:
			# geometry_and_sections = read_geo()


		
		# Initializes an AVL object
		self.aircraft = AVL(geometry, sections)

	def solve_nonlinear(self, params, unknowns, resids):
		#=========================================
		# Modify starting geometry according to taper, twist, dihedral, etc.
		#=========================================

		#TODO
		print('Taper ratio: ')
		print(params['taper'])
		print('\n')

		# Modify taper
		section_num = self.aircraft.geometry_config['surface_0_section_num']
		wingspan = self.aircraft.geometry_config['surface_0_section_data']['section_'+str(section_num-1)+'_Yle']
		root_chord = self.aircraft.geometry_config['surface_0_section_data']['section_0_Chord']

		for num in range(section_num):
			section_location = self.aircraft.geometry_config['surface_0_section_data']['section_'+str(num)+'_Yle']
			self.aircraft.geometry_config['surface_0_section_data']['section_'+str(num)+'_Chord'] = root_chord * (params['taper']-1)/ wingspan * section_location

		#=========================================
		# Rerun AVL with specified AoA
		#=========================================
		self.aircraft.create_geometry_file()
		self.aircraft.run_avl_AoA(0)
		self.aircraft.read_aero_file()

		unknowns['CL'] = self.aircraft.coeffs['CLtot']

		
