# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

from .kimotor_persist import SpinCtrlDoublePersist
import wx
import wx.xrc

###########################################################################
## Class KiMotorGUI
###########################################################################

class KiMotorGUI ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"KiMotor", pos = wx.DefaultPosition, size = wx.Size( 450,850 ), style = wx.DEFAULT_FRAME_STYLE|wx.STAY_ON_TOP|wx.TAB_TRAVERSAL, name = u"kimotor" )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		bSizer5 = wx.BoxSizer( wx.VERTICAL )

		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Mechanical" ), wx.VERTICAL )

		bSizer21211 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time1211 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Motor shape:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time1211" )
		self.lbl_refresh_time1211.Wrap( -1 )

		self.lbl_refresh_time1211.SetToolTip( u"Shape of the PCB motor outline." )

		bSizer21211.Add( self.lbl_refresh_time1211, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		bSizer21211.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		m_cbOutlineChoices = [ u"Circle", u"Square", u"Polygon" ]
		self.m_cbOutline = wx.ComboBox( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Circle", wx.DefaultPosition, wx.Size( 150,20 ), m_cbOutlineChoices, wx.CB_DROPDOWN|wx.CB_READONLY, wx.DefaultValidator, u"m_cbOutline" )
		self.m_cbOutline.SetSelection( 0 )
		bSizer21211.Add( self.m_cbOutline, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer21211, 1, wx.EXPAND, 5 )

		bSizer221 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time21 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Motor size:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time21" )
		self.lbl_refresh_time21.Wrap( -1 )

		self.lbl_refresh_time21.SetToolTip( u"Size of the PCB motor. For a circular outline it corresponds to the board diameter, while for a square board it is the length of the PCB side." )

		bSizer221.Add( self.lbl_refresh_time21, 0, wx.ALL, 5 )


		bSizer221.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_refresh_time114 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"[mm]", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time114" )
		self.lbl_refresh_time114.Wrap( -1 )

		self.lbl_refresh_time114.SetToolTip( u"Trace width in [mm]" )

		bSizer221.Add( self.lbl_refresh_time114, 0, wx.ALL, 5 )

		self.m_ctrlDout = SpinCtrlDoublePersist( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, 1, 9999, 100, 1, u"m_ctrlDout" )
		self.m_ctrlDout.SetDigits( 2 )
		bSizer221.Add( self.m_ctrlDout, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer221, 1, wx.EXPAND, 5 )

		bSizer2212 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_cbWmnt = wx.CheckBox( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"m_cbWmnt" )
		self.m_cbWmnt.SetValue(True)
		bSizer2212.Add( self.m_cbWmnt, 0, wx.ALL, 5 )

		self.lbl_refresh_time212 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"w_mount:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time212" )
		self.lbl_refresh_time212.Wrap( -1 )

		self.lbl_refresh_time212.SetToolTip( u"Width of the exposed copper annular at the PCB outer edge" )

		bSizer2212.Add( self.lbl_refresh_time212, 0, wx.ALL, 5 )


		bSizer2212.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_refresh_time1141 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"[mm]", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time212" )
		self.lbl_refresh_time1141.Wrap( -1 )

		self.lbl_refresh_time1141.SetToolTip( u"Trace width in [mm]" )

		bSizer2212.Add( self.lbl_refresh_time1141, 0, wx.ALL, 5 )

		self.m_ctrlWmnt = SpinCtrlDoublePersist( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, 0, 9999, 5, 0.1, u"m_ctrlWmnt" )
		self.m_ctrlWmnt.SetDigits( 2 )
		bSizer2212.Add( self.m_ctrlWmnt, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer2212, 1, wx.EXPAND, 5 )

		bSizer22121 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_cbWterm = wx.CheckBox( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"m_cbWterm" )
		self.m_cbWterm.SetValue(True)
		bSizer22121.Add( self.m_cbWterm, 0, wx.ALL, 5 )

		self.lbl_refresh_time2121 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"w_terminals:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time2121" )
		self.lbl_refresh_time2121.Wrap( -1 )

		bSizer22121.Add( self.lbl_refresh_time2121, 0, wx.ALL, 5 )


		bSizer22121.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_refresh_time1142 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"[mm]", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time1142" )
		self.lbl_refresh_time1142.Wrap( -1 )

		self.lbl_refresh_time1142.SetToolTip( u"Trace width in [mm]" )

		bSizer22121.Add( self.lbl_refresh_time1142, 0, wx.ALL, 5 )

		self.m_ctrlWtrm = SpinCtrlDoublePersist( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, 0, 9999, 4, 0.1, u"m_ctrlWtrm" )
		self.m_ctrlWtrm.SetDigits( 2 )
		bSizer22121.Add( self.m_ctrlWtrm, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer22121, 1, wx.EXPAND, 5 )

		bSizer22 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time2 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Diameter, coil start (inner):", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time2" )
		self.lbl_refresh_time2.Wrap( -1 )

		self.lbl_refresh_time2.SetToolTip( u"Radial position where the inner segments of the coils are located." )

		bSizer22.Add( self.lbl_refresh_time2, 0, wx.ALL, 5 )


		bSizer22.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_refresh_time1143 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"[mm]", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time1143" )
		self.lbl_refresh_time1143.Wrap( -1 )

		self.lbl_refresh_time1143.SetToolTip( u"Trace width in [mm]" )

		bSizer22.Add( self.lbl_refresh_time1143, 0, wx.ALL, 5 )

		self.m_ctrlDin = SpinCtrlDoublePersist( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, 1, 9999, 26.000000, 1, u"m_ctrlDin" )
		self.m_ctrlDin.SetDigits( 2 )
		bSizer22.Add( self.m_ctrlDin, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer22, 1, wx.EXPAND, 5 )

		bSizer2211 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time211 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Diameter, shaft bore:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time211" )
		self.lbl_refresh_time211.Wrap( -1 )

		bSizer2211.Add( self.lbl_refresh_time211, 0, wx.ALL, 5 )


		bSizer2211.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_refresh_time1144 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"[mm]", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time1144" )
		self.lbl_refresh_time1144.Wrap( -1 )

		self.lbl_refresh_time1144.SetToolTip( u"Trace width in [mm]" )

		bSizer2211.Add( self.lbl_refresh_time1144, 0, wx.ALL, 5 )

		self.m_ctrlDbore = SpinCtrlDoublePersist( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, 0, 9999, 10, 1, u"m_ctrlDbore" )
		self.m_ctrlDbore.SetDigits( 2 )
		bSizer2211.Add( self.m_ctrlDbore, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer2211, 1, wx.EXPAND, 5 )

		bSizer22112 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time2112 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Outline fillet radius:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time2112" )
		self.lbl_refresh_time2112.Wrap( -1 )

		bSizer22112.Add( self.lbl_refresh_time2112, 0, wx.ALL, 5 )


		bSizer22112.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_refresh_time11441 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"[mm]", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time11441" )
		self.lbl_refresh_time11441.Wrap( -1 )

		self.lbl_refresh_time11441.SetToolTip( u"Trace width in [mm]" )

		bSizer22112.Add( self.lbl_refresh_time11441, 0, wx.ALL, 5 )

		self.m_ctrlFilletRadius = SpinCtrlDoublePersist( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, 0, 1000, 3.100000, 0.1, u"m_ctrlFilletRadius" )
		self.m_ctrlFilletRadius.SetDigits( 2 )
		bSizer22112.Add( self.m_ctrlFilletRadius, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer22112, 1, wx.EXPAND, 5 )

		bSizer27 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time13112 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Mounting holes:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time1311" )
		self.lbl_refresh_time13112.Wrap( -1 )

		bSizer27.Add( self.lbl_refresh_time13112, 0, wx.ALL, 5 )


		bSizer27.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_refresh_time131121 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"size", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time1311" )
		self.lbl_refresh_time131121.Wrap( -1 )

		bSizer27.Add( self.lbl_refresh_time131121, 0, wx.ALL, 5 )

		m_cbMountSizeChoices = [ u"None", u"M2", u"M2.5", u"M3", u"M3.5", u"M4", u"M5", u"M6", u"M8" ]
		self.m_cbMountSize = wx.ComboBox( sbSizer2.GetStaticBox(), wx.ID_ANY, u"M3", wx.DefaultPosition, wx.Size( 150,20 ), m_cbMountSizeChoices, wx.CB_DROPDOWN|wx.CB_READONLY, wx.DefaultValidator, u"m_cbMH" )
		self.m_cbMountSize.SetSelection( 0 )
		bSizer27.Add( self.m_cbMountSize, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer27, 1, wx.EXPAND, 5 )

		bSizer213 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time13 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"- outboard", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time13" )
		self.lbl_refresh_time13.Wrap( -1 )

		bSizer213.Add( self.lbl_refresh_time13, 0, wx.ALL, 5 )


		bSizer213.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_mhOut = SpinCtrlDoublePersist( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 0, 36, 6, 1, u"m_mhOut" )
		self.m_mhOut.SetDigits( 0 )
		bSizer213.Add( self.m_mhOut, 0, wx.ALL, 5 )

		self.lbl_refresh_time1312 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"@ [mm]", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time1312" )
		self.lbl_refresh_time1312.Wrap( -1 )

		bSizer213.Add( self.lbl_refresh_time1312, 0, wx.ALL, 5 )

		self.m_mhOutR = SpinCtrlDoublePersist( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, 10, 1000, 100.000000, 0.1, u"m_mhOutR" )
		self.m_mhOutR.SetDigits( 2 )
		bSizer213.Add( self.m_mhOutR, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer213, 1, wx.EXPAND, 5 )

		bSizer2111 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time111 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"- inboard", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time111" )
		self.lbl_refresh_time111.Wrap( -1 )

		self.lbl_refresh_time111.SetToolTip( u"Trace width in [mm]" )

		bSizer2111.Add( self.lbl_refresh_time111, 0, wx.ALL, 5 )


		bSizer2111.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_mhIn = SpinCtrlDoublePersist( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 0, 36, 0.000000, 1, u"m_mhIn" )
		self.m_mhIn.SetDigits( 0 )
		bSizer2111.Add( self.m_mhIn, 0, wx.ALL, 5 )

		self.lbl_refresh_time13111 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"@ [mm]", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time13111" )
		self.lbl_refresh_time13111.Wrap( -1 )

		bSizer2111.Add( self.lbl_refresh_time13111, 0, wx.ALL, 5 )

		self.m_mhInR = SpinCtrlDoublePersist( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, 10, 1000, 20, 0.1, u"m_mhInR" )
		self.m_mhInR.SetDigits( 2 )
		bSizer2111.Add( self.m_mhInR, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer2111, 1, wx.EXPAND, 5 )


		bSizer5.Add( sbSizer2, 1, wx.EXPAND|wx.TOP, 8 )

		sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Electrical" ), wx.VERTICAL )

		bSizer23 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time3 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Motor Connections:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time" )
		self.lbl_refresh_time3.Wrap( -1 )

		self.lbl_refresh_time3.SetToolTip( u"1P: coils wired for 1-phase motor supply (2 terminals)\n3P: coils wired for 3-phase motor supply (3 terminals)\n3P+N: coils wired for 3-phase + neutral exposed (4 terminals)" )

		bSizer23.Add( self.lbl_refresh_time3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		bSizer23.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		m_cbSchemeChoices = [ u"1P", u"3P", u"3P+N" ]
		self.m_cbScheme = wx.ComboBox( sbSizer1.GetStaticBox(), wx.ID_ANY, u"3P", wx.DefaultPosition, wx.Size( 150,20 ), m_cbSchemeChoices, wx.CB_DROPDOWN|wx.CB_READONLY, wx.DefaultValidator, u"m_cbConnections" )
		self.m_cbScheme.SetSelection( 1 )
		bSizer23.Add( self.m_cbScheme, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		sbSizer1.Add( bSizer23, 1, wx.EXPAND, 5 )

		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Motor Slots:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time" )
		self.lbl_refresh_time.Wrap( -1 )

		bSizer2.Add( self.lbl_refresh_time, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		bSizer2.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlSlots = SpinCtrlDoublePersist( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 6, 60, 6.000000, 3, u"m_ctrlPoles" )
		self.m_ctrlSlots.SetDigits( 0 )
		bSizer2.Add( self.m_ctrlSlots, 0, wx.ALL, 5 )


		sbSizer1.Add( bSizer2, 0, wx.EXPAND, 5 )

		bSizer21 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time1 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Coil loops:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time1" )
		self.lbl_refresh_time1.Wrap( -1 )

		bSizer21.Add( self.lbl_refresh_time1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		bSizer21.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlLoops = SpinCtrlDoublePersist( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 1, 999, 12.000000, 1, u"m_ctrlLoops" )
		self.m_ctrlLoops.SetDigits( 0 )
		bSizer21.Add( self.m_ctrlLoops, 0, wx.ALL, 5 )


		sbSizer1.Add( bSizer21, 1, wx.EXPAND, 5 )

		bSizer214 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time14 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Coil style:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time14" )
		self.lbl_refresh_time14.Wrap( -1 )

		bSizer214.Add( self.lbl_refresh_time14, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		bSizer214.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		m_cbStrategyChoices = [ u"Parallel", u"Radial" ]
		self.m_cbStrategy = wx.ComboBox( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), m_cbStrategyChoices, 0, wx.DefaultValidator, u"m_cbStrategy" )
		self.m_cbStrategy.SetSelection( 1 )
		bSizer214.Add( self.m_cbStrategy, 0, wx.ALL, 5 )


		sbSizer1.Add( bSizer214, 1, wx.EXPAND, 5 )

		bSizer2121 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time121 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"PCB preset:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time121" )
		self.lbl_refresh_time121.Wrap( -1 )

		bSizer2121.Add( self.lbl_refresh_time121, 0, wx.ALL, 5 )


		bSizer2121.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		m_cbPresetChoices = [ u"Custom", u"JLCPCB, 1-2L", u"JLCPCB, 4-6L" ]
		self.m_cbPreset = wx.ComboBox( sbSizer1.GetStaticBox(), wx.ID_ANY, u"JLCPCB, 6L", wx.DefaultPosition, wx.Size( 150,20 ), m_cbPresetChoices, 0, wx.DefaultValidator, u"m_cbPreset" )
		self.m_cbPreset.SetSelection( 2 )
		self.m_cbPreset.Enable( False )

		bSizer2121.Add( self.m_cbPreset, 0, wx.ALL, 5 )


		sbSizer1.Add( bSizer2121, 1, wx.EXPAND, 5 )

		bSizer212 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time12 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"PCB layers:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time12" )
		self.lbl_refresh_time12.Wrap( -1 )

		bSizer212.Add( self.lbl_refresh_time12, 0, wx.ALL, 5 )


		bSizer212.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlLayers = SpinCtrlDoublePersist( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 2, 20, 2, 2, u"m_ctrlLayers" )
		self.m_ctrlLayers.SetDigits( 0 )
		bSizer212.Add( self.m_ctrlLayers, 0, wx.ALL, 5 )


		sbSizer1.Add( bSizer212, 1, wx.EXPAND, 5 )

		bSizer211 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time11 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Track width:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time11" )
		self.lbl_refresh_time11.Wrap( -1 )

		self.lbl_refresh_time11.SetToolTip( u"Trace width in [mm]" )

		bSizer211.Add( self.lbl_refresh_time11, 0, wx.ALL, 5 )


		bSizer211.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_refresh_time112 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"[mm]", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time112" )
		self.lbl_refresh_time112.Wrap( -1 )

		self.lbl_refresh_time112.SetToolTip( u"Trace width in [mm]" )

		bSizer211.Add( self.lbl_refresh_time112, 0, wx.ALL, 5 )

		self.m_ctrlTrackWidth = SpinCtrlDoublePersist( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, 0.127, 10, 0.134000, 0.001, u"m_ctrlTrackWidth" )
		self.m_ctrlTrackWidth.SetDigits( 3 )
		bSizer211.Add( self.m_ctrlTrackWidth, 0, wx.ALL, 5 )


		sbSizer1.Add( bSizer211, 1, wx.EXPAND, 5 )

		bSizer22111 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time2111 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Track fillet radius:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time2111" )
		self.lbl_refresh_time2111.Wrap( -1 )

		bSizer22111.Add( self.lbl_refresh_time2111, 0, wx.ALL, 5 )


		bSizer22111.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_refresh_time1122 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"[mm]", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time1122" )
		self.lbl_refresh_time1122.Wrap( -1 )

		self.lbl_refresh_time1122.SetToolTip( u"Trace width in [mm]" )

		bSizer22111.Add( self.lbl_refresh_time1122, 0, wx.ALL, 5 )

		self.m_ctrlRfill = SpinCtrlDoublePersist( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, 0, 100, 0.000000, 0.1, u"m_ctrlRfill" )
		self.m_ctrlRfill.SetDigits( 3 )
		self.m_ctrlRfill.SetToolTip( u"Radius used to smooth the coil corners" )

		bSizer22111.Add( self.m_ctrlRfill, 0, wx.ALL, 5 )


		sbSizer1.Add( bSizer22111, 1, wx.EXPAND, 5 )

		bSizer271 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time131122 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Terminal pads:", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time1311" )
		self.lbl_refresh_time131122.Wrap( -1 )

		bSizer271.Add( self.lbl_refresh_time131122, 0, wx.ALL, 5 )


		bSizer271.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		m_cbTPChoices = [ u"THT", u"SMD" ]
		self.m_cbTP = wx.ComboBox( sbSizer1.GetStaticBox(), wx.ID_ANY, u"THT", wx.DefaultPosition, wx.Size( 90,20 ), m_cbTPChoices, wx.CB_DROPDOWN|wx.CB_READONLY, wx.DefaultValidator, u"m_cbTP" )
		self.m_cbTP.SetSelection( 0 )
		bSizer271.Add( self.m_cbTP, 0, wx.ALL, 5 )

		self.lbl_refresh_time1311221 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"[mm2]", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time1311" )
		self.lbl_refresh_time1311221.Wrap( -1 )

		bSizer271.Add( self.lbl_refresh_time1311221, 0, wx.ALL, 5 )

		m_termSizeChoices = [ u"0.1", u"0.15", u"0.25", u"0.5", u"0.75", u"1.0", u"1.5", u"2.0", u"2.5" ]
		self.m_termSize = wx.ComboBox( sbSizer1.GetStaticBox(), wx.ID_ANY, u"0.1", wx.DefaultPosition, wx.Size( 150,20 ), m_termSizeChoices, wx.CB_DROPDOWN|wx.CB_READONLY, wx.DefaultValidator, u"m_cbTPSize" )
		self.m_termSize.SetSelection( 1 )
		bSizer271.Add( self.m_termSize, 0, wx.ALL, 5 )


		sbSizer1.Add( bSizer271, 1, wx.EXPAND, 5 )


		bSizer5.Add( sbSizer1, 1, wx.EXPAND|wx.TOP, 8 )

		sbSizer111 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Physics / Stats" ), wx.VERTICAL )

		bSizer2112 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time113 = wx.StaticText( sbSizer111.GetStaticBox(), wx.ID_ANY, u"Temperature (ambient):", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time113" )
		self.lbl_refresh_time113.Wrap( -1 )

		self.lbl_refresh_time113.SetToolTip( u"Trace width in [mm]" )

		bSizer2112.Add( self.lbl_refresh_time113, 0, wx.ALL, 5 )


		bSizer2112.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_refresh_time1121 = wx.StaticText( sbSizer111.GetStaticBox(), wx.ID_ANY, u"[deg C]", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time1121" )
		self.lbl_refresh_time1121.Wrap( -1 )

		self.lbl_refresh_time1121.SetToolTip( u"Trace width in [mm]" )

		bSizer2112.Add( self.lbl_refresh_time1121, 0, wx.ALL, 5 )

		self.m_ambT = SpinCtrlDoublePersist( sbSizer111.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_RIGHT|wx.SP_ARROW_KEYS, -50, 150, 20, 0.1, u"m_ambT" )
		self.m_ambT.SetDigits( 1 )
		bSizer2112.Add( self.m_ambT, 0, wx.ALL, 5 )


		sbSizer111.Add( bSizer2112, 1, wx.EXPAND, 5 )

		bSizer21321 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time1321 = wx.StaticText( sbSizer111.GetStaticBox(), wx.ID_ANY, u"Phase wire length", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time1321" )
		self.lbl_refresh_time1321.Wrap( -1 )

		bSizer21321.Add( self.lbl_refresh_time1321, 0, wx.ALL, 5 )


		bSizer21321.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_phaseLength = wx.StaticText( sbSizer111.GetStaticBox(), wx.ID_ANY, u"-", wx.DefaultPosition, wx.Size( 140,20 ), wx.ALIGN_RIGHT, u"lbl_phaseLength" )
		self.lbl_phaseLength.Wrap( -1 )

		bSizer21321.Add( self.lbl_phaseLength, 0, wx.ALL, 5 )

		self.lbl_refresh_time13121111 = wx.StaticText( sbSizer111.GetStaticBox(), wx.ID_ANY, u"[mm]", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time13121111" )
		self.lbl_refresh_time13121111.Wrap( -1 )

		bSizer21321.Add( self.lbl_refresh_time13121111, 0, wx.ALL, 5 )


		sbSizer111.Add( bSizer21321, 1, wx.EXPAND, 5 )

		bSizer21312 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time1313 = wx.StaticText( sbSizer111.GetStaticBox(), wx.ID_ANY, u"Phase resistance (R)", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time1313" )
		self.lbl_refresh_time1313.Wrap( -1 )

		bSizer21312.Add( self.lbl_refresh_time1313, 0, wx.ALL, 5 )


		bSizer21312.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_phaseR = wx.StaticText( sbSizer111.GetStaticBox(), wx.ID_ANY, u"-", wx.DefaultPosition, wx.Size( 140,20 ), wx.ALIGN_RIGHT, u"lbl_phaseR" )
		self.lbl_phaseR.Wrap( -1 )

		bSizer21312.Add( self.lbl_phaseR, 0, wx.ALL, 5 )

		self.lbl_refresh_time13121 = wx.StaticText( sbSizer111.GetStaticBox(), wx.ID_ANY, u"[ohm]", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time13121" )
		self.lbl_refresh_time13121.Wrap( -1 )

		bSizer21312.Add( self.lbl_refresh_time13121, 0, wx.ALL, 5 )


		sbSizer111.Add( bSizer21312, 1, wx.EXPAND, 5 )

		bSizer2132 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time132 = wx.StaticText( sbSizer111.GetStaticBox(), wx.ID_ANY, u"Phase inductance (L)", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time132" )
		self.lbl_refresh_time132.Wrap( -1 )

		bSizer2132.Add( self.lbl_refresh_time132, 0, wx.ALL, 5 )


		bSizer2132.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_phaseL = wx.StaticText( sbSizer111.GetStaticBox(), wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_phaseL" )
		self.lbl_phaseL.Wrap( -1 )

		bSizer2132.Add( self.lbl_phaseL, 0, wx.ALL, 5 )

		self.lbl_refresh_time1312111 = wx.StaticText( sbSizer111.GetStaticBox(), wx.ID_ANY, u"[uH]", wx.DefaultPosition, wx.DefaultSize, 0, u"lbl_refresh_time1312111" )
		self.lbl_refresh_time1312111.Wrap( -1 )

		bSizer2132.Add( self.lbl_refresh_time1312111, 0, wx.ALL, 5 )


		sbSizer111.Add( bSizer2132, 1, wx.EXPAND, 5 )


		bSizer5.Add( sbSizer111, 1, wx.EXPAND|wx.TOP, 8 )


		bSizer5.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

		self.btn_load = wx.Button( self, wx.ID_OK, u"Load", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"btn_ok" )
		bSizer3.Add( self.btn_load, 0, wx.ALIGN_CENTER_VERTICAL, 5 )

		self.btn_save = wx.Button( self, wx.ID_OK, u"Save", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"btn_ok" )
		bSizer3.Add( self.btn_save, 0, wx.ALL, 5 )


		bSizer3.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.btn_clear = wx.Button( self, wx.ID_ANY, u"Clear", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"btn_clear" )
		self.btn_clear.Enable( False )
		self.btn_clear.Hide()

		bSizer3.Add( self.btn_clear, 0, wx.ALL, 5 )

		self.btn_ok = wx.Button( self, wx.ID_OK, u"Generate", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"btn_ok" )
		bSizer3.Add( self.btn_ok, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )


		bSizer5.Add( bSizer3, 0, wx.EXPAND|wx.TOP, 5 )


		bSizer1.Add( bSizer5, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.on_close )
		self.m_cbOutline.Bind( wx.EVT_TEXT, self.on_cb_outline )
		self.m_cbMountSize.Bind( wx.EVT_TEXT, self.on_cb_mholes )
		self.m_cbScheme.Bind( wx.EVT_TEXT, self.on_cb_connections )
		self.m_cbStrategy.Bind( wx.EVT_TEXT, self.on_cb_outline )
		self.m_cbPreset.Bind( wx.EVT_TEXT, self.on_cb_preset )
		self.m_ctrlLayers.Bind( wx.EVT_SPINCTRLDOUBLE, self.on_nr_layers )
		self.m_cbTP.Bind( wx.EVT_TEXT, self.on_cb_trmtype )
		self.m_termSize.Bind( wx.EVT_TEXT, self.on_cb_connections )
		self.btn_load.Bind( wx.EVT_BUTTON, self.on_btn_load )
		self.btn_save.Bind( wx.EVT_BUTTON, self.on_btn_save )
		self.btn_clear.Bind( wx.EVT_BUTTON, self.on_btn_clear )
		self.btn_ok.Bind( wx.EVT_BUTTON, self.on_btn_generate )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def on_close( self, event ):
		event.Skip()

	def on_cb_outline( self, event ):
		event.Skip()

	def on_cb_mholes( self, event ):
		event.Skip()

	def on_cb_connections( self, event ):
		event.Skip()


	def on_cb_preset( self, event ):
		event.Skip()

	def on_nr_layers( self, event ):
		event.Skip()

	def on_cb_trmtype( self, event ):
		event.Skip()


	def on_btn_load( self, event ):
		event.Skip()

	def on_btn_save( self, event ):
		event.Skip()

	def on_btn_clear( self, event ):
		event.Skip()

	def on_btn_generate( self, event ):
		event.Skip()


