import sys
from pathlib import Path
import re
import struct
import queue
import time

import hid
import numpy as np
from PySide6.QtCore import QObject, Signal

# import algo.cali_func as cf
# Ensure project root is importable when script is launched with a restricted sys.path.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# from device.rm55 import Rm55
# from view.burn_tool.fw_config import FirmwarePacket


def is_number(number):
    return bool(re.match(r'^-?\d+(\.\d+)?$', number))


def float_to_bytes(f):
    return struct.pack('f', f)


def bytes_to_float(b):
    return struct.unpack('f', b)[0]


def double_to_bytes(d):
    return struct.pack('d', d)


def bytes_to_double(b):
    return struct.unpack('d', b)[0]


def str_to_list(s: str) -> list:
    """将字符串转换为字符列表."""
    return list(s)


def list_to_str(lst: list) -> str:
    """将字符列表连接成一个字符串."""
    return ''.join(lst)


def list_to_hex(data):
    out = 0
    for i in range(len(data)):
        if data[i] == 'X':
            data[i] = '0'
        out |= int(data[i]) << i
    return hex(out)


def list_to_hex_2(data):
    out = 0
    for i in range(len(data) - 1, -1, -1):
        if data[i] == 'X':
            data[i] = '0'
        out |= int(data[i]) << (len(data) - i - 1)
    return hex(out)


