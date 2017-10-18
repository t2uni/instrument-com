from ctypes import *
import os

CardType = {
    'USB_16PIO': 0x01,
    'USB_LABKIT': 0x02,
    'USB_16PR': 0x03,
    'USB_8PR': 0x06,
    'USB_4PR': 0x07,
    'USB_8PI': 0x08,
    'USB_8RO': 0x09,
    'USB_16PI': 0x0A,
    'USB_16RO': 0x0B,
    'USB_32PI': 0x0C,
    'USB_32RO': 0x0D,
}


if os.name == "posix":
    usbdii = CDLL("./usbdii.so")
else:
    usbdii = windll.usbdii


class RelaisCardSimulation:
    def __init__(self, card_type, path=''):
        self.channels = [0] * 4


    def check_connection(self, card_number):
        return True


    def connect(self, card_number):
        return True

    def disconnect(self):
        pass

    def set_digital_byte(self, channel, byte):
        byte_str = "{0:b}".format(byte)
        while len(byte_str) < 8:
            byte_str = "0" + byte_str
        print("set channel", channel, "=", byte_str)
        self.channels[channel] = byte

    def get_digital_byte(self, channel):
        return self.channels[channel]

class RelaisCard:
    def __init__(self, card_type, path = ' '):
        if isinstance(card_type, int):
            self.__card_type = c_uint(card_type)
        else:
            self.__card_type = c_uint(CardType[card_type])

        self.__device_path = c_char_p(path)
        self.__handle = 0


    def set_device_path(self, newpath):
        self.__device_path = newpath

    def check_connection(self, card_number):
        result = self.connect(card_number)
        self.disconnect()
        return result


    def connect(self, card_number):
        self.__handle = 0

        if os.name == "posix":
            self.__handle = usbdii.dcihid_open(self.__device_path, self.__card_type, card_number)
        elif os.name == "nt":
            self.__handle = usbdii.hid_OpenDevice(self.__card_type, card_number)

        if self.__handle == -1:
            return False

        return True

    def disconnect(self):
        if self.__handle != 0:
            handle_c = c_uint(self.__handle)
            if os.name == 'posix':
                usbdii.dcihid_close(handle_c)
            elif os.name == 'nt':
                usbdii.hid_CloseDevice(handle_c)
            self.__handle = 0

    def set_digital_byte(self, channel, byte):
        if(self.__handle == 0):
            raise Exception("Device not connected")

        channel_c = c_uint(channel)
        byte_c = c_ubyte(byte)
        handle_c = c_uint(self.__handle)

        res = -1

	if os.name == 'nt':
            res = usbdii.hid_SetDigitalByte(handle_c, channel_c, byte_c)
        elif os.name == 'posix':
            res = usbdii.dcihid_write(handle_c, channel_c, byte_c)
 
        if res == -1:
            raise Exception("Error: sending byte unsuccessful! Maybe USB connection was interrupted. Please connect device and restart program.")

    def get_digital_byte(self, channel):
        byte = c_ubyte(0)
        channel_c = c_uint(channel)
        handle_c = c_uint(self.__handle)

	if os.name == 'nt':
            usbdii.hid_GetDigitalByte(handle_c, channel_c, byref(byte))
        elif os.name ==  'posix':
            usbdii.dcihid_read(handle_c, channel_c, byref(byte))

        return byte.value




if __name__ == "__main__":
    card = RelaisCard(CardType["USB_16PIO"])
    if os.name == "posix":
        for i in range(16):
            if os.path.exists("/dev/usb/hiddev" + str(i)):
                card.set_device_path("/dev/usb/hiddev" + str(i))
                if card.check_connection(0):
                    print("device-path: /dev/usb/hiddev" + str(i), ": connection to card 0 successful!")
    elif os.name == "nt":
        for i in range(16):
            if card.check_connection(i):
                print("connection to card " + str(i) + " successful!")


