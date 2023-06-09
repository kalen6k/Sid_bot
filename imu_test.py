import board
import adafruit_bno055
import time

# class BNO055_extended(adafruit_bno055.BNO055_I2C):
#     def get_calibration(self):
#         """Return the sensor's calibration data and return it as an array of
#         22 bytes. Can be saved and then reloaded with the set_calibration function
#         to quickly calibrate from a previously calculated set of calibration data.
#         """
#         # Switch to configuration mode, as mentioned in section 3.10.4 of datasheet.
#         self.mode = adafruit_bno055.CONFIG_MODE
#         # Read the 22 bytes of calibration data and convert it to a list (from
#         # a bytearray) so it's more easily serialized should the caller want to
#         # store it.
#         cal_data = list(self._read_registers(0X55, 22))
#         # Go back to normal operation mode.
#         self.mode = adafruit_bno055.NDOF_MODE
#         return cal_data
    
#     def _read_registers(self, register, length):
#         read_buffer = bytearray(23)
#         read_buffer[0] = register & 0xFF
#         with self.i2c_device as i2c:
#             i2c.write(read_buffer, start=0, end=1)
#             i2c.readinto(read_buffer, start=0, end=length)
#             return read_buffer[0:length]

# i2c = board.I2C()
# bno = BNO055_extended(i2c)
# bno.mode = adafruit_bno055.IMUPLUS_MODE

# while True:
#     (sys, gyro, accel, mag) = bno.calibration_status
#     print(sys, gyro, accel, mag)
#     if gyro==3 and accel==3:
#         print(bno.get_calibration())
#         break
#     time.sleep(0.5)
    
class BNO055_extended(adafruit_bno055.BNO055_I2C):
    def set_calibration(self, data):
        """Set the sensor's calibration data using a list of 22 bytes that
        represent the sensor offsets and calibration data.  This data should be
        a value that was previously retrieved with get_calibration (and then
        perhaps persisted to disk or other location until needed again).
        """        
        # Check that 22 bytes were passed in with calibration data.
        if data is None or len(data) != 22:
            raise ValueError('Expected a list of 22 bytes for calibration data.')
        # Switch to configuration mode, as mentioned in section 3.10.4 of datasheet.
        self.mode = adafruit_bno055.CONFIG_MODE
        # Set the 22 bytes of calibration data.
        self._write_register_data(0X55, data)
        # Go back to normal operation mode.
        self.mode = adafruit_bno055.NDOF_MODE
    
    def _write_register_data(self, register, data):
        write_buffer = bytearray(1)
        write_buffer[0] = register & 0xFF
        write_buffer[1:len(data)+1]=data
        with self.i2c_device as i2c:
            i2c.write(write_buffer, start=0, end=len(write_buffer))

i2c = board.I2C()
bno = BNO055_extended(i2c)
bno.mode = adafruit_bno055.IMUPLUS_MODE
bno.set_calibration([251, 255, 212, 255, 236, 255, 0, 0, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 232, 3, 0, 0])
while True:
    #(sys, gyro, accel, mag) = bno.calibration_status
    #print(sys, gyro, accel, mag)
    print(bno.euler[0])
    time.sleep(0.5)
