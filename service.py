import os
import xbmc
import xbmcaddon
import xbmcgui

def getCpuTemperature():
	tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
	cpu_temp = tempFile.read()
	tempFile.close()
	return float(cpu_temp)/1000

def export_pin(pin):
	try:
		file = open("/sys/class/gpio/export","w")
		file.write(str(pin))
		file.close()
	except IOError:
		return 4
	return 0

def unexport_pin(pin):
	try:
		file = open("/sys/class/gpio/unexport","w")
		file.write(str(pin))
		file.close()
	except IOError:
		return 4
	return 0

def set_pin_direction(pin, direction):
	try:
		file = open("/sys/class/gpio/gpio"+ str(pin) +"/direction","w")
		file.write(direction)
		file.close()
	except IOError:
		return 4
	return 0
	
def set_pin_value(pin, value):
	try:
		file = open("/sys/class/gpio/gpio"+ str(pin) +"/value","w")
		file.write(str(value))
		file.close()
	except IOError:
		return 4
	return 0	
	
def check_is_raspberry():
	try:
		file = open("/sys/class/gpio/export","w")
		file.close()
	except:
		return 4
	return 0

if __name__ == '__main__':
	addon = xbmcaddon.Addon()
	name  = addon.getAddonInfo('name')

	if check_is_raspberry():
		line1 = addon.getLocalizedString(32000)
		line2 = addon.getLocalizedString(32001)
		xbmcgui.Dialog().ok(name, line1 , line2)
		quit()

	monitor        = xbmc.Monitor()
	Check_Interval = int(addon.getSetting('Check_Interval'))
	Control_Pin_3V = int(addon.getSetting('Control_Pin_3V'))
	Control_Pin_5V = int(addon.getSetting('Control_Pin_5V'))
	
	# Init control pin 3.3 V
	export_pin(Control_Pin_3V)
	set_pin_direction(Control_Pin_3V,'out')
		
	# Init control pin 5 V
	export_pin(Control_Pin_5V)
	set_pin_direction(Control_Pin_5V,'out')
	
	MSG_1 = addon.getLocalizedString(32002)
	Status = 'init'
	
	while not monitor.abortRequested():
		if monitor.waitForAbort(Check_Interval):
			# Free control pin 3.3 V
			unexport_pin(Control_Pin_3V)
	
			# Free control pin 5 V
			unexport_pin(Control_Pin_5V)		
			break

		Temperature    = int(getCpuTemperature())
		Check_Interval = int(addon.getSetting('Check_Interval'))		
		Temperature_3V = int(addon.getSetting('Temperature_3V'))
		Temperature_5V = int(addon.getSetting('Temperature_5V'))
		Display_Info   = str(addon.getSetting('Display_Info'))
		
		if Temperature <= Temperature_3V:
			set_pin_value(Control_Pin_3V, 0)
			set_pin_value(Control_Pin_5V, 0)
			if Display_Info == 'true' and Status != 'off':
				MSG_2 = addon.getLocalizedString(32003)
			Status = 'off'				
			
		if Temperature_3V <= Temperature <= Temperature_5V:
			set_pin_value(Control_Pin_3V, 1)
			set_pin_value(Control_Pin_5V, 0)
			if Display_Info == 'true' and Status != 'slow':
				MSG_2 = addon.getLocalizedString(32004)
			Status = 'slow'

		if Temperature_5V <= Temperature:
			set_pin_value(Control_Pin_3V, 0)
			set_pin_value(Control_Pin_5V, 1)
			if Display_Info == 'true' and Status != 'fast':
				MSG_2 = addon.getLocalizedString(32005)
			Status = 'fast'
			
		if Display_Info == 'true' and MSG_2:
			xbmcgui.Dialog().notification(name, MSG_1 + str(Temperature) + MSG_2)			
			MSG_2 = ''