class GcDevCore(QObject):
    send_data = Signal(list)
    send_cali_data = Signal(list)
    cali_finished = Signal()
    sig_cal_cali_arg = Signal(int, int)

    def __init__(self):
        super().__init__()
        self.gc_dev = hid.device()
        self.gc_dev_pid = 0x3505
        self.gc_dev_vid = 0xc251
        self.write_msg = queue.Queue()
        self.cali_flag = False
        self.async_flag = True
        self.params = None
        self.res_cali_gear_en = None
        self.rm55 = None
        self.run_flag = True
        self.dev_status = False
        self.run_mode = 0
        self.wait_flag = True
        # CRC-32相关变量
        self.POLY = 0xEDB88320
        self.crc_table = [0] * 256
        self.crc_table_initialized = False

        self.write_buf = [0] * 64
        self.read_buf = [0] * 64
        self.read_len = 64
        self.write_len = 64
        self.vol=0


    def crc32_table_init(self):
        """初始化CRC查找表"""
        for i in range(256):
            crc = i
            for j in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ self.POLY
                else:
                    crc = crc >> 1
            self.crc_table[i] = crc
        self.crc_table_initialized = True

    def crc32(self, data):
        """
        使用查找表计算CRC-32
        :param data: bytes或list类型的数据
        :return: CRC32值
        """
        if not self.crc_table_initialized:
            self.crc32_table_init()

        crc = 0xFFFFFFFF  # 初始CRC值

        # 确保data是字节类型
        if isinstance(data, list):
            data = bytes(data)

        for byte in data:
            crc = (crc >> 8) ^ self.crc_table[(crc ^ byte) & 0xFF]

        return (~crc) & 0xFFFFFFFF  # 返回结果时取反并确保是32位

    def open_device(self):
        if self.dev_status:
            return
        try:
            self.gc_dev.open(self.gc_dev_vid, self.gc_dev_pid)
            self.dev_status = True
        except IOError as e:
            self.dev_status = False
            print("open dev error", e)

    def close_device(self):
        self.gc_dev.close()
        self.dev_status = False
    def command(self, main, sub, data):
        write_buf = [0, main, sub]
        write_buf += data
        if len(write_buf) != 65:
            write_buf += [0 for i in range(65 - len(write_buf))]
        self.gc_dev.write(write_buf)
        return self.gc_dev.read(64)
    def debug_mode_exit(self):
        self.write_msg.put([0xff, 0x00])

    def delay(self, num):
        self.write_msg.put([0xff, 0x01, num])

    def cal_cali_arg(self, mode, channel):
        self.write_msg.put([0xff, 0x02, mode, channel])

    # def set_res(self, rm55: Rm55, res):
    #     if self.rm55 is None:
    #         self.rm55 = rm55
    #     self.write_msg.put([0xff, 0x03, res])

    def send_command(self, command):
        if command[0] == 0xff and command[1] == 0x00:
            self.run_mode = 0
            self.wait_flag = False
            print("debug mode exit")
            self.cali_finished.emit()
            return
        elif command[0] == 0xff and command[1] == 0x01:
            print("[delay]", command[2])
            self.thread().msleep(command[2])
            self.wait_flag = False
            return
        elif command[0] == 0xff and command[1] == 0x02:
            self.sig_cal_cali_arg.emit(command[2], command[3])
        elif command[0] == 0xff and command[1] == 0x03:
            if self.rm55.status:
                print(f"[rm55] set {command[2]}")
                self.rm55.set_r_value(command[2])
                self.wait_flag = False
            else:
                print("[rm55] disconnect")
            return
        write_buf = [0]
        write_buf += command
        if len(write_buf) != 65:
            write_buf += [0 for _ in range(65 - len(write_buf))]
        try:

            self.gc_dev.write(write_buf)
            a = time.time()
            data = self.gc_dev.read(64)
            b = time.time()
            # print((b - a) * 1000)
            #print(data)
            return data
            if len(data) == 64:
                self.send_data.emit(data)
        except Exception as e:
            print("send error", e)
            self.gc_dev.close()
            self.dev_status = False
        return None
    # def lcd_write_reg(self,cmd,data):
    #     if self.async_flag:
    #         self.write_msg.put([0x80, 0x01, 0x01])
    #     else:
    #         self.send_command(
    #             [0x30, 0x00, 0x00, 0, g, b, 0x0, 0x0, 0x0, 0x00])

    def send_gamma_image(self, r, g, b):
        if self.async_flag:
            self.write_msg.put([0x80, 0x01, 0x01])
        else:
            self.send_command(
                [0x80, 0x1, 0x1, r, g, b, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x0, 0x0, 0x0])
            # self.send_command([0x80, 0x01, 0x00, 204, 204, 204, 204, 204, 204, 204, 204, 204, 204,204,204])

    def send_gamma_image2(self):
        if self.async_flag:
            self.write_msg.put([0x80, 0x01, 0x01])
        else:
            self.send_command(
                [0x80, 0x1, 0x0, 0x1, 0x18, 0xf6, 0x0, 0x20, 0x0, 0x0, 0x0, 0x0, 0x50, 0x66, 0x1, 0x20, 0x1, 0x0, 0x0,
                 0x0, 0x94, 0x69, 0x0, 0x20, 0x64, 0xf2, 0x0, 0x20, 0x8c, 0x85, 0x0, 0x20, 0x0, 0x0, 0x0, 0x0, 0x64,
                 0xf2, 0x0, 0x20, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x5, 0x7a, 0x12, 0x8, 0x75, 0x5e, 0x12, 0x8,
                 0x98, 0x34, 0x12, 0x8, 0x0, 0x0, 0x0, 0x61])

    def set_power_en(self, en):
        if self.async_flag:
            self.write_msg.put([0x30, 0x00, 0x00, 0x01, en])
        else:
            self.send_command([0x30, 0x00, 0x00, 0x01, en])

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
        if self.async_flag:
            self.write_msg.put([0x20, 0x06, cmd, voltage >> 8, voltage & 0xff])
        else:
            self.send_command([0x20, 0x06, cmd, voltage >> 8, voltage & 0xff])

    # def send_firmware(self, packet: FirmwarePacket):
    #     temp_data = []
    #     temp_data[0] = 0x10
    #     temp_data[1] = 0x14
    #     temp_data[2] = packet.line_num >> 8
    #     temp_data[3] = packet.line_num & 0xff
    #     temp_data[4] = packet.packet_size
    #     for i in range(len(packet.packet_size)):
    #         temp_data.append(packet.data[i])

    #     # TODO crc32
    #     # uint32_t
    #     # crc = crc32( & temp_data[3], packet->packet_size);
    #     # temp_data[60 - 2] = crc >> 24;
    #     # temp_data[61 - 2] = crc >> 16;
    #     # temp_data[62 - 2] = crc >> 8;
    #     # temp_data[63 - 2] = crc & 0xff;

    #     if self.async_flag:
    #         self.write_msg.put(temp_data)
    #     else:
    #         self.send_command(temp_data)

    # def meter_res_cali_func(self, rm55, start_res, step, times, gear):
    #     rm55.set_r_value(start_res)
    #     set_res = start_res + step
    #     real = []
    #     meter = []
    #     for i in range(times):
    #         rm55.set_r_value(set_res)
    #         real.append(set_res)
    #         #time.sleep(1)
    #         val = self.meter_cmd_get_single_res(0, 1, gear, 0)  # channel 0
    #         meter.append(val)
    #         set_res += step
    #     line = cf.CalFunc("poly", start_res, start_res + (1 + times) * step, len(real))
    #     cali_arg = line.solution(np.array(meter), np.array(real))

    #     for i in range(times):
    #         error_a = real[i] / meter[i]
    #         error_b = real[i] / (meter[i] * cali_arg[0] + cali_arg[1])
    #         print(error_a, error_b, real[i], meter[i] * meter[i] * cali_arg[0] + meter[i] * cali_arg[1] + cali_arg[2])
    #     return cali_arg[0], cali_arg[1], cali_arg[2]

    def meter_res_cali_flow(self):
        self.cali_flag = True
        self.async_flag = False

        if self.res_cali_gear_en[0] == 2:
            arg = self.meter_res_cali_func(self.rm55, 10, 40, 5, 6)
            self.send_cali_data.emit(arg)

        if self.res_cali_gear_en[1] == 2:
            arg = self.meter_res_cali_func(self.rm55, 100, 150, 5, 5)
            self.send_cali_data.emit(arg)

        if self.res_cali_gear_en[2] == 2:
            arg = self.meter_res_cali_func(self.rm55, -800, 2000, 5, 4)
            self.send_cali_data.emit(arg)

        if self.res_cali_gear_en[3] == 2:
            arg = self.meter_res_cali_func(self.rm55, -8000, 20000, 5, 3)
            self.send_cali_data.emit(arg)

        if self.res_cali_gear_en[4] == 2:
            arg = self.meter_res_cali_func(self.rm55, -80000, 200000, 5, 2)
            self.send_cali_data.emit(arg)

        if self.res_cali_gear_en[5] == 2:
            arg = self.meter_res_cali_func(self.rm55, -800000, 4000000, 5, 1)
            self.send_cali_data.emit(arg)

        self.cali_finished.emit()
        self.cali_flag = False
        self.async_flag = True
        self.thread().currentThread().exit(0)

    def meter_get_device_sw_id(self):
        if self.async_flag:
            self.write_msg.put([0xf2, 0x00, 0x00])
        else:
            self.send_command([0xf2, 0x00, 0x00])

    def meter_get_device_hw_id(self):
        if self.async_flag:
            self.write_msg.put([0xf2, 0x00, 0x01])
        else:
            self.send_command([0xf2, 0x00, 0x01])

    def meter_get_power_voltage(self, channel, cali_en):
        if self.async_flag:
            self.write_msg.put([0xf2, 0x20, 0x01, channel, cali_en])
        else:
            self.send_command([0xf2, 0x20, 0x01, channel, cali_en])

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
        vol = bytes_to_float(bytes([read_buf[6 + i] for i in range(4)]))
        print("channel ",channel,vol,status)
        return channel, vol, status
    def meter_cmd_get_single_power_current(self, channel, cali_en):
        read_buf = self.command(0xf2, 0x20, [0x04, channel, cali_en])
        status = read_buf[5]
        if read_buf[0] != 0xf2 or read_buf[1] != 0x20 or read_buf[2] != 0x04:
            print("error")
            return 0
        cur = bytes_to_float(bytes([read_buf[6 + i] for i in range(4)]))
        gear = status >> 4
        if gear == 0:
            print(channel, "mA档", str(cur / 1000) + "mA")
            return cur / 1000
        else:
            print(channel, "uA档", str(cur) + "uA")
            return cur
    def meter_get_single_power_voltage(self, channel, group, gear, cali_en):
        """
        获取单路电压
        :param channel:
        :param group:
        :param gear: 0 small 1 big
        :param cali_en:
        """
        if self.async_flag:
            self.write_msg.put([0xf2, 0x20, 0x06, channel, group, gear, cali_en])
        else:
            self.send_command([0xf2, 0x20, 0x06, channel, group, gear, cali_en])

    def meter_get_cali_arg(self, cali_type, pos):
        """
        读取校准参数
        :param cali_type:
            0 VOL 1 VOL single small 2 VOL single big 3 CUR uA 4 CUR mA small 5 CUR mA big 6 RES 7 DIO
        :param pos: pos
        :return:
        """
        if self.async_flag:
            self.write_msg.put([0xf2, 0x30, 0x01, cali_type, pos])
        else:
            self.send_command([0xf2, 0x30, 0x01, cali_type, pos])

    # def meter_set_cali_arg(self, cali_type, pos, arg_a, arg_b, arg_c):
    #     """
    #     设定校准参数
    #     :param cali_type: 0 VOL 1 VOL single small 2 VOL single big 3 CUR uA 4 CUR mA small 5 CUR mA big 6 RES 7 DIO
    #     :param pos: pos41
    #     :param arg_a:
    #     :param arg_b:
    #     :param arg_c:
    #     :return:
    #     """
    #     list_a = common.convert.double_to_bytes(arg_a)
    #     list_b = common.convert.double_to_bytes(arg_b)
    #     list_c = common.convert.double_to_bytes(arg_c)
    #     write_buf = [0xf2, 0x30, 0x00, cali_type, pos]
    #     write_buf.extend(list_a)
    #     write_buf.extend(list_b)
    #     write_buf.extend(list_c)
    #     if self.async_flag:
    #         self.write_msg.put(write_buf)
    #     else:
    #         self.send_command(write_buf)

    def meter_cmd_get_single_res(self, pin_p, pin_n, gear, cali_en):
        """
        获取电阻二极管采样数据
        :param cali_en: 0 close 1 open
        :param gear: 1-7
        :param pin_n: 0-63
        :param pin_p: 0-63
        :return dio: mV
        """
        if self.async_flag:
            self.write_msg.put([0xf2, 0x20, 0x07, pin_p, pin_n, 1, gear, cali_en])
        else:
            self.send_command([0xf2, 0x20, 0x07, pin_p, pin_n, 1, gear, cali_en])

    def meter_cmd_get_single_dio(self, pin_p, pin_n, cali_en):
        """
        获取电阻二极管采样数据
        :param cali_en: 0 close 1 open
        :param gear: 1-7
        :param pin_n: 0-63
        :param pin_p: 0-63
        :return dio: mV
        """
        if self.async_flag:
            self.write_msg.put([0xf2, 0x20, 0x07, pin_p, pin_n, 0, 0, cali_en])
        else:
            self.send_command([0xf2, 0x20, 0x07, pin_p, pin_n, 0, 0, cali_en])

    def meter_cmd_set_freq_voltage(self, channel, voltage):
        """
        :param channel: 0-23pin
        :return:
        """
        byte_array = float_to_bytes(voltage)
        if self.async_flag:
            self.write_msg.put(
                [0xf2, 0x20, 0x0a, 0x00, channel, byte_array[0], byte_array[1], byte_array[2], byte_array[3]])
        else:
            self.send_command(
                [0xf2, 0x20, 0x0a, 0x00, channel, byte_array[0], byte_array[1], byte_array[2], byte_array[3]])

    def meter_cmd_get_freq(self):
        if self.async_flag:
            self.write_msg.put([0xf2, 0x20, 0x0b])
        else:
            self.send_command([0xf2, 0x20, 0x0b])
        freq = bytes_to_float(bytes([self.read_buf[4 + j] for j in range(4)]))
        duty = bytes_to_float(bytes([self.read_buf[8 + j] for j in range(4)]))
        print(freq,duty)
        return freq,duty

    def meter_cmd_set_bias_vol(self, group, channel, vol):
        byte_array = float_to_bytes(vol)
        if self.async_flag:
            self.write_msg.put([0xf2, 0x20, 0x08,
                                group, channel, byte_array[0], byte_array[1], byte_array[2], byte_array[3]])
        else:
            self.send_command([0xf2, 0x20, 0x08,
                               group, channel, byte_array[0], byte_array[1], byte_array[2], byte_array[3]])

    def meter_cmd_get_bias(self, cali_en, gear):
        if self.async_flag:
            self.write_msg.put([0xf2, 0x20, 0x09, cali_en, gear])
        else:
            self.send_command([0xf2, 0x20, 0x09, cali_en, gear])

    def meter_cmd_get_power_current(self, channel, cali_en, gear):
        if self.async_flag:
            self.write_msg.put([0xf2, 0x20, 0x04, channel, gear, cali_en])
        else:
            self.send_command([0xf2, 0x20, 0x04, channel, gear, cali_en])

    def meter_cmd_set_dac_value(self, channel, value):
        byte_array = float_to_bytes(value)
        if self.async_flag:
            self.write_msg.put([0xf2, 0x10, 0x04,
                                channel, byte_array[0], byte_array[1], byte_array[2], byte_array[3]])
        else:
            self.send_command([0xf2, 0x10, 0x04,
                               channel, byte_array[0], byte_array[1], byte_array[2], byte_array[3]])

    def meter_cmd_active_cali_arg(self, active: int):
        """
        更新校准参数
        :param active:0x8e 0x8f
        :return:
        """
        print(active)
        if self.async_flag:
            self.write_msg.put([0xf2, 0x30, 0x03, active])
        else:
            self.send_command([0xf2, 0x30, 0x03, active])

    def meter_cmd_fast_read_vol(self, channel, vol):
        if self.async_flag:
            self.write_msg.put([0xf2, 0x20, 0x0c, channel, 1])
        else:
            self.send_command([0xf2, 0x20, 0x0c, channel, 1])

    def run(self):
        print("normal thread start")
        while self.run_flag:
            if self.run_mode == 0:
                try:
                    msg = self.write_msg.get(timeout=1)
                    if msg is not None:
                        self.send_command(msg)
                except queue.Empty:
                    pass
            elif self.run_mode == 1:
                msg = self.write_msg.get(timeout=1)
                if msg is not None:
                    self.send_command(msg)
                    while self.wait_flag:
                        self.thread().msleep(10)
                    self.wait_flag = True

        print("normal thread stop")
        self.thread().currentThread().exit(0)

    def meter_cmd_update_bin(self, data):
        cmd = [i for i in range(60)]
        self.send_command([0xf2, 0x00, 0x08] + cmd)

    def meter_cmd_send_fw_bin(self, cmd_type, num, packet_num):

        data = [i + 1 for i in range(55)]
        crc32_value = self.crc32(data).to_bytes(4, byteorder='little')
        #print(hex(crc32_value[3]),hex(crc32_value[2]),hex(crc32_value[1]),hex(crc32_value[0]))
        #print(cmd_type << 4 | num)
        if cmd_type == 0:
            self.send_command(
                [0x40, 0x0c, (num<< 4)|cmd_type, packet_num >> 8, packet_num & 0xff, crc32_value[3], crc32_value[2],
                 crc32_value[1], crc32_value[0]] + data)
        elif cmd_type == 1:
            self.send_command([0x40, 0x0c, (num<< 4)|cmd_type])

    def cmd_d0_interface_cfg(self,mode,speed):
        """

        :param mode: 0 spi 1 i2c
        :param speed: mode 0: 0-7 mode 1: 0-1
        :return:
        """
        self.send_command([0xd0, 0x00, mode, speed])

    def cmd_d0_prepare_write_data(self,data):
        if len(data) > 58:
            send_cnt = int(len(data)/58)
            rec_cnt = len(data)%58
            addr = 0
            for i in range(0,send_cnt):
                addr = i*58
                size = 58
                self.send_command([0xd0, 0x01, addr >> 8, addr& 0xff,size >> 8,size & 0xff] + data[i:58*(i+1)])
            if rec_cnt > 0:
                addr = addr + 58
                size = rec_cnt
                self.send_command([0xd0, 0x01, addr >> 8, addr& 0xff,size >> 8,size & 0xff] + data[-rec_cnt:])

    def cmd_d0_write_prepare_data(self,size,cs_h_en,cs_low_en):
        self.send_command([0xd0, 0x02,size >> 8,size & 0xff,cs_h_en,cs_low_en])

    def cmd_d0_write_data(self,data,cs_h_en,cs_low_en):
        size = len(data)
        self.send_command([0xd0, 0x03,size >> 8,size & 0xff,cs_h_en,cs_low_en] + data)

    def cmd_d0_read_data(self,w_data,r_size,cs_h_en,cs_low_en):
        w_size = len(w_data)
        return self.send_command([0xd0, 0x04,w_size >> 8,w_size & 0xff,r_size >> 8,r_size & 0xff,cs_h_en,cs_low_en] + w_data)

    def cmd_d0_erase_flash(self,mode,pos):
        """

        :param mode: 0 erase block 1 erase sector
        :param pos: 24 bit
        :return:
        """
        self.send_command([0xd0, 0x05, mode,(pos>>16)&0xff,(pos>>8)&0xff,pos&0xff])

    def cmd_d0_program_flash(self,flag,addr,flash_data):
        """

        :param flag: 0 program 1-n prepare data
        :param addr: 24 bit
        :param flash_data: 58 bytes
        :return:
        """
        self.send_command([0xd0, 0x06,flag,(addr >> 16) & 0xff,(addr >> 8) & 0xff,addr & 0xff] + flash_data)


    def cmd_30_ssd_send(self,ctr,data):
        self.send_command([0x30, 0x00, 0x00, 0x11, len(data), ctr] + data)
    def cmd_31_ssd_read(self,write_type,addr,num):
        self.send_command([31, 0, 1,13, write_type, (addr>>8)&0xff,num])
    def cmd_d0_spi_16bit_write(self,addr,data):
        self.send_command([0xd0, 0x08,addr>>8,addr&0xff,data])

    def cmd_d0_spi_16bit_read(self,addr):
        ret = self.send_command([0xd0, 0x09,addr>>8,addr&0xff])
        return ret[3]

    def master_cmd_send_dmr_bin(self,bin_size,packet_cnt,name:str):
        print(hex(bin_size >> 24))
        print(hex(bin_size >> 16))
        print(hex(bin_size >> 8))
        print(hex(bin_size & 0xff))
        print([0xd0, 0x20, bin_size>>24, (bin_size>>16)&0xff,(bin_size>>8)&0xff,bin_size&0xff,packet_cnt>>8,packet_cnt&0xff])
        #self.send_command([0xd0, 0x20, bin_size>>24, bin_size>>16,bin_size>>8,bin_size&0xff,packet_cnt>>8,packet_cnt&0xff] + list(name.encode("utf-8")))

    def command2(self, main, sub, data):
        write_buf = [0, main, sub]
        write_buf += list(data)
        if len(write_buf) != 65:
            write_buf += [0 for i in range(65 - len(write_buf))]
        self.gc_dev.write(write_buf)

    def lcd_write_reg(self, cmd, data):
        return self.command(0x30, 0x00, [0])

    def get_dev_id(self):
        read_buf = self.command(0x10, 0x04, [0])
        print(read_buf)

    def set_dev_power(self):
        return self.command(0x10, 0x04, [0])

    def master_cmd_set_power_en(self, en):
        return self.command(0x30, 0x00, [0x00, 0x01, en])

    def master_cmd_set_algo_img_name(self, num, name: str):
        print([num >> 8, num & 0xff] + list(name.encode("utf-8")))
        return self.command(0x40, 0x0b, [num >> 8, num & 0xff] + list(name.encode("utf-8")))

    def master_cmd_show_algo_img_enable(self):
        return self.command(0x80, 0x04, [])

    def master_cmd_send_algo_img(self, num):
        return self.command(0x80, 0x05, [num >> 8, num & 0xff])

    def wait_key(self):
        return self.command(0x30, 0x00, [0x00, 0x20])

    def meter_cmd_get_single_voltage(self, mode, channel, cali_en):
        read_buf = self.command(0xf2, 0x20, [0x06, channel, mode, cali_en])
        channel = read_buf[4]
        vol = bytes_to_float(bytes([read_buf[6 + i] for i in range(4)]))
        if mode == 1:
            print("cmd ", read_buf[0], "通道", channel, ": T", channel % 8, "-", int(channel / 8 + 1), "电压", vol,
                  "mV")
        return vol
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
        list_a = double_to_bytes(arg_a)
        list_b = double_to_bytes(arg_b)
        list_c = double_to_bytes(arg_c)
        write_buf = [0x00, cali_type, pos]
        write_buf.extend(list_a)
        write_buf.extend(list_b)
        write_buf.extend(list_c)
        self.read_buf = self.command(0xf2, 0x30, write_buf)
    def meter_cmd_update_cali_arg(self,log_en):
        """
        更新校准参数
        :return:
        """
        self.command(0xf2, 0x30, [0x02,log_en])
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
        byte_array = float_to_bytes(ol_val)
        read_buf = self.command(0xf2, 0x20,
                                [0x07, pin_p, pin_n, mode, 0, cali_en, byte_array[0],byte_array[1],byte_array[2], byte_array[3]])
        # print("pin p " + hex(read_buf[4]))
        # print("pin n " + hex(read_buf[5]))
        print("ol status " + hex(read_buf[7]))
        dio =bytes_to_float(bytes([read_buf[8 + i] for i in range(4)]))
        return dio


