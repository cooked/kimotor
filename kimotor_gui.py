# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-253-g8e3463c9)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class KiMotorGUI
###########################################################################

class KiMotorGUI ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"KiMotor", pos = wx.DefaultPosition, size = wx.Size( 450,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.STAY_ON_TOP|wx.TAB_TRAVERSAL, name = u"kimotor" )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer5 = wx.BoxSizer( wx.VERTICAL )


		bSizer5.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel1, wx.ID_ANY, u"General" ), wx.VERTICAL )

		bSizer221 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time21 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"D_out [mm]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time21.Wrap( -1 )

		bSizer221.Add( self.lbl_refresh_time21, 0, wx.ALL, 5 )


		bSizer221.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlDout = wx.SpinCtrlDouble( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 10, 1000, 100, 1 )
		self.m_ctrlDout.SetDigits( 2 )
		self.m_ctrlDout.SetToolTip( u"Stator outer diameter (NOTE: coil outer diameter is calculated subtracting from this the mounting ring width)" )

		bSizer221.Add( self.m_ctrlDout, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer221, 1, wx.EXPAND, 5 )

		bSizer2212 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_cbWmnt = wx.CheckBox( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_cbWmnt.SetValue(True)
		bSizer2212.Add( self.m_cbWmnt, 0, wx.ALL, 5 )

		self.lbl_refresh_time212 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"w_mount [mm]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time212.Wrap( -1 )

		self.lbl_refresh_time212.SetToolTip( u"Width of the mounting ring (exposed copper annular))" )

		bSizer2212.Add( self.lbl_refresh_time212, 0, wx.ALL, 5 )


		bSizer2212.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlWmnt = wx.SpinCtrlDouble( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 0, 50, 5, 0.1 )
		self.m_ctrlWmnt.SetDigits( 2 )
		self.m_ctrlWmnt.SetToolTip( u"Stator outer diameter (NOTE: coil outer diameter is calculated subtracting from this the mounting ring width)" )

		bSizer2212.Add( self.m_ctrlWmnt, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer2212, 1, wx.EXPAND, 5 )

		bSizer22121 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_cbWterm = wx.CheckBox( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_cbWterm.SetValue(True)
		bSizer22121.Add( self.m_cbWterm, 0, wx.ALL, 5 )

		self.lbl_refresh_time2121 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"w_terminals [mm]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time2121.Wrap( -1 )

		self.lbl_refresh_time2121.SetToolTip( u"Width of the mounting ring (exposed copper annular))" )

		bSizer22121.Add( self.lbl_refresh_time2121, 0, wx.ALL, 5 )


		bSizer22121.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlWtrm = wx.SpinCtrlDouble( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 0, 50, 4, 0.1 )
		self.m_ctrlWtrm.SetDigits( 2 )
		self.m_ctrlWtrm.SetToolTip( u"Stator outer diameter (NOTE: coil outer diameter is calculated subtracting from this the mounting ring width)" )

		bSizer22121.Add( self.m_ctrlWtrm, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer22121, 1, wx.EXPAND, 5 )

		bSizer22 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time2 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"D_in [mm]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time2.Wrap( -1 )

		bSizer22.Add( self.lbl_refresh_time2, 0, wx.ALL, 5 )


		bSizer22.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlDin = wx.SpinCtrlDouble( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 10, 1000, 30.000000, 1 )
		self.m_ctrlDin.SetDigits( 2 )
		self.m_ctrlDin.SetToolTip( u"Diameter " )

		bSizer22.Add( self.m_ctrlDin, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer22, 1, wx.EXPAND, 5 )

		bSizer2211 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time211 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"D_bore [mm]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time211.Wrap( -1 )

		bSizer2211.Add( self.lbl_refresh_time211, 0, wx.ALL, 5 )


		bSizer2211.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlDbore = wx.SpinCtrlDouble( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 10, 1000, 10, 1 )
		self.m_ctrlDbore.SetDigits( 2 )
		self.m_ctrlDbore.SetToolTip( u"Diameter of the shaft pass-through bore" )

		bSizer2211.Add( self.m_ctrlDbore, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer2211, 1, wx.EXPAND, 5 )

		bSizer22111 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time2111 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"R_fillet [mm]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time2111.Wrap( -1 )

		bSizer22111.Add( self.lbl_refresh_time2111, 0, wx.ALL, 5 )


		bSizer22111.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlRfill = wx.SpinCtrlDouble( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 0, 100, 0.200000, 0.1 )
		self.m_ctrlRfill.SetDigits( 2 )
		self.m_ctrlRfill.SetToolTip( u"Radius used to smooth the coil corners" )

		bSizer22111.Add( self.m_ctrlRfill, 0, wx.ALL, 5 )


		sbSizer2.Add( bSizer22111, 1, wx.EXPAND, 5 )


		bSizer5.Add( sbSizer2, 1, wx.EXPAND, 5 )


		bSizer5.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel1, wx.ID_ANY, u"Electrical" ), wx.VERTICAL )

		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Nr. of Poles:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time.Wrap( -1 )

		bSizer2.Add( self.lbl_refresh_time, 0, wx.ALL, 5 )


		bSizer2.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlPoles = wx.SpinCtrlDouble( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 140,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 3, 60, 6, 3 )
		self.m_ctrlPoles.SetDigits( 0 )
		bSizer2.Add( self.m_ctrlPoles, 0, wx.ALL, 5 )


		sbSizer1.Add( bSizer2, 0, wx.EXPAND, 5 )

		bSizer21 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time1 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Nr. of Coil Loops:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time1.Wrap( -1 )

		bSizer21.Add( self.lbl_refresh_time1, 0, wx.ALL, 5 )


		bSizer21.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlLoops = wx.SpinCtrlDouble( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 140,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 1, 999, 40, 1 )
		self.m_ctrlLoops.SetDigits( 0 )
		bSizer21.Add( self.m_ctrlLoops, 0, wx.ALL, 5 )


		sbSizer1.Add( bSizer21, 1, wx.EXPAND, 5 )

		bSizer2121 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time121 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Preset", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time121.Wrap( -1 )

		bSizer2121.Add( self.lbl_refresh_time121, 0, wx.ALL, 5 )


		bSizer2121.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		m_cbPresetChoices = [ u"Custom", u"JLCPCB, 1-2L", u"JLCPCB, 4-6L" ]
		self.m_cbPreset = wx.ComboBox( sbSizer1.GetStaticBox(), wx.ID_ANY, u"JLCPCB, 6L", wx.DefaultPosition, wx.Size( 190,20 ), m_cbPresetChoices, 0 )
		self.m_cbPreset.SetSelection( 2 )
		self.m_cbPreset.Enable( False )

		bSizer2121.Add( self.m_cbPreset, 0, wx.ALL, 5 )


		sbSizer1.Add( bSizer2121, 1, wx.EXPAND, 5 )

		bSizer212 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time12 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Nr. of PCB layers:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time12.Wrap( -1 )

		bSizer212.Add( self.lbl_refresh_time12, 0, wx.ALL, 5 )


		bSizer212.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlLayers = wx.SpinCtrlDouble( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 140,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 2, 6, 2, 2 )
		self.m_ctrlLayers.SetDigits( 0 )
		bSizer212.Add( self.m_ctrlLayers, 0, wx.ALL, 5 )


		sbSizer1.Add( bSizer212, 1, wx.EXPAND, 5 )

		bSizer211 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time11 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Track width", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time11.Wrap( -1 )

		self.lbl_refresh_time11.SetToolTip( u"Trace width in [mm]" )

		bSizer211.Add( self.lbl_refresh_time11, 0, wx.ALL, 5 )


		bSizer211.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_refresh_time112 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"[mm]", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time112.Wrap( -1 )

		self.lbl_refresh_time112.SetToolTip( u"Trace width in [mm]" )

		bSizer211.Add( self.lbl_refresh_time112, 0, wx.ALL, 5 )

		self.m_ctrlTrackWidth = wx.SpinCtrlDouble( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 140,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 0.127, 10, 0.127, 0.001 )
		self.m_ctrlTrackWidth.SetDigits( 3 )
		bSizer211.Add( self.m_ctrlTrackWidth, 0, wx.ALL, 5 )


		sbSizer1.Add( bSizer211, 1, wx.EXPAND, 5 )


		bSizer5.Add( sbSizer1, 1, wx.EXPAND, 5 )


		bSizer5.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		sbSizer11 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel1, wx.ID_ANY, u"Mechanical" ), wx.VERTICAL )

		bSizer213 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time13 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"Holes, outer:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time13.Wrap( -1 )

		bSizer213.Add( self.lbl_refresh_time13, 0, wx.ALL, 5 )


		bSizer213.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_mhOut = wx.SpinCtrlDouble( sbSizer11.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 140,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 0, 36, 6, 1 )
		self.m_mhOut.SetDigits( 0 )
		bSizer213.Add( self.m_mhOut, 0, wx.ALL, 5 )


		sbSizer11.Add( bSizer213, 1, wx.EXPAND, 5 )

		bSizer2131 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time131 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"   - D position", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time131.Wrap( -1 )

		bSizer2131.Add( self.lbl_refresh_time131, 0, wx.ALL, 5 )


		bSizer2131.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_refresh_time1312 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"[mm]", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time1312.Wrap( -1 )

		bSizer2131.Add( self.lbl_refresh_time1312, 0, wx.ALL, 5 )

		self.m_mhOutR = wx.SpinCtrlDouble( sbSizer11.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 140,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 10, 1000, 100.000000, 0.1 )
		self.m_mhOutR.SetDigits( 2 )
		bSizer2131.Add( self.m_mhOutR, 0, wx.ALL, 5 )


		sbSizer11.Add( bSizer2131, 1, wx.EXPAND, 5 )

		bSizer2111 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time111 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"Holes, inner:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time111.Wrap( -1 )

		self.lbl_refresh_time111.SetToolTip( u"Trace width in [mm]" )

		bSizer2111.Add( self.lbl_refresh_time111, 0, wx.ALL, 5 )


		bSizer2111.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_mhIn = wx.SpinCtrlDouble( sbSizer11.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 140,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 0, 36, 0, 1 )
		self.m_mhIn.SetDigits( 0 )
		bSizer2111.Add( self.m_mhIn, 0, wx.ALL, 5 )


		sbSizer11.Add( bSizer2111, 1, wx.EXPAND, 5 )

		bSizer21311 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time1311 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"   - D position", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time1311.Wrap( -1 )

		bSizer21311.Add( self.lbl_refresh_time1311, 0, wx.ALL, 5 )


		bSizer21311.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.lbl_refresh_time13111 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"[mm]", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time13111.Wrap( -1 )

		bSizer21311.Add( self.lbl_refresh_time13111, 0, wx.ALL, 5 )

		self.m_mhInR = wx.SpinCtrlDouble( sbSizer11.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 140,20 ), wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 10, 1000, 20, 0.1 )
		self.m_mhInR.SetDigits( 2 )
		bSizer21311.Add( self.m_mhInR, 0, wx.ALL, 5 )


		sbSizer11.Add( bSizer21311, 1, wx.EXPAND, 5 )


		bSizer5.Add( sbSizer11, 1, wx.EXPAND, 5 )


		bSizer5.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

		self.btn_load = wx.Button( self.m_panel1, wx.ID_ANY, u"Load", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.btn_load, 0, wx.ALL, 5 )

		self.btn_save = wx.Button( self.m_panel1, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.btn_save, 0, wx.ALL, 5 )


		bSizer3.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.btn_clear = wx.Button( self.m_panel1, wx.ID_ANY, u"Clear", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btn_clear.Enable( False )

		bSizer3.Add( self.btn_clear, 0, wx.ALL, 5 )

		self.btn_ok = wx.Button( self.m_panel1, wx.ID_OK, u"Generate", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.btn_ok, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )


		bSizer5.Add( bSizer3, 0, wx.EXPAND, 5 )


		self.m_panel1.SetSizer( bSizer5 )
		self.m_panel1.Layout()
		bSizer5.Fit( self.m_panel1 )
		bSizer1.Add( self.m_panel1, 1, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.on_close )
		self.m_cbPreset.Bind( wx.EVT_TEXT, self.on_cb_preset )
		self.m_ctrlLayers.Bind( wx.EVT_SPINCTRLDOUBLE, self.on_nr_layers )
		self.btn_load.Bind( wx.EVT_BUTTON, self.on_btn_load )
		self.btn_save.Bind( wx.EVT_BUTTON, self.on_btn_save )
		self.btn_clear.Bind( wx.EVT_BUTTON, self.on_btn_clear )
		self.btn_ok.Bind( wx.EVT_BUTTON, self.on_btn_generate )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def on_close( self, event ):
		event.Skip()

	def on_cb_preset( self, event ):
		event.Skip()

	def on_nr_layers( self, event ):
		event.Skip()

	def on_btn_load( self, event ):
		event.Skip()

	def on_btn_save( self, event ):
		event.Skip()

	def on_btn_clear( self, event ):
		event.Skip()

	def on_btn_generate( self, event ):
		event.Skip()


