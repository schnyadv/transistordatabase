from matplotlib import pyplot as plt
import numpy as np
from math import floor
from scipy.interpolate import interpn
import transistordatabase as tdb

tdb.print_tdb()

transistor1 = tdb.load("Fuji_2MBI200XBE120-50")
transistor2 = tdb.load("Fuji_2MBI200XBE120-50")
transistor3 = tdb.load("Fuji_2MBI300XBE120-50")

transistor_list = [transistor1, transistor2, transistor3]
t_j_list = [25, 25, 25]
v_g_on_list = [15, 15, 15]
v_supply_list = [15, 15, 15]

for m in range(1):

    dict = transistor_list[m].switch.convert_to_dict()

    channel = []
    for curve in dict["channel"]:
        if curve["v_g"] == v_g_on_list[m]:
            channel.append(curve)

    print(channel)

    t_j_available = []
    for curve in channel:
        if curve["t_j"] not in t_j_available:
            t_j_available.append(curve["t_j"])
    t_j_available.sort()

    print(t_j_available)


    vec_i = np.linspace(0, transistor_list[m].i_abs_max, 50)

    m_t_j_available, m_i = np.meshgrid(t_j_available, vec_i, indexing='ij')

    m_v = np.zeros_like(m_t_j_available)

    for i in range(len(t_j_available)):
        for j in range(len(vec_i)):
            transistor_list[m].wp.switch_channel = transistor_list[m].get_object_v_i(switch_or_diode="switch",
                                                                                     t_j=m_t_j_available[i, j],
                                                                                     v_g=v_g_on_list[m])

            m_v[i, j] = np.interp(m_i[i, j], transistor_list[m].wp.switch_channel.graph_v_i[1], transistor_list[m].wp.switch_channel.graph_v_i[0]*1000000)



    points = (t_j_available, vec_i)
    values = m_v

    vec_v = np.zeros_like(vec_i)

    for n in range(len(vec_i)):
        point = ([t_j_list[m], vec_i[n]])
        vec_v[n] = interpn(points, values, point, bounds_error=False, fill_value=None) / 1000000

    if t_j_list[m] < min(t_j_available) or t_j_list[m] > max(t_j_available):
        label = f"{transistor_list[m].name} (data extrapolated)"
    else:
        label = f"{transistor_list[m].name} (data interpolated)"

    plt.plot(vec_v, vec_i, label=label)
    plt.show()