class UsbHid:
    def __init__(self, vid, pid, read_len=64, write_len=64):
        try:
            import importlib
            usb = importlib.import_module("usb")
        except ImportError as exc:
            raise ImportError("UsbHid requires pyusb to be installed") from exc

        self.usb = usb
        backend = self.usb.backend.libusb1.get_backend(
            find_library=lambda x: "/opt/homebrew/Cellar/libusb/1.0.27/lib/libusb-1.0.0.dylib")
        self.dev = self.usb.core.find(backend=backend, idVendor=vid, idProduct=pid)
        if self.dev is None:
            raise ValueError('Device not found')

        self.dev.set_configuration()
        self.config = self.dev.get_active_configuration()
        self.write_ep = self.usb.util.find_descriptor(self.config[(0, 0)],
                                                      custom_match=lambda e: self.usb.util.endpoint_direction(
                                                          e.bEndpointAddress) == self.usb.util.ENDPOINT_OUT)
        self.read_ep = self.usb.util.find_descriptor(self.config[(0, 0)],
                                                     custom_match=lambda e: self.usb.util.endpoint_direction(
                                                         e.bEndpointAddress) == self.usb.util.ENDPOINT_IN)
        self.write_buf = [0] * write_len
        self.read_buf = [0] * read_len
        self.read_len = read_len
        self.write_len = write_len

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


