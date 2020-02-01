import cyppy
import numpy as np


def test_h2ophys_init():
    cyppy.lib.h2ophys_init()


def test_sfc_ocean_init():
    cyppy.lib.sfc_ocean_init()


def test_sfc_ocean_run():
    im = np.array(5)
    cp = np.array(1005.)
    rd = np.array(287.04)
    eps = np.array(rd / 461.50)
    epsm1 = np.array(eps - 1.0)
    hvap = np.array(2.501e6)
    rvrdm1 = np.array(1.0 / eps - 1.0)
    ps = np.array(1.0e5) * np.ones([im])
    t1 = np.array(300.0) * np.ones([im])
    q1 = np.array(1.0e-3) * np.ones([im])
    tskin = np.array(290.0) * np.ones([im])
    cm = np.array(0.004) * np.ones([im])
    ch = np.array(0.004) * np.ones([im])
    prsl1 = np.array(0.95e5) * np.ones([im])
    prslki = np.array(1.05) * np.ones([im])
    wet = np.ones([im], dtype=bool)
    wind = np.ones([im])
    flag_iter = np.ones([im], dtype=bool)

    qsurf = np.zeros([im])
    cmm = np.zeros([im])
    chh = np.zeros([im])
    gflux = np.zeros([im])
    evap = np.zeros([im])
    hflx = np.zeros([im])
    ep = np.zeros([im])

    cyppy.lib.sfc_ocean_run(
        im, cp, rd, eps, epsm1, hvap, rvrdm1, ps, t1, q1,
        tskin, cm, ch, prsl1, prslki, wet, wind, flag_iter,
        qsurf, cmm, chh, gflux, evap, hflx, ep
    )
