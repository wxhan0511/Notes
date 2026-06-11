import time

import hid
import common.convert

class UsbHid:
    def __init__(self, vid, pid, read_len=64, write_len=64):
        backend = usb.backend.libusb1.get_backend(
            find_library=lambda x: "/opt/homebrew/Cellar/libusb/1.0.27/lib/libusb-1.0.0.dylib")
        self.dev = usb.core.find(backend=backend, idVendor=vid, idProduct=pid)
        if self.dev is None:
            raise ValueError('Device not found')

        self.dev.set_configuration()
        self.config = self.dev.get_active_configuration()
        self.write_ep = usb.util.find_descriptor(self.config[(0, 0)],
                                                 custom_match=lambda e: usb.util.endpoint_direction(
                                                     e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        self.read_ep = usb.util.find_descriptor(self.config[(0, 0)],
                                                custom_match=lambda e: usb.util.endpoint_direction(
                                                    e.bEndpointAddress) == usb.util.ENDPOINT_IN)
        self.write_buf = [0] * write_len
        self.read_buf = [0] * read_len
        self.read_len = read_len
        self.write_len = write_len
        # print(self.dev)
        # print(self.read_ep)
        # print(self.write_ep)

    def write(self):
        self.dev.write(self.write_ep, self.write_buf, 30000)

    def read(self):
        return self.dev.read(self.read_ep, self.read_len, 30000)

    def command(self, main, sub, data):
        self.write_buf[0] = main
        self.write_buf[1] = sub
        self.write_buf[2] = data
        self.write()
        self.read()

    def get_dev_id(self):
        self.command(0x10, 0x04, [])
        print(self.read_buf)


class GcControl:
    def __init__(self, vid, pid, read_len=64, write_len=64):
        self.dev = hid.device()
        self.dev.open(vid, pid)
        print("Manufacturer: %s" % self.dev.get_manufacturer_string())
        print("Product: %s" % self.dev.get_product_string())
        print("Serial No: %s" % self.dev.get_serial_number_string())
        print("\r\n")
        self.write_buf = [0] * write_len
        self.read_buf = [0] * read_len
        self.read_len = read_len
        self.write_len = write_len

    # def write(self):
    #     self.dev.write(self.write_buf)

    def write(self, data):
        self.dev.write(data)

    def read(self):
        return self.dev.read(self.read_len)

    def command(self, main, sub, data):
        write_buf = [0, main, sub]
        write_buf += data
        if len(write_buf) != 65:
            write_buf += [0 for i in range(65 - len(write_buf))]
        self.dev.write(write_buf)
        return self.read()

    def command2(self, main, sub, data):
        write_buf = [0, main, sub]
        write_buf += data
        if len(write_buf) != 65:
            write_buf += [0 for i in range(65 - len(write_buf))]
        self.dev.write(write_buf)
        #return self.read()

    def lcd_write_reg(self, cmd, data):
        read_buf = self.command(0x30, 0x00, [0])

    def get_dev_id(self):
        read_buf = self.command(0x10, 0x04, [0])
        print(read_buf)

    def set_dev_power(self):
        read_buf = self.command(0x10, 0x04, [0])

    def set_single_power_vol(self, name, voltage):
        if name == "vcc":
            cmd = 0x01
        elif name == "iovcc":
            cmd = 0x02
        elif name == "io":
            cmd = 0x03
        elif name == "vsn":
            cmd = 0x04
        elif name == "vsp":
            cmd = 0x05
        elif name == "vdd":
            cmd = 0x06
        elif name == "led":
            cmd = 0x07
        else:
            cmd = name

        read_buf = self.command(0x20, 0x06, [cmd, voltage >> 8, voltage & 0xff])

    def master_cmd_set_power_en(self, en):
        read_buf = self.command(0x30, 0x00, [0x00, 0x01, en])

    def meter_cmd_get_id(self):
        read_buf = self.command(0xf2, 0x00, [0x00])
        #print(read_buf)
        print(hex(read_buf[4]))
        print(hex(read_buf[5]))
        print(hex(read_buf[6]))
        print(hex(read_buf[7]))

    def meter_cmd_get_hw_id(self):
        read_buf = self.command(0xf2, 0x00, [0x01])
        print(read_buf)
        print(hex(read_buf[4]))
        print(hex(read_buf[5]))
        print(hex(read_buf[6]))
        print(hex(read_buf[7]))

    def meter_cmd_get_single_power_current(self, channel, cali_en):
        read_buf = self.command(0xf2, 0x20, [0x04, channel, cali_en])
        status = read_buf[5]
        if read_buf[0] != 0xf2 or read_buf[1] != 0x20 or read_buf[2] != 0x04:
            print("error")
            return 0
        cur = common.convert.bytes_to_float(bytes([read_buf[6 + i] for i in range(4)]))
        gear = status >> 4
        if gear == 0:
            print(channel, "mA档", str(cur / 1000) + "mA")
            return cur / 1000
        else:
            print(channel, "uA档", str(cur) + "uA")
            return cur

    def meter_cmd_get_all_power_current(self):
        read_buf = self.command(0xf2, 0x20, [0x05])
        cur = []
        status = []
        for j in range(5):
            status.append(read_buf[5 * j + 4])
            cur.append(common.convert.bytes_to_float(bytes([read_buf[5 + i + 5 * j] for i in range(4)])))
            if status[j] >> 4 == 0:
                print(str(cur[j] / 1000) + "mA")
            else:
                print(str(cur[j]) + "uA")

    def meter_cmd_get_single_power_voltage(self, channel, cali_en):
        """
        获取单路电源电压
        :param cali_en: 0: 不校准 1: 校准
        :param channel: VSN VSP VCC IOVCC VDD LED
        :return: channel vol status
        """
        if channel == "vsn":
            name = 0
        elif channel == "vsp":
            name = 1
        elif channel == "vcc":
            name = 2
        elif channel == "iovcc":
            name = 3
        elif channel == "vdd":
            name = 4
        elif channel == "led":
            name = 6
        else:
            name = channel
        read_buf = self.command(0xf2, 0x20, [0x01, name, cali_en])
        channel = read_buf[4]
        status = read_buf[5]
        vol = common.convert.bytes_to_float(bytes([read_buf[6 + i] for i in range(4)]))
        print("channel ",channel,vol,status)
        return channel, vol, status

    def meter_cmd_get_single_voltage(self, mode, channel, cali_en):
        """
        获取单路电压
        :param cali_en: 0 close 1 open
        :param mode: 0: 24pin 1: 64pin 2: 4power
        :param channel: 24pin mode: 40-63 64pin mode: 0-63 4 power mode:vsn vsp iovcc vcc
        :return: vol
        """
        read_buf = self.command(0xf2, 0x20, [0x06, channel, mode, cali_en])
        channel = read_buf[4]
        vol = common.convert.bytes_to_float(bytes([read_buf[6 + i] for i in range(4)]))
        if mode == 1:
            print("cmd ", read_buf[0], "通道", channel, ": T", channel % 8, "-", int(channel / 8 + 1), "电压", vol,
                  "mV")
        return vol

    def meter_cmd_get_all_power_voltage(self):
        read_buf = self.command(0xf2, 0x20, [0x02])
        print(read_buf)
        vol = []
        status = []
        for j in range(5):
            status.append(read_buf[5 * j + 4])
            vol.append(common.convert.bytes_to_float(bytes([read_buf[5 + i + 5 * j] for i in range(4)])))
        print("vsn   ", status[0], vol[0])
        print("vsp   ", status[1], vol[1])
        print("vcc   ", status[2], vol[2])
        print("iovcc ", status[3], vol[3])
        print("vdd   ", status[4], vol[4])

    def meter_cmd_get_single_r_d(self, mode, pin_p, pin_n, ol_val, cali_en):
        """
        获取电阻二极管采样数据
        :param cali_en:
        :param mode: 0 二极管 1 电阻
        :param pin_p: 0-63
        :param pin_n: 0-63
        :param ol_val:
        :return dio: mV
        """
        byte_array = common.convert.float_to_bytes(ol_val)
        read_buf = self.command(0xf2, 0x20,
                                [0x07, pin_p, pin_n, mode, 0, cali_en, byte_array[0],byte_array[1],byte_array[2], byte_array[3]])
        # print("pin p " + hex(read_buf[4]))
        # print("pin n " + hex(read_buf[5]))
        print("ol status " + hex(read_buf[7]))
        dio = common.convert.bytes_to_float(bytes([read_buf[8 + i] for i in range(4)]))
        return dio

    def meter_cmd_get_single_res(self, pin_p, pin_n, gear, cali_en):
        """
        获取电阻二极管采样数据
        :param cali_en: 0 close 1 open
        :param gear: 1-7
        :param pin_n: 0-63
        :param pin_p: 0-63
        :return dio: mV
        """
        read_buf = self.command(0xf2, 0x20, [0x07, pin_p, pin_n, 1, gear, cali_en])
        # print("pin p " + hex(read_buf[4]))
        # print("pin n " + hex(read_buf[5]))
        # print("ol status " + hex(read_buf[6]))
        dio = common.convert.bytes_to_float(bytes([read_buf[8 + i] for i in range(4)]))
        # print([hex(read_buf[8 + i]) for i in range(4)])
        return dio

    def meter_cmd_set_bias_vol(self, group, channel, vol):
        """
        设定外灌电压
        :param group: 0: 24pin 1: 64pin 2: 3power
        :param channel: group0:40-63 group1:0-63 group2:0-3
        :param vol: v
        :return: 设定电压值
        """
        byte_array = common.convert.float_to_bytes(vol)
        read_buf = self.command(0xf2, 0x20,
                                [0x08, group, channel, byte_array[0], byte_array[1], byte_array[2], byte_array[3]])
        return common.convert.bytes_to_float(bytes([read_buf[5 + i] for i in range(4)]))

    def meter_cmd_get_bias_vol(self, cali_en):
        """
        获取外灌电压
        :return: 通道，[电流，档位]，[电压，档位]
        """
        read_buf = self.command(0xf2, 0x20, [0x09, cali_en])
        status = read_buf[3]
        if status == 1:
            print("未设置外灌电压")
            return None
        else:
            channel = read_buf[4]
            gear_cur = read_buf[5] >> 4
            cur = common.convert.bytes_to_float(bytes([read_buf[6 + j] for j in range(4)]))
            gear_vol = read_buf[10] >> 4
            vol = common.convert.bytes_to_float(bytes([read_buf[11 + j] for j in range(4)]))
            print("通道", channel, "电流", cur, "档位", gear_cur, "电压", vol, "档位", gear_vol)
            return channel, [cur, gear_cur], [vol, gear_vol]

    def meter_cmd_set_freq_voltage(self, group, channel, voltage):
        """
        :param voltage:
        :param channel: 0-23pin
        :return:
        """
        byte_array = common.convert.float_to_bytes(voltage)
        read_buf = self.command(0xf2, 0x20, [0x0a, group, channel,
                                             byte_array[0],byte_array[1],byte_array[2],byte_array[3]])

    def meter_cmd_get_freq(self):
        read_buf = self.command(0xf2, 0x20, [0x0b])
        freq = common.convert.bytes_to_float(bytes([read_buf[4 + j] for j in range(4)]))
        duty = common.convert.bytes_to_float(bytes([read_buf[8 + j] for j in range(4)]))
        print(freq,duty)
        return freq,duty

    def meter_cmd_set_cali_arg(self, cali_type, pos, arg_a, arg_b, arg_c):
        """
        设定校准参数
        :param cali_type: 0 VOL 1 VOL single small 2 VOL single big 3 CUR uA 4 CUR mA small 5 CUR mA big 6 RES 7 DIO
        :param pos: pos41
        :param arg_a:
        :param arg_b:
        :param arg_c:
        :return:
        """
        list_a = common.convert.double_to_bytes(arg_a)
        list_b = common.convert.double_to_bytes(arg_b)
        list_c = common.convert.double_to_bytes(arg_c)
        write_buf = [0x00, cali_type, pos]
        write_buf.extend(list_a)
        write_buf.extend(list_b)
        write_buf.extend(list_c)
        read_buf = self.command(0xf2, 0x30, write_buf)

    def meter_cmd_get_cali_arg(self, cali_type, pos):
        """
        读取校准参数
        :param cali_type: 0 VOL 1 VOL single small 2 VOL single big 3 CUR uA 4 CUR mA small 5 CUR mA big 6 RES 7 DIO
        :param pos: pos
        :return:
        """
        read_buf = self.command(0xf2, 0x30, [0x01, cali_type, pos])
        arg_a = common.convert.bytes_to_double(bytes([read_buf[5 + j] for j in range(8)]))
        arg_b = common.convert.bytes_to_double(bytes([read_buf[5 + 8 + j] for j in range(8)]))
        arg_c = common.convert.bytes_to_double(bytes([read_buf[5 + 16 + j] for j in range(8)]))
        print(arg_a, arg_b, arg_c)
        return arg_a, arg_b, arg_c

    def meter_cmd_update_cali_arg(self,log_en):
        """
        更新校准参数
        :return:
        """
        self.command(0xf2, 0x30, [0x02,log_en])

    def meter_cmd_active_cali_arg(self, active):
        """
        更新校准参数
        :return:
        """
        self.command(0xf2, 0x30, [0x03, active])

    def master_cmd_set_algo_img_name(self,num,name:str):
        print([num>>8, num&0xff] + list(name.encode("utf-8")))
        self.command(0x40, 0x0b, [num>>8, num&0xff] + list(name.encode("utf-8")))

    def master_cmd_show_algo_img_enable(self):
        self.command(0x80, 0x04,[])

    def master_cmd_send_algo_img(self,num):
        self.command(0x80, 0x05, [num>>8, num&0xff])

    def wait_key(self):
        self.command(0x30, 0x00, [0x00, 0x20])

def manual_current_cali_flow():
    res_ua = [20*1000,30*1000,40*1000,50*1000]
    res_b = [1000,500,300,200]
    res_s = [2000, 1000, 800, 500]
    res_iovcc = [1000,500,200,100]
    res_iovcc_b = [300, 200, 100, 60]
    gc = GcControl(0xc251, 0x3505)
    # gc.meter_cmd_active_cali_arg(0x8e)
    # gc.meter_cmd_update_cali_arg(1)

    # gc.meter_cmd_get_id()
    gc.set_dev_power()
    i = gc.meter_cmd_get_single_power_current(0,0)
    # i = gc.meter_cmd_get_single_power_current(1,0)
    for i in range(len(res_iovcc_b)):
        print(6000000/res_ua[i])

    #gc.meter_cmd_set_cali_arg(3, 0, 1.03714206,  9.48965467, 0)

if __name__ == '__main__':
    # manual_current_cali_flow()
    dev = GcControl(0xc251, 0x3505)
    dev.master_cmd_set_algo_img_name(0,"01_1.bmp")
    dev.master_cmd_set_algo_img_name(1, "01_2.bmp")
    dev.master_cmd_set_algo_img_name(2, "01_3.bmp")
    dev.master_cmd_set_algo_img_name(3, "01_4.bmp")
    dev.master_cmd_set_algo_img_name(4, "01_5.bmp")
    dev.master_cmd_show_algo_img_enable()
    dev.master_cmd_send_algo_img(3)
    # dev.master_cmd_show_algo_img(1)
    # time.sleep(3)
    # dev.master_cmd_send_algo_img(1)
    # dev.master_cmd_show_algo_img(1)
    # for i in range(64):
    # dev.meter_cmd_get_single_voltage(1, i,1)
    #dev.meter_cmd_get_single_voltage(0, 6, 0)
    # for i in range(14, 21, 1):
    #     vol = dev.meter_cmd_get_single_voltage(1, i, 1)
    #     dev.meter_cmd_set_freq_voltage(1, i, vol / 2)
    #     dev.meter_cmd_get_freq()
    # dev.meter_cmd_set_freq_voltage(1, 23, 900)
    # dev.meter_cmd_get_freq()
    # dev.meter_cmd_get_freq()
    # dev.meter_cmd_get_freq()    # dev.meter_cmd_set_freq_voltage(1, 24, 1800)
    # dev.meter_cmd_get_freq()
    # def meter_cmd_set_freq_voltage(self, channel,voltage):
    #     """
    #     :param voltage:
    #     :param channel: 0-23pin
    #     :return:
    #     """
    #     byte_array = common.convert.float_to_bytes(voltage)
    #     read_buf = self.command(0xf2, 0x20, [0x0a,0,channel,
    #                                          byte_array[0],byte_array[1],byte_array[2],byte_array[3]])
    #
    # def meter_cmd_get_freq(self):
    # dev.meter_cmd_set_bias_vol(0,0,4000)
    # dev.meter_cmd_set_freq_voltage(40,1500)
    # dev.meter_cmd_get_freq()
    # i = dev.meter_cmd_get_single_power_current(0, 1)
    # i = dev.meter_cmd_get_single_power_current(1, 1)
    # i = dev.meter_cmd_get_single_power_current(3, 1)
    #dev.meter_cmd_set_cali_arg(4,6,0.34140012,206.51997208,0)
    # dev.meter_cmd_set_cali_arg(3,6,0.72752053,256.67110398,0)
    # #dev.meter_cmd_set_cali_arg(5,1, 1.00494696,-0.15044497, 0)
    # dev.meter_cmd_update_cali_arg(1)
    # dev.meter_cmd_active_cali_arg(0x8f)

    # dev.meter_cmd_set_cali_arg(3, 0, 1.0442649305458138,10.707689512425743, 0)
    # dev.meter_cmd_set_cali_arg(3, 1, 1.0524281371661035, -20.87263596576027, 0)
    # dev.meter_cmd_set_cali_arg(3, 2, 1.062575422972273, -20.5307044592104, 0)
    # dev.meter_cmd_set_cali_arg(3, 3, 1.0703480166035662, -5.013076064325444, 0)
    # dev.meter_cmd_set_cali_arg(3, 4, 1.06119, -23.40546, 0)
    # dev.meter_cmd_set_cali_arg(3, 5, 1, 0, 0)
    #
    # dev.meter_cmd_update_cali_arg(1)
    # dev.meter_cmd_active_cali_arg(0x8e)0XF8
    # dev.meter_cmd_update_cali_arg(1)
    #dev.meter_cmd_get_single_power_current(0, 1)
    #dev.get_dev_id()
    #dio = dev.meter_cmd_get_single_r_d(0,24,27,1000,0)
    #print(dio)
    #dev.meter_cmd_set_bias_vol(0,0,1500)
    # dev.set_single_power_vol("vsn",6000)
    # dev.set_single_power_vol("vsp", 6000)



    #dev.meter_cmd_active_cali_arg(0x8f)
    # vol_24pin_list = ["TESTN_R","TESTP_R","TESTP_L","VDD_TP","DVDD","VDDML","VGMN","VGMP","VCL","NULL","NULL","VGHO","VGLO",
    #                   "VCOM_OPT","NULL","VCIP","NULL","VCOM","NULL","TVDD","NULL","VGL","NULL","VGH"]
    # vol_list = []
    #
    # dev.meter_cmd_get_single_power_current(0,1)
    # dev.meter_cmd_get_single_power_current(1, 1)
    # dev.meter_cmd_get_single_power_current(3, 1)
    #
    # dev.wait_key()
    #
    # time.sleep(2)
    #
    # dev.meter_cmd_get_single_power_current(0,1)
    # dev.meter_cmd_get_single_power_current(1, 1)
    # dev.meter_cmd_get_single_power_current(3, 1)
    #
    # dev.wait_key()
    #
    # time.sleep(2)
    #
    # dev.meter_cmd_get_single_power_current(0, 1)
    # dev.meter_cmd_get_single_power_current(1, 1)
    # dev.meter_cmd_get_single_power_current(3, 1)
    # vsn = dev.meter_cmd_get_single_power_voltage(0,1)
    # vsp = dev.meter_cmd_get_single_power_voltage(1, 1)
    # iovcc = dev.meter_cmd_get_single_power_voltage(3, 1)
    #
    # print(iovcc)
    # print(vsp)
    # print(vsn)
    # for i in range(24):
    #     if vol_24pin_list[23-i] != "NULL":
    #         vol = dev.meter_cmd_get_single_voltage(0,23-i,1)
    #         print(23-i,vol_24pin_list[23-i],vol/1000)
    # for i in range(24):
    #     if vol_24pin_list[i] != "NULL":
    #         vol = dev.meter_cmd_get_single_voltage(0,i,1)
    #         print(i,vol_24pin_list[i],vol)
   # dev.wait_key()
   #  i = 19
   #
   #  vol = dev.meter_cmd_get_single_voltage(0, i, 1)
   #  print(vol_24pin_list[i], vol)
   #  i = 12
   #
   #  vol = dev.meter_cmd_get_single_voltage(0, i, 1)
   #  print(vol_24pin_list[i], vol)
   #  i = 1
   #  vol = dev.meter_cmd_get_single_voltage(0, i, 1)
   #  print(vol_24pin_list[i], vol)
    #i = 6
    # vol = dev.meter_cmd_get_single_voltage(0, i, 1)
    # print(vol_24pin_list[i], vol)
    # dev.wait_key()
    #
    # for i in range(24):
    #     dev.meter_cmd_get_single_voltage(0,i,1)
    #
    # for i in range(24):
    #     dev.meter_cmd_get_single_voltage(0, 40 + i, 1)
    #dev.meter_cmd_set_freq_voltage(40,1600)
    #dev.meter_cmd_get_freq()
    # for i in range(64):
    #     dev.meter_cmd_get_single_voltage(1,i,1)
    # dev.set_single_power_vol("vsn",4500)
    # dev.meter_cmd_get_single_voltage(2, 0, 1)
    # dev.meter_cmd_get_single_voltage(2, 1, 1)
    # dev.meter_cmd_get_single_voltage(2, 2, 1)
    # dev.meter_cmd_get_single_voltage(2, 3, 1)
    #dev.meter_cmd_get_single_voltage(1, 15, 0)
    #dev.meter_cmd_get_single_voltage(1, 16, 0)
    # for i in range(24):
    #     dev.meter_cmd_get_single_voltage(0,40+i,1)

    #dev.meter_cmd_active_cali_arg(0x8f)
    #dev.meter_cmd_update_cali_arg()
    # for i in range(8):
    # res = dev.meter_cmd_get_single_res(8,1,0,1)
    # print(res)
    # res = dev.meter_cmd_get_single_res(1, 0, 0, 1)
    # print(res)
    #
    # for j in range(8):
    #     res = dev.meter_cmd_get_single_res(0,j,0,1)
    #     print(0,j,res)

    # dio_0 = dev.meter_cmd_get_single_r_d(0, 0, 1, 1000, 0)
    # dio_1 = dev.meter_cmd_get_single_r_d(0, 1, 0, 1000, 0)
    # print(dio_0, dio_1)
    # dio_0 = dev.meter_cmd_get_single_r_d(0, 0, 39, 1000, 0)
    # #print(dio_0)
    # dio_1 = dev.meter_cmd_get_single_r_d(0, 39, 0, 1000, 0)
    # print(dio_0, dio_1)

    # a = []
    # for i in range(40):
    #     for j in range(40):
    #         dio = dev.meter_cmd_get_single_r_d(0, i, j, 1000, 0)
    #         a.append(int(dio))
    #         print(i,j,int(dio))
    #
    # a = np.array(a).reshape(40, 40)
    pin_name = ['VSN', 'VSP', 'NULL', 'VDDI', 'NULL', 'GND', 'COG_TEST_3', 'TP_SPI_CS_N', 'TP_SPI_MOSI',
                'ATTN', 'TP_I2C_SDA', 'TP_I2C_SCL', 'TP_RESX', 'TP_SPI_MISO', 'TP_SPI_SCLK', 'COG_TEST_1',
                'GND', 'TP_SPI_MISO', 'TP_FLASH_SPI_SCLK', 'TP_SPI_CSN', 'GND', 'LED_PWM', 'FTE', 'RESX', 'GND', 'D0P',
                'D0N', 'GND', 'D1P', 'D1N', 'GND', 'CLK_P',
                'CLK_N', 'GND', 'D2P', 'D2N', 'GND', 'D3P', 'D3N', 'GND']

    # for i in range(40):
    #         dio_0 = dev.meter_cmd_get_single_r_d(0, i, 39 ,1000, 0)
    #         dio_1 = dev.meter_cmd_get_single_r_d(0, 39, i, 1000, 0)
    #         print(pin_name[i],"-",i,int(dio_0),int(dio_1))

    # for i in range(6,24,1):
    #         dio_0 = dev.meter_cmd_get_single_res(3, i ,0, 1)
    #         #dio_1 = dev.meter_cmd_get_single_res(39, i, 0, 1)
    #         print(pin_name[i],"-",i,int(dio_0))

    # for i in range(40):
    #         dio_0 = dev.meter_cmd_get_single_res(i, 39 ,0, 1)
    #         dio_1 = dev.meter_cmd_get_single_res(39, i, 0, 1)
    #         print(pin_name[i],"-",i,int(dio_0),int(dio_1))
    # df = pd.DataFrame(a, columns=pin_name, index=pin_name)
    # df.to_csv('test.csv')
    # dev.meter_cmd_get_single_power_current(0,1)
    # dev.meter_cmd_get_single_power_current(1,1)
    # dev.meter_cmd_get_single_power_current(3,1)

    # dev.meter_cmd_get_single_power_current(0,0)
    # dev.meter_cmd_get_single_power_current(1,0)
    # dev.meter_cmd_get_single_power_current(3,0)
    # dev.meter_cmd_get_single_power_voltage(0,1)
    # dev.meter_cmd_get_single_power_voltage(1,1)
    # dev.meter_cmd_get_single_power_voltage(3,1)




    # dev.set_single_power_vol("iovcc",2800)

    # # cali vol 5*2
    # dev.meter_cmd_set_cali_arg(0, 0, 1.14, 2049, 0)
    # dev.meter_cmd_set_cali_arg(0, 1, 2.14, 1049, 0)
    # dev.meter_cmd_set_cali_arg(0, 2, 3.14, 4049, 0)
    # dev.meter_cmd_set_cali_arg(0, 3, 4.14, 5049, 0)
    # dev.meter_cmd_set_cali_arg(0, 4, 5.14, 9049, 0)
    #
    # # cali vol single small 2*2
    # dev.meter_cmd_set_cali_arg(1, 0, 6.14, 2049, 0)
    # dev.meter_cmd_set_cali_arg(1, 1, 7.14, 1049, 0)
    #
    # # cali vol single big 1*2
    # dev.meter_cmd_set_cali_arg(2, 0, 8.14, 2049, 0)
    #
    # # cali cur uA 6*2
    # dev.meter_cmd_set_cali_arg(3, 0, 9.14, 2049, 0)
    # dev.meter_cmd_set_cali_arg(3, 1, 10.14, 1049, 0)
    # dev.meter_cmd_set_cali_arg(3, 2, 11.14, 4049, 0)
    # dev.meter_cmd_set_cali_arg(3, 3, 12.14, 5049, 0)
    # dev.meter_cmd_set_cali_arg(3, 4, 13.14, 9049, 0)
    # dev.meter_cmd_set_cali_arg(3, 5, 14.14, 9049, 0)
    #
    # # cali cur mA small 6*2
    # dev.meter_cmd_set_cali_arg(4, 0, 15.14, 2049, 0)
    # dev.meter_cmd_set_cali_arg(4, 1, 16.14, 1049, 0)
    # dev.meter_cmd_set_cali_arg(4, 2, 17.14, 4049, 0)
    # dev.meter_cmd_set_cali_arg(4, 3, 18.14, 5049, 0)
    # dev.meter_cmd_set_cali_arg(4, 4, 19.14, 9049, 0)
    # dev.meter_cmd_set_cali_arg(4, 5, 20.14, 9049, 0)
    #
    # # cali cur mA big 6*2
    # dev.meter_cmd_set_cali_arg(5, 0, 21.14, 2049, 0)
    # dev.meter_cmd_set_cali_arg(5, 1, 22.14, 1049, 0)
    # dev.meter_cmd_set_cali_arg(5, 2, 23.14, 4049, 0)
    # dev.meter_cmd_set_cali_arg(5, 3, 24.14, 5049, 0)
    # dev.meter_cmd_set_cali_arg(5, 4, 25.14, 9049, 0)
    # dev.meter_cmd_set_cali_arg(5, 5, 26.14, 9049, 0)
    #
    # #cali res 7*2
    # dev.meter_cmd_set_cali_arg(6, 0, 127.14, 51111, 51234)
    # dev.meter_cmd_set_cali_arg(6, 1, 128.14, 52222, 52345)
    # dev.meter_cmd_set_cali_arg(6, 2, 129.14, 53333, 53)
    # dev.meter_cmd_set_cali_arg(6, 3, 130.14, 54444, 54)
    # dev.meter_cmd_set_cali_arg(6, 4, 131.14, 55555, 55)
    # dev.meter_cmd_set_cali_arg(6, 5, 132.14, 56666, 56)
    # dev.meter_cmd_set_cali_arg(6, 6, 133.14, 57777, 57)
    #
    # #cali dio1 1*2
    # dev.meter_cmd_set_cali_arg(7, 0, 34.14, 2049, 0)

    # dev.meter_cmd_active_cali_arg(0x8f)
    # dev.meter_cmd_update_cali_arg()

    # dev.meter_cmd_get_cali_arg(6,0)
    # dev.meter_cmd_get_cali_arg(6,1)
    # dev.meter_cmd_get_cali_arg(6,2)
    # dev.meter_cmd_get_cali_arg(6,3)
    # dev.meter_cmd_get_cali_arg(6,4)
    # dev.meter_cmd_get_cali_arg(6,5)
    # dev.meter_cmd_set_cali_arg(7, 0, 34.14, 2049, 0)
    # dev.meter_cmd_set_cali_arg(6, 0, 134.14, 12049, 0)
    # dev.meter_cmd_get_cali_arg(7, 0)
    # dev.meter_cmd_update_cali_arg()

# # for i in range(5):
# #     dev.meter_cmd_get_single_power_voltage(i)
#
# dev.meter_cmd_get_id()
# dev.set_single_power_vol(1,2500)
# dev.meter_cmd_get_single_power_voltage(2)
# dev.meter_cmd_get_hw_id()
# dev.meter_cmd_get_all_power_voltage()
# dev.master_cmd_set_power_en(1)

# for i in range(100):
#     dev.meter_cmd_get_single_power_current(1)

# dev.meter_cmd_get_all_power_current()
# for i in range(2):
#     dev.meter_cmd_get_single_voltage(0,i)

# dev.meter_cmd_get_single_voltage(1,0)


# dev.meter_cmd_get_all_power_voltage()

# test_single_voltage_64pin(dev)
# dev.meter_cmd_get_single_voltage(1, 27)
# for i in range(1):
#     dev.meter_cmd_set_bias_vol(64 + 0,2.5)

# dev.meter_cmd_set_bias_vol(64 + 0,2.5)
# # time.sleep(2)
# for i in range(10):
#     dev.meter_cmd_get_bias_vol(65)
# dev.meter_cmd_get_single_voltage(1,0)

#     time.sleep(2)
# dev.meter_cmd_get_single_r_d(0,0,1,800)
# dev.meter_cmd_get_all_power_current()
# dev.meter_cmd_get_id()
# for i in range(100):
#     print("------------")
#     dev.meter_cmd_get_all_power_current()
# dev.meter_cmd_get_single_power_current(1)
# time.sleep(1)
# dev.meter_cmd_get_single_power_current(0)
# #time.sleep(1)
# dev.meter_cmd_get_single_power_current(1)
# #time.sleep(1)
# dev.meter_cmd_get_single_power_current(2)
# #time.sleep(1)
# dev.meter_cmd_get_single_power_current(3)
# #time.sleep(1)
# dev.meter_cmd_get_single_power_current(4)
# dev.meter_cmd_set_bias_vol(27,6000)