class GcControl(GcDevCore):
    def __init__(self, vid, pid, read_len=64, write_len=64):
        super().__init__()
        self.gc_dev_vid = vid
        self.gc_dev_pid = pid
        self.async_flag = False
        self.read_len = read_len
        self.write_len = write_len
        self.write_buf = [0] * write_len
        self.read_buf = [0] * read_len
        self.open_device()
        if self.dev_status:
            print("Manufacturer: %s" % self.gc_dev.get_manufacturer_string())
            print("Product: %s" % self.gc_dev.get_product_string())
            print("Serial No: %s" % self.gc_dev.get_serial_number_string())
            print("\r\n")


def manual_current_cali_flow():
    res_ua = [20 * 1000, 30 * 1000, 40 * 1000, 50 * 1000]
    res_b = [1000, 500, 300, 200]
    res_s = [2000, 1000, 800, 500]
    res_iovcc = [1000, 500, 200, 100]
    res_iovcc_b = [300, 200, 100, 60]
    gc = GcControl(0xc251, 0x3505)
    gc.set_dev_power()
    i = gc.meter_cmd_get_single_power_current(0, 0)
    for i in range(len(res_iovcc_b)):
        print(6000000 / res_ua[i])

def test_3101_write_flash():
    def fspi_cs_low(_dev:GcDevCore):
        _dev.cmd_d0_write_data([0x4C, 0x05, 0xfa, 0x40, 0x00, 0x01, 0xcc, 0x30], 1, 1)

    def fspi_cs_high(_dev:GcDevCore):
        _dev.cmd_d0_write_data([0x4C, 0x05, 0xfa, 0x40, 0x00, 0x01, 0xcc, 0x31], 1, 1)

    def fspi_write(_dev:GcDevCore,data):
        w_data = [0x4C, 0x05, 0xfa, 0x40, 0x00, 0x01, 0xc8] + data
        if len(w_data) > 58:
            _dev.cmd_d0_prepare_write_data(w_data)
            _dev.cmd_d0_write_prepare_data(len(w_data),1,1)
        else:
            _dev.cmd_d0_write_data(w_data,1,1)

    def fspi_read(_dev:GcDevCore,r_size):
        return dev.cmd_d0_read_data([0x4C, 0x05, 0xfb, 0x40, 0x00, 0x01, 0xc8], r_size,1, 1)

    def erase_flash(_dev:GcDevCore):
        fspi_cs_low(_dev)
        fspi_write(_dev,0xab)
        fspi_cs_high(_dev)

        fspi_cs_low(_dev)
        fspi_write(_dev,0x06)
        fspi_cs_high(_dev)

        fspi_cs_low(_dev)
        fspi_write(_dev, 0x05)
        fspi_write(_dev, 0xff)
        ret = fspi_read(_dev, 1)
        if ret is not None and ret[3] & 0x02 == 1:
            fspi_cs_high(_dev)
        else:
            #retry?
            return

        fspi_cs_low(_dev)
        fspi_write(_dev, [0xDB,0x00,0x00,0x00])
        fspi_cs_high(_dev)

        fspi_cs_low(_dev)
        fspi_write(_dev, 0x05)
        fspi_write(_dev, 0xff)
        ret = fspi_read(_dev, 1)
        if ret is not None and ret[3] & 0x01 == 0:
            fspi_cs_high(_dev)
        else:
            #retry?
            return

        fspi_cs_low(_dev)
        fspi_write(_dev,0x06)
        fspi_cs_high(_dev)

        fspi_cs_low(_dev)
        fspi_write(_dev, 0x05)
        fspi_write(_dev, 0xff)
        ret = fspi_read(_dev, 1)
        if ret is not None and ret[3] & 0x02 == 1:
            fspi_cs_high(_dev)
        else:
            #retry?
            return

        fspi_cs_low(_dev)
        fspi_write(_dev, [0x20,0x01,0x00,0x00])
        fspi_cs_high(_dev)

        fspi_cs_low(_dev)
        fspi_write(_dev, 0x05)
        fspi_write(_dev, 0xff)
        ret = fspi_read(_dev, 1)
        if ret is not None and ret[3] & 0x01 == 0:
            fspi_cs_high(_dev)
        else:
            #retry?
            return

        fspi_cs_low(_dev)
        fspi_write(_dev, [0x05,0xFF,0x2B])
        fspi_cs_high(_dev)
        ret = fspi_read(_dev, 1)
        if ret is not None and ret[3] & 0x01 == 0:
            return

    def program_flash(_dev:GcDevCore,_addr,flash_data):
        fspi_cs_low(_dev)
        fspi_write(_dev,0x06)
        fspi_cs_high(_dev)

        fspi_cs_low(_dev)
        fspi_write(_dev, 0x05)
        fspi_write(_dev, 0xff)
        ret = fspi_read(_dev, 1)
        if ret is not None and ret[3] & 0x02 == 1:
            fspi_cs_high(_dev)
        else:
            #retry?
            return

        fspi_cs_low(_dev)
        fspi_write(_dev, [0x02,(_addr >> 16) & 0xff,(_addr >> 8) & 0xff,_addr & 0xff] + flash_data)
        fspi_cs_high(_dev)

        fspi_cs_low(_dev)
        fspi_write(_dev, 0x05)
        fspi_write(_dev, 0xff)
        ret = fspi_read(_dev, 1)
        if ret is not None and ret[3] & 0x01 == 0:
            fspi_cs_high(_dev)
        else:
            # retry?
            return


    # idm_code = [0x4C, 0x70, 0xb8, 0x5c, 0x2e, 0x17, 0x0b, 0x05, 0x02, 0x81, 0xc0, 0x60, 0x30, 0x98, 0x4c,
    # 0x26, 0x13, 0x09, 0x84, 0x42, 0xa1, 0xd0, 0xe8, 0x74, 0x3a, 0x9d, 0x4e, 0xa7, 0x53, 0x29, 0x14,
    # 0x0a, 0x05, 0x02, 0x81, 0x40, 0xa0, 0xd0, 0xe8, 0xf4, 0xfa, 0x7d, 0x3e, 0x9f, 0x4f, 0xa7, 0x53, 0x29,
    # 0x14, 0x0a, 0x05, 0x82, 0xc1, 0xe0, 0xf0, 0xf8, 0xfc, 0xfe, 0xff, 0x7f, 0x3f, 0x9f, 0xcf, 0xe7, 0x73]
    #
    # dummy_bin = [0]*68*1024
    #
    #
    #
    # dev = GcDevCore()
    # dev.async_flag = False
    # dev.open_device()
    #
    # #enter idm
    # dev.cmd_d0_prepare_write_data(idm_code)
    # dev.cmd_d0_write_prepare_data(len(idm_code),1,1)
    # dev.cmd_d0_write_data([0x4C, 0x0f, 0xf0],1,1)
    #
    # #init fspi
    # dev.cmd_d0_write_data([0x4C, 0x05, 0xfa, 0x40, 0x00, 0x01, 0xc4, 0x5e],1,1)
    # dev.cmd_d0_write_data([0x4C, 0x05, 0xfa, 0x40, 0x00, 0x01, 0xcc, 0x31],1,1)
    #
    # #erase flash
    # erase_flash(dev)
    #
    # #mipi write reg
    #
    #
    # #program flash
    # addr = 0
    # while addr < 0x11000:
    #     program_flash(dev,addr,dummy_bin[addr:addr+256])
    #     addr += 256
    #
    # #start fw
    # dev.cmd_d0_write_data([0x4C, 0x05, 0xfa, 0xC0, 0x00, 0x00,0x51,0x40],1,1)
    # dev.cmd_d0_write_data([0x4C, 0x0A, 0xf5],1,1)

