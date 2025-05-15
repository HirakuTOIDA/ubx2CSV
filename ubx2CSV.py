# -*- coding: utf-8 -*-
"""GUI for csv convertor of ubx files."""

import os
import threading
import tkinter as tk
import tkinter.filedialog
import ublox

class Application(tk.Frame):
    """class for GUI."""

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.master.title('ubx2CSV')

        _pad = [5,5]

        self.version_list = ["6", "7", "8", "9"]
        self.version_list_len = len(self.version_list)

        # ラベル
        self.lb0 = tk.Label(self, text=u'u-blox generation: ')
        self.lb0.grid(row=0, column=0, columnspan=self.version_list_len,
                      padx=_pad[0], pady=_pad[1], sticky=tk.W)

        # ラジオボタン
        self.var = tk.IntVar()
        self.var.set(9)
        self.rbs = [tk.Radiobutton(self, value=6+i, variable=self.var, text=self.version_list[i]) for i in range(self.version_list_len)]
        [self.rbs[i].grid(row=1, column=i, columnspan=1, padx=_pad[0], pady=_pad[1], sticky=tk.W) for i in range(self.version_list_len)]

        # ボタン
        self.bt = tk.Button(self, text=u'Open & Convert',
                            command = self.fileopen)
        self.bt.grid(row=self.version_list_len+1, column=0,
                     columnspan=self.version_list_len,
                     padx=_pad[0], pady=_pad[1], sticky=tk.W+tk.E)

        # ラベル
        self.filename_str = tk.StringVar()
        self.filename_str.set(u"File name: ")
        self.lbfn = tk.Label(self, textvariable=self.filename_str)
        self.lbfn.grid(row=self.version_list_len+2, column=0,
                       columnspan=int(self.version_list_len/2),
                       padx=_pad[0], pady=_pad[1], sticky=tk.W)

        # ラベル
        self.filesize_str = tk.StringVar()
        self.filesize_str.set(u"File size: ")
        self.lbfs = tk.Label(self, textvariable=self.filesize_str)
        self.lbfs.grid(row=self.version_list_len+3, column=0,
                       columnspan=int(self.version_list_len/2),
                       padx=_pad[0], pady=_pad[1], sticky=tk.W)

        # ラベル
        self.status_str = tk.StringVar()
        self.status_str.set(u"Select file.")
        self.lbst = tk.Label(self, textvariable=self.status_str)
        self.lbst.grid(row=self.version_list_len+4, column=0,
                       columnspan=int(self.version_list_len/2),
                       padx=_pad[0], pady=_pad[1], sticky=tk.W)

    def fileopen(self):
        """Open button."""
        fTyp = [("ubx file","*.ubx")]
        filename = tk.filedialog.askopenfilename(filetypes = fTyp)
        dirname = os.path.dirname(filename)
        if filename:
            os.chdir(dirname)
        if len(filename) > 0:
            self.bt.configure(state = tk.DISABLED)
            self.status_str.set(u"File selected.")
            th = threading.Thread(target=self.convert, args=(filename,))
            th.start()

    def convert(self, filename):
        """Convert function called from fileopen."""
        # 世代選択
        ublox_generation = self.var.get()
        # UBXメッセージ一覧を取得
        ubx_messages = getattr(ublox, "ubx_messages_" + str(ublox_generation))

        # UBXインスタンスを格納する辞書
        ubx_instances = {}

        # 各UBXメッセージに対してインスタンス生成
        for msg_key, msg_def in ubx_messages.items():
            ubx_instances[msg_key] = ublox.ublox(msg_def)

        with open(filename, 'rb') as fobj:
            with open("ubx2CSV.log", 'w') as fobjlog:
                self.filename_str.set(u"File name: " + filename)
                filesize = os.path.getsize(filename)
                self.filesize_str.set(u"File size: {0:,} byte".format(filesize))
                self.status_str.set(u"File opened.")
                name, _ = os.path.splitext(filename)

                message_count = 0
                ubx_count = 0
                read_count = 0
                convert_count = 0
                checksum_error_count = 0
                pb_previous = 0

                self.status_str.set(u"Reading file.")
                while True:
                    if message_count == 0: #ヘッダのチェック 1
                        h_data = fobj.read(1) # 1バイトずつ
                        read_count += len(h_data)
                        if len(h_data) < 1:
                            break
                        if h_data == ublox.ubx_sync_char[0].to_bytes(1, 'big'):
                            message_count += 1
                    elif message_count == 1: # ヘッダのチェック 2
                        h_data = fobj.read(1) # 1バイトずつ
                        read_count += len(h_data)
                        if len(h_data) < 1:
                            break
                        if h_data == ublox.ubx_sync_char[1].to_bytes(1, 'big'):
                            ubx_count += 1
                            message_count += 1
                        else:
                            message_count = 0
                    elif message_count == 2: # ヘッダが見つかった場合
                        # class, id, lengthの読み込み
                        h_data = fobj.read(4)
                        read_count += len(h_data)
                        if len(h_data) < 4:
                            break
                        dat = bytearray(h_data)
                        ubx_class_id = int.from_bytes(h_data[:2], 'big')
                        ubx_length = int.from_bytes(h_data[2:], 'little')
                        # length分だけメッセージの読み込み
                        h_data = fobj.read(ubx_length)
                        read_count += len(h_data)
                        if len(h_data) < ubx_length:
                            break
                        dat = dat + bytearray(h_data)
                        ch = ublox.checksum(dat)
                        # checksumの読み込み
                        h_data = fobj.read(2)
                        read_count += len(h_data)
                        if len(h_data) < 2:
                            break
                        pb_current = int(read_count / filesize * 100)
                        if pb_previous < pb_current:
                            self.status_str.set(u"Reading file. {}% done.".format(pb_current))
                            pb_previous = pb_current
                        checksum_data = int.from_bytes(h_data, 'little')
                        if checksum_data != ch:
                            fobjlog.write(f"Checksum error: ubx count={ubx_count:,}, class/id=0x{ubx_class_id:04X}, length={ubx_length:,}, checksum data=0x{checksum_data:04X}, checksum calculated=0x{ch:04X}\n")
                            # @todo 戻る?
                            checksum_error_count += 1
                        else:
                            if ubx_class_id in ubx_messages: # class, idが見つかった場合
                                if len(dat[4:]) == 0:
                                    fobjlog.write(f"No data contained: ubx count={ubx_count:,}, class/id=0x{ubx_class_id:04X}, length={ubx_length:,}\n")
                                else:
                                    ubx_instances[ubx_class_id].append(dat[4:])
                                    convert_count += 1
                            else: # class, idが見つからなかった場合
                                fobjlog.write(f"Message class/id not found: ubx count={ubx_count:,}, class/id=0x{ubx_class_id:04X}, length={ubx_length:,}\n")
                        message_count = 0

                self.status_str.set(u"Writing csv files.")
                print("Saved UBX Messages")
                for ubx_class_id in ubx_messages:
                    try:
                        ubx_instances[ubx_class_id].save_csv(f"{ubx_messages[ubx_class_id][0]}.csv")
                        print(f"0x{ubx_class_id:04X}: Done")
                    except:
                        print(f"0x{ubx_class_id:04X}: Error")

                self.status_str.set(u"Writing log file.")
                fobjlog.write("\nSummary of the conversion\n")
                fobjlog.write(f"Source: {filename}\n")
                fobjlog.write(f"Filesize:  {filesize:,} bytes\n")
                fobjlog.write(f"Read data: {read_count:,} bytes\n")
                fobjlog.write(f"ubx messages found:     {ubx_count:,}\n")
                fobjlog.write(f"ubx messages converted: {convert_count:,}\n")
                fobjlog.write(f"checksum error count: {checksum_error_count:,}\n")

                self.status_str.set(u"Done.")
                self.bt.configure(state = tk.NORMAL)

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
