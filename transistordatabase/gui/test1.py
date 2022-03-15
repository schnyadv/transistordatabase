import transistordatabase as tdb
import matplotlib.pyplot as plt
import buck_converter_functions
import numpy as np

transistor_list = tdb.print_tdb()
tdb.print_tdb()
transistor1 = tdb.load("CREE_C3M0120100J")
transistor2 = tdb.load("Fuji_2MBI100XAA120-50")

"""transistor.wp.switch_channel = transistor.get_object_v_i(switch_or_diode="diode",
                                                         t_j=25,
                                                         v_g=None)

plt.plot(transistor.wp.switch_channel.graph_v_i[0], transistor.wp.switch_channel.graph_v_i[1])
plt.show()"""

"""transistor.wp.e_on = transistor.calc_object_i_e(e_on_off_rr="e_on",
                                                t_j=25,
                                                v_supply=600,
                                                r_g=15,
                                                normalize_t_to_v=10)"""

"""transistor.wp.e_rr = transistor.get_object_i_e(e_on_off_rr="e_rr",
                                               t_j=25,
                                               v_supply=600,
                                               r_g=1.8,
                                               v_g=min([i for i in [e_rr.v_g for e_rr in transistor.diode.e_rr] if i is not None]))



plt.plot(transistor.wp.e_rr.graph_i_e[0], transistor.wp.e_rr.graph_i_e[1])
plt.show()"""



v_channel1, r_channel1 = transistor1.calc_lin_channel(t_j=max([channel.t_j for channel in transistor1.diode.channel]),
                                                                   v_g=0,
                                                                   i_channel=10,
                                                                   switch_or_diode="diode")
print(v_channel1)
print(r_channel1)