def test_download():
    dev = GcDevCore()
    dev.async_flag = False
    dev.open_device()
    start = time.time()
    #dev.meter_cmd_send_fw_bin(0, 0, 0)

    for i in range(1192):
        dev.meter_cmd_send_fw_bin(0, 3, i)
        if i % 100 == 0:
            print(i)
    end = time.time()
    print(end - start)

def test_update():
    dev = GcDevCore()
    dev.async_flag = False
    dev.open_device()
    start = time.time()
    #dev.meter_cmd_send_fw_bin(0, 0, 0)
    dev.meter_cmd_send_fw_bin(1, 0, 0)
    end = time.time()
    print(end - start)

def binary_file_to_list(file_path):
    # 检查文件是否存在
    import os
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    try:
        with open(file_path, "rb") as f:  # 以二进制模式读取
            data = f.read()
            # 将 bytes 转换为 list[int]
            return list(data)
    except Exception as e:
        raise RuntimeError(f"读取文件时出错: {e}")
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
        vol = bytes_to_float(bytes([read_buf[6 + i] for i in range(4)]))
        print("channel ",channel,vol,status)
        return channel, vol, status

def test_dmr_bin(_dev:GcDevCore):
    import os
    dummy_bin = binary_file_to_list("../dmr_rtl_gvo_pm_dec1_bl0_bw0_sp0_lut32_inv.bin")
    #dummy_bin = [0] * 460 * 1024 *4
    print(len(dummy_bin))
    addr = 0
    packet_size = 192
    max_send_len = 58
    a = time.time()
    while addr < len(dummy_bin):
    #while addr < 55:
        #program_flash(dev,addr,dummy_bin[addr:addr+256])
        data_addr = 0
        crc32_value = _dev.crc32(dummy_bin[addr:addr+192]).to_bytes(4, byteorder='little')

        send_cnt = packet_size // max_send_len
        data_len_remain = packet_size % max_send_len

        for i in range(send_cnt):
            _dev.send_command([0xd0, 0x01,data_addr >> 8,data_addr & 0xff,max_send_len >> 8,max_send_len & 0xff]+ dummy_bin[addr:addr+max_send_len])
            addr += max_send_len
            data_addr += max_send_len

        if data_len_remain > 0:
            _dev.send_command([0xd0, 0x01, data_addr >> 8, data_addr & 0xff, data_len_remain >> 8, data_len_remain & 0xff] + dummy_bin[addr:addr + data_len_remain])
            addr += data_len_remain
            data_addr += data_len_remain

        ret = _dev.send_command([0xd0, 0x02,data_addr >> 8,data_addr & 0xff,0,0,crc32_value[3],crc32_value[2],crc32_value[1],crc32_value[0]])
        if ret[2] != 1:
            crc32_value_0 = _dev.crc32(dummy_bin[0:58]).to_bytes(4, byteorder='little')
            crc32_value_1 = _dev.crc32(dummy_bin[58:58*2]).to_bytes(4, byteorder='little')
            crc32_value_2 = _dev.crc32(dummy_bin[58*2:58*3]).to_bytes(4, byteorder='little')
            crc32_value_3 = _dev.crc32(dummy_bin[58*3:58*3+18]).to_bytes(4, byteorder='little')
            print("------------------------")
            print(crc32_value_0)
            print(crc32_value_1)
            print(crc32_value_2)
            print(crc32_value_3)
            print(addr)
            print(ret)
    b = time.time()
    print(b - a)

