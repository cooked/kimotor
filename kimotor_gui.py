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
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"KiMotor", pos = wx.DefaultPosition, size = wx.Size( 353,454 ), style = wx.DEFAULT_FRAME_STYLE|wx.STAY_ON_TOP|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer5 = wx.BoxSizer( wx.VERTICAL )

		bSizer221 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time21 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"D_out [mm]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time21.Wrap( -1 )

		bSizer221.Add( self.lbl_refresh_time21, 0, wx.ALL, 5 )


		bSizer221.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlDout = wx.SpinCtrlDouble( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 10, 1000, 100, 1 )
		self.m_ctrlDout.SetDigits( 2 )
		bSizer221.Add( self.m_ctrlDout, 0, wx.ALL, 5 )


		bSizer5.Add( bSizer221, 1, wx.EXPAND, 5 )

		bSizer22 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time2 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"D_in [mm]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time2.Wrap( -1 )

		bSizer22.Add( self.lbl_refresh_time2, 0, wx.ALL, 5 )


		bSizer22.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlDin = wx.SpinCtrlDouble( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 10, 1000, 20, 1 )
		self.m_ctrlDin.SetDigits( 2 )
		bSizer22.Add( self.m_ctrlDin, 0, wx.ALL, 5 )


		bSizer5.Add( bSizer22, 1, wx.EXPAND, 5 )

		bSizer2211 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time211 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"D_bore [mm]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time211.Wrap( -1 )

		bSizer2211.Add( self.lbl_refresh_time211, 0, wx.ALL, 5 )


		bSizer2211.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlDbore = wx.SpinCtrlDouble( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 10, 1000, 10, 1 )
		self.m_ctrlDbore.SetDigits( 2 )
		bSizer2211.Add( self.m_ctrlDbore, 0, wx.ALL, 5 )


		bSizer5.Add( bSizer2211, 1, wx.EXPAND, 5 )

		bSizer22111 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time2111 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"R_fillet [mm]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time2111.Wrap( -1 )

		bSizer22111.Add( self.lbl_refresh_time2111, 0, wx.ALL, 5 )


		bSizer22111.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlRfill = wx.SpinCtrlDouble( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 0.1, 100, 1, 1 )
		self.m_ctrlRfill.SetDigits( 2 )
		bSizer22111.Add( self.m_ctrlRfill, 0, wx.ALL, 5 )


		bSizer5.Add( bSizer22111, 1, wx.EXPAND, 5 )

		bSizer221111 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time21111 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"R_flatten [mm]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time21111.Wrap( -1 )

		bSizer221111.Add( self.lbl_refresh_time21111, 0, wx.ALL, 5 )


		bSizer221111.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlRflatt = wx.SpinCtrlDouble( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 1, 100, 30, 0.1 )
		self.m_ctrlRflatt.SetDigits( 2 )
		bSizer221111.Add( self.m_ctrlRflatt, 0, wx.ALL, 5 )


		bSizer5.Add( bSizer221111, 1, wx.EXPAND, 5 )

		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Poles:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time.Wrap( -1 )

		bSizer2.Add( self.lbl_refresh_time, 0, wx.ALL, 5 )


		bSizer2.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlPoles = wx.SpinCtrlDouble( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 3, 60, 6, 3 )
		self.m_ctrlPoles.SetDigits( 0 )
		bSizer2.Add( self.m_ctrlPoles, 0, wx.ALL, 5 )


		bSizer5.Add( bSizer2, 0, wx.EXPAND, 5 )

		bSizer21 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time1 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Coil loops:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time1.Wrap( -1 )

		bSizer21.Add( self.lbl_refresh_time1, 0, wx.ALL, 5 )


		bSizer21.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlLoops = wx.SpinCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 1, 999, 20 )
		bSizer21.Add( self.m_ctrlLoops, 0, wx.ALL, 5 )


		bSizer5.Add( bSizer21, 1, wx.EXPAND, 5 )

		bSizer211 = wx.BoxSizer( wx.HORIZONTAL )

		self.lbl_refresh_time11 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Track width [mm]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl_refresh_time11.Wrap( -1 )

		bSizer211.Add( self.lbl_refresh_time11, 0, wx.ALL, 5 )


		bSizer211.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_ctrlTrackWidth = wx.SpinCtrlDouble( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL|wx.SP_ARROW_KEYS, 0, 10, 0.2, 0.1 )
		self.m_ctrlTrackWidth.SetDigits( 2 )
		bSizer211.Add( self.m_ctrlTrackWidth, 0, wx.ALL, 5 )


		bSizer5.Add( bSizer211, 1, wx.EXPAND, 5 )


		bSizer5.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

		self.btn_refresh = wx.Button( self.m_panel1, wx.ID_ANY, u"Clear", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.btn_refresh, 0, wx.ALL, 5 )


		bSizer3.Add( ( 0, 0), 1, wx.EXPAND, 5 )

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
		self.btn_refresh.Bind( wx.EVT_BUTTON, self.on_btn_clear )
		self.btn_ok.Bind( wx.EVT_BUTTON, self.on_btn_generate )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def on_btn_clear( self, event ):
		event.Skip()

	def on_btn_generate( self, event ):
		event.Skip()


