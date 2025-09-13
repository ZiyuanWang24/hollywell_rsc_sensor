import phi_rsc
import time

sensorrsc = phi_rsc.HRSC()
sensorrsc.sensor_info()
# Reset ADC
sensorrsc.adc_configure()
sensorrsc.rsc_test(2000)

def basicInfo():
	print("Testing RSC")
	print("1. Read the ADC settings and the compensation values from EEPROM.")
	sensorrsc.sensor_info()
	print("2. Initialize the ADC converter using the settings provided in EEPROM.")
	sensorrsc.adc_configure()
	print("3. Adjust the ADC sample rate if desired.")
	#sensorrsc.set_speed(20) #in SPS
	print("4. Command the ADC to take a temperature reading, and store this reading.")
	sensorrsc.read_temp()
	print("5. Give Delay (Example: if sample rate is 330SPS delay for 3.03 ms [1/330 s]).")
	time.sleep(0.004)
	print("6. Command the ADC to take a pressure reading, and store this reading.")
	sensorrsc.read_pressure()
	# 7. Apply the compensation formulae to the temperature and pressure readings in order to calculate a pressure value.
	sensorrsc.comp_readings(10,10)
	# 8. Repeat steps 4, 5 and 6 in a loop to take additional readings
	print(sensorrsc.comp_readings(10,10))
	print("All done!")
