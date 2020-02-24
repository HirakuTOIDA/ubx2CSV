# -*- coding: utf-8 -*-
import os
import sys
import math
import numpy as np
import pandas as pd
import ublox

if __name__ == "__main__":
    argvs = sys.argv
    argc = len(argvs)

    if argc != 2:
        print ("Usage: # python {0} filename'".format(argvs[0]))
    filename = argvs[1]
    name, ext = os.path.splitext(filename)
    dirname = os.path.dirname(filename)
    os.chdir(dirname)

    df = pd.read_csv(filename)
    dat = df.to_numpy()
    dat_length = dat.shape[0]
    dat_width = dat.shape[1]

    rxm_rawx = ublox.ubx_messages_8[0x0215]
    fix_length = len(rxm_rawx[5])
    var_length = len(rxm_rawx[7])
    number_var = int((dat_width - fix_length) / var_length)
    gnss_sv_ids = []
    for i in range(dat_length):
        for j in range(number_var):
            gnssid_svid = [dat[i,11 + j * var_length], dat[i,12 + j * var_length]]
            if not (math.isnan(gnssid_svid[0])):
                if not gnssid_svid in gnss_sv_ids:
                    gnss_sv_ids.append(gnssid_svid)

    gnss_sv_ids.sort()

    dat_shaped = np.zeros([dat_length, fix_length + var_length * len(gnss_sv_ids)])
    dat_shaped[:, :] = np.nan
    dat_shaped[:, :fix_length] = dat[:, :fix_length]

    for i in range(dat_length):
        for j in range(number_var):
            for k, gnss_sv_id in enumerate(gnss_sv_ids):
                if [dat[i, 11 + j * var_length], dat[i, 12 + j * var_length]] == gnss_sv_id:
                    dat_shaped[i, fix_length + k * var_length:fix_length + var_length + k * var_length] = dat[i, fix_length + j * var_length:fix_length + var_length + j * var_length]
    df = pd.DataFrame(dat_shaped)
    header = rxm_rawx[6]
    if number_var != 0:
        header += rxm_rawx[8] * len(gnss_sv_ids)
    header[0] = "# " + header[0]
    df.columns = header
    df.to_csv(name + "_shaped" + ext, index=False)