if __name__ == '__main__':
    #test_3101_write_flash()
    dev = GcDevCore()
    dev.async_flag = False
    dev.open_device()
    #dev.master_cmd_send_dmr_bin(4992*192,192,"dmr_bin/936.bin")
    # test_dmr_bin(dev)
    #dev.cmd_d0_spi_16bit_write(0xffee,0xaa)

    #dev.cmd_d0_interface_cfg(2,0)
    #dev.cmd_d0_write_data([0x2C, 0x0f, 0xf0, 0x0f, 0xf0, 0x0f, 0xf0, 0x0f, 0xf0, 0x0f, 0xf0],1,1)
    # SSD_SEND---------------------------------------------
    
    # idm_code = [0x4C, 0x70, 0xb8, 0x5c, 0x2e, 0x17, 0x0b, 0x05, 0x02, 0x81, 0xc0, 0x60, 0x30, 0x98, 0x4c,
    # 0x26, 0x13, 0x09, 0x84, 0x42, 0xa1, 0xd0, 0xe8, 0x74, 0x3a, 0x9d, 0x4e, 0xa7, 0x53, 0x29, 0x14,
    # 0x0a, 0x05, 0x02, 0x81, 0x40, 0xa0, 0xd0, 0xe8, 0xf4, 0xfa, 0x7d, 0x3e, 0x9f, 0x4f, 0xa7, 0x53, 0x29,
    # 0x14, 0x0a, 0x05, 0x82, 0xc1, 0xe0, 0xf0, 0xf8, 0xfc, 0xfe, 0xff, 0x7f, 0x3f, 0x9f, 0xcf, 0xe7, 0x73]
    # dev.cmd_d0_prepare_write_data(idm_code)
    # dev.cmd_d0_write_prepare_data(len(idm_code),1,1)

    # for i in range(256):
    #     #dev.meter_cmd_update_bin(0)
    #     dev.cmd_d0_program_flash(1,0,[0xff])
    #     dev.cmd_d0_program_flash(2, 0, [0xff])
    #     dev.cmd_d0_program_flash(3, 0, [0xff])
    #     dev.cmd_d0_program_flash(4, 0, [0xff])
    #     dev.cmd_d0_program_flash(5, 0, [0xff])
    #     dev.cmd_d0_program_flash(0, 0, [0xff])
    # #dev.meter_get_single_power_voltage(6, 1, 0, 1)
    # dev.meter_cmd_fast_read_vol(0,0)
    # # list_color_name = ["w", "r", "g", "b"]
    # list_color = [[255, 255, 255], [255, 0, 0], [0, 255, 0], [0, 0, 255]]
    # dev.send_gamma_image(0x00, 0x00, 0x00)
    # time.sleep(2)
    # for i in range(200):
    #     num = int(i % 4)
    #     print(i, num, list_color_name[num])
    #     dev.send_gamma_image(list_color[num][0], list_color[num][1], list_color[num][2])
    #     # time.sleep(0.1)
    # dev.send_gamma_image(0xff, 0xff, 0xff)
    # dev.master_cmd_set_algo_img_name(0,"01_1.bmp")
    # dev.master_cmd_show_algo_img_enable()
    # dev.master_cmd_send_algo_img(3)
    dev.cmd_30_ssd_send(0x01, [0x2C, 0x0f, 0xf0])
    dev.cmd_31_ssd_read(1,0x11,11)
    dev.meter_cmd_get_freq()
    for i in range(64):
        dev.meter_cmd_get_single_voltage(1, i,1)
        dev.meter_cmd_get_single_voltage(0, 6, 0)
    for i in range(14, 21, 1):
        vol = dev.meter_cmd_get_single_voltage(1, i, 1)
        dev.meter_cmd_set_freq_voltage(1, i, vol / 2)
        dev.meter_cmd_get_freq()
    dev.meter_cmd_get_freq()
    dev.meter_cmd_get_freq()
    dev.meter_cmd_get_freq()    # dev.meter_cmd_set_freq_voltage(1, 24, 1800)
    dev.meter_cmd_get_freq()
    dev.meter_cmd_set_bias_vol(0,0,4000)
    dev.meter_cmd_set_freq_voltage(40,1500)
    dev.meter_cmd_get_freq()
    i = dev.meter_cmd_get_single_power_current(0, 1)
    i = dev.meter_cmd_get_single_power_current(1, 1)
    i = dev.meter_cmd_get_single_power_current(3, 1)
    dev.meter_cmd_set_cali_arg(4,6,0.34140012,206.51997208,0)
    dev.meter_cmd_set_cali_arg(3,6,0.72752053,256.67110398,0)
    #dev.meter_cmd_set_cali_arg(5,1, 1.00494696,-0.15044497, 0)
    dev.meter_cmd_update_cali_arg(1)
    dev.meter_cmd_active_cali_arg(0x8f)

    dev.meter_cmd_set_cali_arg(3, 0, 1.0442649305458138,10.707689512425743, 0)
    dev.meter_cmd_set_cali_arg(3, 1, 1.0524281371661035, -20.87263596576027, 0)
    dev.meter_cmd_set_cali_arg(3, 2, 1.062575422972273, -20.5307044592104, 0)
    dev.meter_cmd_set_cali_arg(3, 3, 1.0703480166035662, -5.013076064325444, 0)
    dev.meter_cmd_set_cali_arg(3, 4, 1.06119, -23.40546, 0)
    dev.meter_cmd_set_cali_arg(3, 5, 1, 0, 0)
    
    dev.meter_cmd_update_cali_arg(1)
    dev.meter_cmd_active_cali_arg(0x8e)
    dev.meter_cmd_update_cali_arg(1)
    dev.meter_cmd_get_single_power_current(0, 1)
    dev.get_dev_id()
    dio = dev.meter_cmd_get_single_r_d(0,24,27,1000,0)
    print(dio)
    dev.meter_cmd_set_bias_vol(0,0,1500)
    dev.set_single_power_vol("vsn",6000)
    dev.set_single_power_vol("vsp", 6000)
    dev.meter_cmd_get_single_power_current(0, 1)
    dev.meter_cmd_get_single_power_current(1, 1)
    dev.meter_cmd_get_single_power_current(3, 1)
    vsn = dev.meter_cmd_get_single_power_voltage(0,1)
    vsp = dev.meter_cmd_get_single_power_voltage(1, 1)
    iovcc = dev.meter_cmd_get_single_power_voltage(3, 1)
    
    dev.close_device()
