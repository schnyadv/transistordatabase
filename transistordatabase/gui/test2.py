def plot_channel(transistor1, transistor2, transistor3, matplotlibwidget, t_j1, t_j2, t_j3, v_g_on1, v_g_on2, v_g_on3):
    """
    Calculates and plots switch turn-on energy i-e characteristic curves for all three transistors for a chosen
    junction temperature, gate resistor and supply voltage into a MatplotlibWidget

    :param transistor1: transistor object for transistor1
    :param transistor2: transistor object for transistor2
    :param transistor3: transistor object for transistor3
    :param matplotlibwidget: MatplotlibWidget object
    :param t_j1: junction temperature for transistor1
    :param t_j2: junction temperature for transistor2
    :param t_j3: junction temperature for transistor3
    :param v_g_on1: gate voltage for transistor1
    :param v_g_on2: gate voltage for transistor2
    :param v_g_on3: gate voltage for transistor3

    :return: None
    """

    annotations_list = []

    def clicked(event):
        if event.dblclick:
            click_event(event.button, event.xdata, event.ydata, matplotlibwidget, annotations_list)

    transistor_list = [transistor1, transistor2, transistor3]
    t_j_list = [t_j1, t_j2, t_j3]
    v_g_on_list = [v_g_on1, v_g_on2, v_g_on3]
    color_list = ["blue", "green", "red"]

    for m in range(len(transistor_list)):
        try:
            dict = transistor_list[m].switch.convert_to_dict()

            channel_filtered_v_g = []
            for curve in dict["channel"]:
                if curve["v_g"] == v_g_on_list[m]:
                    channel_filtered_v_g.append(curve)

            t_j_available = []
            for curve in channel_filtered_v_g:
                if curve["t_j"] not in t_j_available:
                    t_j_available.append(curve["t_j"])

            if t_j_list[m] in t_j_available:
                for curve in channel_filtered_v_g:
                    if curve["t_j"] == t_j_list[m]:
                        graph_v_i = curve["graph_v_i"]

                        label = transistor_list[m].name
                        matplotlibwidget.axis.plot(graph_v_i[0], graph_v_i[1], color=color_list[m], label=label)
            else:
                if len(channel_filtered_v_g) == 1:
                    graph_v_i = channel_filtered_v_g[0]["graph_v_i"]

                    t_j = channel_filtered_v_g[0]["t_j"]
                    label = f"{transistor_list[m].name}, T_j = {t_j}°C"
                    matplotlibwidget.axis.plot(graph_v_i[0], graph_v_i[1], color=color_list[m], label=label)

                elif len(channel_filtered_v_g) > 1:
                    for curve in channel_filtered_v_g:
                        if curve["t_j"] == max(t_j_available):
                            graph_v_i_max = curve["graph_v_i"]
                        elif curve["t_j"] == min(t_j_available):
                            graph_v_i_min = curve["graph_v_i"]

                    vec_v_min = np.copy(graph_v_i_min[0])
                    vec_v_max = np.copy(graph_v_i_max[0])

                    vec_i_min = np.copy(graph_v_i_min[1])
                    vec_i_max = np.copy(graph_v_i_max[1])

                    mean_max = sum(vec_i_max) / len(vec_i_max)
                    mean_min = sum(vec_i_min) / len(vec_i_min)

                    mean_diff = (mean_max - mean_min) / mean_max
                    temp_diff_max_min = max(t_j_available) - min(t_j_available)

                    if t_j_list[m] < min(t_j_available):
                        temp_diff = min(t_j_available) - t_j_list[m]
                        vec_i = vec_i_min * (1 + mean_diff * temp_diff / temp_diff_max_min)
                        graph_v_i = [vec_v_min, vec_i]

                    elif t_j_list[m] > min(t_j_available) and t_j_list[m] < max(t_j_available):
                        temp_diff = t_j_list[m] - min(t_j_available)
                        vec_i = vec_i_min * (1 - mean_diff * temp_diff / temp_diff_max_min)
                        graph_v_i = [vec_v_min, vec_i]

                    elif t_j_list[m] > max(t_j_available):
                        temp_diff = t_j_list[m] - max(t_j_available)
                        if mean_diff * temp_diff / temp_diff_max_min < 1:
                            vec_i = vec_i_max * (1 - mean_diff * temp_diff / temp_diff_max_min)
                        else:
                            vec_i = np.zeros_like(vec_i_min)
                        graph_v_i = [vec_v_max, vec_i]


                    label = f"{transistor_list[m].name} (data estimated)"
                    matplotlibwidget.axis.plot(graph_v_i[0], graph_v_i[1], color=color_list[m], label=label)

        except:
            MainWindow.show_popup_message(MainWindow,
                                          f"Switch channel v_i curve is not available for <b>{transistor_list[m].name}</b>!")

        try:
            matplotlibwidget.axis.legend(fontsize=5)
            matplotlibwidget.axis.set(xlabel="Voltage in V",
                                      ylabel="Current in A")
            matplotlibwidget.axis.set_position([0.12, 0.2, 0.9, 0.7])
            matplotlibwidget.axis.grid()
            matplotlibwidget.figure.canvas.draw_idle()

            matplotlibwidget.cursor = Cursor(matplotlibwidget.axis, horizOn=True, vertOn=True, useblit=True,
                                             color="Green", linewidth=1)
            matplotlibwidget.figure.canvas.mpl_connect("button_press_event", clicked)
        except:
            pass















def plot_e_on_t_j_r_g(transistor1, transistor2, transistor3, matplotlibwidget, t_j1, t_j2, t_j3, r_g_on1, r_g_on2, r_g_on3, v_supply1, v_supply2, v_supply3):
    """
    Calculates and plots switch turn-on energy i-e characteristic curves for all three transistors for a chosen
    junction temperature, gate resistor and supply voltage into a MatplotlibWidget

    :param transistor1: transistor object for transistor1
    :param transistor2: transistor object for transistor2
    :param transistor3: transistor object for transistor3
    :param matplotlibwidget: MatplotlibWidget object
    :param t_j1: junction temperature for transistor1
    :param t_j2: junction temperature for transistor2
    :param t_j3: junction temperature for transistor3
    :param r_g_on1: gate resistor for transistor1
    :param r_g_on2: gate resistor for transistor2
    :param r_g_on3: gate resistor for transistor3
    :param v_supply1: supply voltage for transistor1
    :param v_supply2: supply voltage for transistor2
    :param v_supply3: supply voltage for transistor3

    :return: None
    """

    annotations_list = []
    def clicked(event):
        if event.dblclick:
            click_event(event.button, event.xdata, event.ydata, matplotlibwidget, annotations_list)


    transistor_list = [transistor1, transistor2, transistor3]
    t_j_list = [t_j1, t_j2, t_j3]
    r_g_on_list = [r_g_on1, r_g_on2, r_g_on3]
    v_supply_list = [v_supply1, v_supply2, v_supply3]

    color_list = ["blue", "green", "red"]

    for m in range(len(transistor_list)):
        try:
            t_j_available_unfiltered = [i for i in [e_on.t_j for e_on in transistor_list[m].switch.e_on]]
            t_j_available_unfiltered = np.sort(t_j_available_unfiltered)
            t_j_available = []
            for i in t_j_available_unfiltered:
                if i not in t_j_available:
                    t_j_available.append(i)

            v_supply_chosen = max([i for i in [e_on.v_supply for e_on in transistor_list[m].switch.e_on]])


            if len(t_j_available) == 1:
                try:
                    transistor_list[m].wp.e_on = transistor_list[m].calc_object_i_e(e_on_off_rr="e_on",
                                                                                    t_j=t_j_available[0],
                                                                                    v_supply=v_supply_chosen,
                                                                                    r_g=r_g_on_list[m],
                                                                                    normalize_t_to_v=10)
                    vec_e_on = transistor_list[m].wp.e_on.graph_i_e[1] * v_supply_list[m] / v_supply_chosen
                except:
                    transistor_list[m].wp.e_on = transistor_list[m].get_object_i_e(e_on_off_rr="e_on",
                                                                   t_j=t_j_available[0],
                                                                   v_supply=v_supply_chosen,
                                                                   r_g=r_g_on_list[m],
                                                                   v_g=max([i for i in [e_on.v_g for e_on in transistor_list[m].switch.e_on] if i is not None]))
                    vec_e_on = transistor_list[m].wp.e_on.graph_i_e[1] * v_supply_list[m] / v_supply_chosen

                MainWindow.show_popup_message(MainWindow,
                                              f"Switch energy i_e curve for <b>{transistor_list[m].name}</b> only available for T_j = {t_j_available[0]}°C due to missing data!")
                matplotlibwidget.axis.plot(transistor_list[m].wp.e_on.graph_i_e[0], vec_e_on, color=color_list[m],
                                           label=f"{transistor_list[m].name}, T_j = {t_j_available[0]}°C")

            else:
                r_g_on_max_list = np.zeros_like(t_j_available)

                for i in range(len(t_j_available)):
                    r_e_object_on1 = transistor_list[m].get_object_r_e_simplified(e_on_off_rr="e_on",
                                                                                  t_j=t_j_available[i],
                                                                                  v_g=max([i for i in
                                                                                           [e_on.v_g for e_on in
                                                                                            transistor_list[
                                                                                                m].switch.e_on]
                                                                                           if
                                                                                           i != None]),
                                                                                  v_supply=max(
                                                                                      [i for i in
                                                                                       [e_on.v_supply for e_on in
                                                                                        transistor_list[
                                                                                            m].switch.e_on] if
                                                                                       i != None]),
                                                                                  normalize_t_to_v=10)
                    r_g_on_max_list[i] = np.amax(r_e_object_on1.graph_r_e[0]) * 10000

                r_g_on_max = floor(10 * min(r_g_on_max_list) / 10000) / 10

                r_g_on_available = np.linspace(0, r_g_on_max, 10)

                vec_i = np.linspace(0, transistor_list[m].i_abs_max, 10)


                m_t_j_available, m_r_g_on_available, m_i = np.meshgrid(t_j_available, r_g_on_available, vec_i,
                                                                       indexing='ij')

                m_e_on = np.zeros_like(m_t_j_available)

                for i in range(len(t_j_available)):
                    for j in range(len(r_g_on_available)):
                        for k in range(len(vec_i)):
                            transistor_list[m].wp.e_on = transistor_list[m].calc_object_i_e(e_on_off_rr="e_on",
                                                                                            t_j=m_t_j_available[
                                                                                                i, j, k],
                                                                                            v_supply=v_supply_chosen,
                                                                                            r_g=m_r_g_on_available[
                                                                                                i, j, k],
                                                                                            normalize_t_to_v=10)
                            m_e_on[i, j, k] = np.interp(m_i[i, j, k], transistor_list[m].wp.e_on.graph_i_e[0],
                                                        transistor_list[m].wp.e_on.graph_i_e[1]) * v_supply_list[
                                                  m] / v_supply_chosen * 1000000000

                points = (t_j_available, r_g_on_available, vec_i)
                values = m_e_on

                if t_j_list[m] >= min(t_j_available) and t_j_list[m] <= max(t_j_available):
                    vec_e_on = np.zeros_like(vec_i)
                    for n in range(len(vec_i)):
                        point = ([t_j_list[m], r_g_on_list[m], vec_i[n]])
                        vec_e_on[n] = interpn(points, values, point) / 1000000000
                    label = f"{transistor_list[m].name}"
                else:
                    vec_e_on_min = np.zeros_like(vec_i)
                    vec_e_on_max = np.zeros_like(vec_i)
                    for n in range(len(vec_i)):
                        point = ([min(t_j_available), r_g_on_list[m], vec_i[n]])
                        vec_e_on_min[n] = interpn(points, values, point) / 1000000000
                        point = ([max(t_j_available), r_g_on_list[m], vec_i[n]])
                        vec_e_on_max[n] = interpn(points, values, point) / 1000000000

                    # self written estimation in case of selected t_j is out of bounds to interpolate via interpn-function
                    mean_max = sum(vec_e_on_max) / len(vec_e_on_max)
                    mean_min = sum(vec_e_on_min) / len(vec_e_on_min)

                    mean_diff = (mean_max-mean_min)/mean_max
                    temp_diff_max_min = max(t_j_available) - min(t_j_available)

                    if t_j_list[m] < min(t_j_available):
                        temp_diff = min(t_j_available) - t_j_list[m]
                        if mean_diff*temp_diff/temp_diff_max_min < 1:
                            vec_e_on = vec_e_on_min * (1 - mean_diff * temp_diff / temp_diff_max_min)
                        else:
                            vec_e_on = np.zeros_like(vec_e_on_min)


                    elif t_j_list[m] > max(t_j_available):
                        temp_diff = t_j_list[m] - max(t_j_available)
                        vec_e_on = vec_e_on_max * (1+mean_diff*temp_diff/temp_diff_max_min)

                    label = f"{transistor_list[m].name} (data estimated)"

                matplotlibwidget.axis.plot(vec_i, vec_e_on, color=color_list[m], label=label)


        except:
            MainWindow.show_popup_message(MainWindow, f"Switch energy i_e curve is not available for <b>{transistor_list[m].name}</b>!")

        try:
            matplotlibwidget.axis.legend(fontsize=5)
            matplotlibwidget.axis.set(xlabel="Current in A",
                                      ylabel="Loss energy in J")
            matplotlibwidget.axis.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
            matplotlibwidget.axis.set_position([0.12, 0.2, 0.9, 0.7])
            matplotlibwidget.axis.grid()
            matplotlibwidget.figure.canvas.draw_idle()

            matplotlibwidget.cursor = Cursor(matplotlibwidget.axis, horizOn=True, vertOn=True, useblit=True,
                                             color="Green", linewidth=1)
            matplotlibwidget.figure.canvas.mpl_connect("button_press_event", clicked)
        except:
            pass




def plot_e_off_t_j_r_g(transistor1, transistor2, transistor3, matplotlibwidget, t_j1, t_j2, t_j3, r_g_off1, r_g_off2, r_g_off3, v_supply1, v_supply2, v_supply3):
    """
    Calculates and plots switch turn-on energy i-e characteristic curves for all three transistors for a chosen
    junction temperature, gate resistor and supply voltage into a MatplotlibWidget

    :param transistor1: transistor object for transistor1
    :param transistor2: transistor object for transistor2
    :param transistor3: transistor object for transistor3
    :param matplotlibwidget: MatplotlibWidget object
    :param t_j1: junction temperature for transistor1
    :param t_j2: junction temperature for transistor2
    :param t_j3: junction temperature for transistor3
    :param r_g_off1: gate resistor for transistor1
    :param r_g_off2: gate resistor for transistor2
    :param r_g_off3: gate resistor for transistor3
    :param v_supply1: supply voltage for transistor1
    :param v_supply2: supply voltage for transistor2
    :param v_supply3: supply voltage for transistor3

    :return: None
    """

    annotations_list = []
    def clicked(event):
        if event.dblclick:
            click_event(event.button, event.xdata, event.ydata, matplotlibwidget, annotations_list)


    transistor_list = [transistor1, transistor2, transistor3]
    t_j_list = [t_j1, t_j2, t_j3]
    r_g_off_list = [r_g_off1, r_g_off2, r_g_off3]
    v_supply_list = [v_supply1, v_supply2, v_supply3]

    color_list = ["blue", "green", "red"]

    for m in range(len(transistor_list)):
        try:
            t_j_available_unfiltered = [i for i in [e_off.t_j for e_off in transistor_list[m].switch.e_off]]
            t_j_available_unfiltered = np.sort(t_j_available_unfiltered)
            t_j_available = []
            for i in t_j_available_unfiltered:
                if i not in t_j_available:
                    t_j_available.append(i)

            v_supply_chosen = max([i for i in [e_off.v_supply for e_off in transistor_list[m].switch.e_off]])


            if len(t_j_available) == 1:
                try:
                    transistor_list[m].wp.e_off = transistor_list[m].calc_object_i_e(e_on_off_rr="e_off",
                                                                                     t_j=t_j_available[0],
                                                                                     v_supply=v_supply_chosen,
                                                                                     r_g=r_g_off_list[m],
                                                                                     normalize_t_to_v=10)
                    vec_e_off = transistor_list[m].wp.e_off.graph_i_e[1] * v_supply_list[m] / v_supply_chosen
                except:
                    transistor_list[m].wp.e_off = transistor_list[m].get_object_i_e(e_on_off_rr="e_off",
                                                                                   t_j=t_j_available[0],
                                                                                   v_supply=v_supply_chosen,
                                                                                   r_g=r_g_off_list[m],
                                                                                   v_g=min([i for i in [e_off.v_g for e_off in transistor_list[m].switch.e_off] if i is not None]))
                    vec_e_off = transistor_list[m].wp.e_off.graph_i_e[1] * v_supply_list[m] / v_supply_chosen

                MainWindow.show_popup_message(MainWindow, f"Switch energy i_e curve for <b>{transistor_list[m].name}</b> only available for T_j = {t_j_available[0]}°C due to missing data!")
                matplotlibwidget.axis.plot(transistor_list[m].wp.e_off.graph_i_e[0], vec_e_off, color=color_list[m],
                                           label=f"{transistor_list[m].name}, T_j = {t_j_available[0]}°C")

            else:
                r_g_off_max_list = np.zeros_like(t_j_available)

                for i in range(len(t_j_available)):
                    r_e_object_off1 = transistor_list[m].get_object_r_e_simplified(e_on_off_rr="e_off",
                                                                                  t_j=t_j_available[i],
                                                                                  v_g=max([i for i in
                                                                                           [e_off.v_g for e_off in
                                                                                            transistor_list[
                                                                                                m].switch.e_off]
                                                                                           if
                                                                                           i != None]),
                                                                                  v_supply=max(
                                                                                      [i for i in
                                                                                       [e_off.v_supply for e_off in
                                                                                        transistor_list[
                                                                                            m].switch.e_off] if
                                                                                       i != None]),
                                                                                  normalize_t_to_v=10)
                    r_g_off_max_list[i] = np.amax(r_e_object_off1.graph_r_e[0]) * 10000

                r_g_off_max = floor(10 * min(r_g_off_max_list) / 10000) / 10

                r_g_off_available = np.linspace(0, r_g_off_max, 10)

                vec_i = np.linspace(0, transistor_list[m].i_abs_max, 10)


                m_t_j_available, m_r_g_off_available, m_i = np.meshgrid(t_j_available, r_g_off_available, vec_i,
                                                                       indexing='ij')

                m_e_off = np.zeros_like(m_t_j_available)

                for i in range(len(t_j_available)):
                    for j in range(len(r_g_off_available)):
                        for k in range(len(vec_i)):
                            transistor_list[m].wp.e_off = transistor_list[m].calc_object_i_e(e_on_off_rr="e_off",
                                                                                            t_j=m_t_j_available[
                                                                                                i, j, k],
                                                                                            v_supply=v_supply_chosen,
                                                                                            r_g=m_r_g_off_available[
                                                                                                i, j, k],
                                                                                            normalize_t_to_v=10)
                            m_e_off[i, j, k] = np.interp(m_i[i, j, k], transistor_list[m].wp.e_off.graph_i_e[0],
                                                        transistor_list[m].wp.e_off.graph_i_e[1]) * v_supply_list[
                                                  m] / v_supply_chosen * 1000000000

                points = (t_j_available, r_g_off_available, vec_i)
                values = m_e_off

                if t_j_list[m] >= min(t_j_available) and t_j_list[m] <= max(t_j_available):
                    vec_e_off = np.zeros_like(vec_i)
                    for n in range(len(vec_i)):
                        point = ([t_j_list[m], r_g_off_list[m], vec_i[n]])
                        vec_e_off[n] = interpn(points, values, point) / 1000000000
                    label = f"{transistor_list[m].name}"
                else:
                    vec_e_off_min = np.zeros_like(vec_i)
                    vec_e_off_max = np.zeros_like(vec_i)
                    for n in range(len(vec_i)):
                        point = ([min(t_j_available), r_g_off_list[m], vec_i[n]])
                        vec_e_off_min[n] = interpn(points, values, point) / 1000000000
                        point = ([max(t_j_available), r_g_off_list[m], vec_i[n]])
                        vec_e_off_max[n] = interpn(points, values, point) / 1000000000

                    # self written estimation in case of selected t_j is out of bounds to interpolate via interpn-function
                    mean_max = sum(vec_e_off_max) / len(vec_e_off_max)
                    mean_min = sum(vec_e_off_min) / len(vec_e_off_min)

                    mean_diff = (mean_max-mean_min)/mean_max
                    temp_diff_max_min = max(t_j_available) - min(t_j_available)

                    if t_j_list[m] < min(t_j_available):
                        temp_diff = min(t_j_available) - t_j_list[m]
                        if mean_diff*temp_diff/temp_diff_max_min < 1:
                            vec_e_off = vec_e_off_min * (1 - mean_diff * temp_diff / temp_diff_max_min)
                        else:
                            vec_e_off = np.zeros_like(vec_e_off_min)


                    elif t_j_list[m] > max(t_j_available):
                        temp_diff = t_j_list[m] - max(t_j_available)
                        vec_e_off = vec_e_off_max * (1+mean_diff*temp_diff/temp_diff_max_min)


                    label = f"{transistor_list[m].name} (data estimated)"

                matplotlibwidget.axis.plot(vec_i, vec_e_off, color=color_list[m], label=label)

        except:
            MainWindow.show_popup_message(MainWindow, f"Switch energy i_e curve is not available for <b>{transistor_list[m].name}</b>!")

        try:
            matplotlibwidget.axis.legend(fontsize=5)
            matplotlibwidget.axis.set(xlabel="Current in A",
                                      ylabel="Loss energy in J")
            matplotlibwidget.axis.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
            matplotlibwidget.axis.set_position([0.12, 0.2, 0.9, 0.7])
            matplotlibwidget.axis.grid()
            matplotlibwidget.figure.canvas.draw_idle()

            matplotlibwidget.cursor = Cursor(matplotlibwidget.axis, horizOn=True, vertOn=True, useblit=True,
                                             color="Green", linewidth=1)
            matplotlibwidget.figure.canvas.mpl_connect("button_press_event", clicked)
        except:
            pass



def plot_e_rr_t_j_r_g(transistor1, transistor2, transistor3, matplotlibwidget, t_j1, t_j2, t_j3, r_g_off1, r_g_off2, r_g_off3, v_supply1, v_supply2, v_supply3):
    """
    Calculates and plots switch turn-on energy i-e characteristic curves for all three transistors for a chosen
    junction temperature, gate resistor and supply voltage into a MatplotlibWidget

    :param transistor1: transistor object for transistor1
    :param transistor2: transistor object for transistor2
    :param transistor3: transistor object for transistor3
    :param matplotlibwidget: MatplotlibWidget object
    :param t_j1: junction temperature for transistor1
    :param t_j2: junction temperature for transistor2
    :param t_j3: junction temperature for transistor3
    :param r_g_off1: gate resistor for transistor1
    :param r_g_off2: gate resistor for transistor2
    :param r_g_off3: gate resistor for transistor3
    :param v_supply1: supply voltage for transistor1
    :param v_supply2: supply voltage for transistor2
    :param v_supply3: supply voltage for transistor3

    :return: None
    """

    annotations_list = []
    def clicked(event):
        if event.dblclick:
            click_event(event.button, event.xdata, event.ydata, matplotlibwidget, annotations_list)


    transistor_list = [transistor1, transistor2, transistor3]
    t_j_list = [t_j1, t_j2, t_j3]
    r_g_off_list = [r_g_off1, r_g_off2, r_g_off3]
    v_supply_list = [v_supply1, v_supply2, v_supply3]

    color_list = ["blue", "green", "red"]

    for m in range(len(transistor_list)):
        try:
            t_j_available_unfiltered = [i for i in [e_rr.t_j for e_rr in transistor_list[m].diode.e_rr]]
            t_j_available_unfiltered = np.sort(t_j_available_unfiltered)
            t_j_available = []
            for i in t_j_available_unfiltered:
                if i not in t_j_available:
                    t_j_available.append(i)

            v_supply_chosen = max([i for i in [e_rr.v_supply for e_rr in transistor_list[m].diode.e_rr]])


            if len(t_j_available) == 1:
                try:
                    transistor_list[m].wp.e_rr = transistor_list[m].calc_object_i_e(e_on_off_rr="e_rr",
                                                                                    t_j=t_j_available[0],
                                                                                    v_supply=v_supply_chosen,
                                                                                    r_g=r_g_off_list[m],
                                                                                    normalize_t_to_v=10)
                    vec_e_rr = transistor_list[m].wp.e_rr.graph_i_e[1] * v_supply_list[m] / v_supply_chosen
                except:
                    transistor_list[m].wp.e_rr = transistor_list[m].get_object_i_e(e_on_off_rr="e_rr",
                                                                                    t_j=t_j_available[0],
                                                                                    v_supply=v_supply_chosen,
                                                                                    r_g=r_g_off_list[m],
                                                                                    v_g=min([i for i in [e_rr.v_g for e_rr in transistor_list[m].diode.e_rr] if i is not None]))
                    vec_e_rr = transistor_list[m].wp.e_rr.graph_i_e[1] * v_supply_list[m] / v_supply_chosen

                MainWindow.show_popup_message(MainWindow, f"Diode energy i_e curve for <b>{transistor_list[m].name}</b> only available for T_j = {t_j_available[0]}°C due to missing data!")
                matplotlibwidget.axis.plot(transistor_list[m].wp.e_rr.graph_i_e[0], vec_e_rr, color=color_list[m],
                                           label=f"{transistor_list[m].name}, T_j = {t_j_available[0]}°C")

            else:
                r_g_rr_max_list = np.zeros_like(t_j_available)

                for i in range(len(t_j_available)):
                    r_e_object_rr1 = transistor_list[m].get_object_r_e_simplified(e_on_off_rr="e_rr",
                                                                                  t_j=t_j_available[i],
                                                                                  v_g=max([i for i in
                                                                                           [e_rr.v_g for e_rr in
                                                                                            transistor_list[
                                                                                                m].diode.e_rr]
                                                                                           if
                                                                                           i != None]),
                                                                                  v_supply=max(
                                                                                      [i for i in
                                                                                       [e_rr.v_supply for e_rr in
                                                                                        transistor_list[
                                                                                            m].diode.e_rr] if
                                                                                       i != None]),
                                                                                  normalize_t_to_v=10)
                    r_g_rr_max_list[i] = np.amax(r_e_object_rr1.graph_r_e[0]) * 10000

                r_g_rr_max = floor(10 * min(r_g_rr_max_list) / 10000) / 10

                r_g_rr_available = np.linspace(0, r_g_rr_max, 10)

                vec_i = np.linspace(0, transistor_list[m].i_abs_max, 10)


                m_t_j_available, m_r_g_rr_available, m_i = np.meshgrid(t_j_available, r_g_rr_available, vec_i,
                                                                       indexing='ij')

                m_e_rr = np.zeros_like(m_t_j_available)

                for i in range(len(t_j_available)):
                    for j in range(len(r_g_rr_available)):
                        for k in range(len(vec_i)):
                            transistor_list[m].wp.e_rr = transistor_list[m].calc_object_i_e(e_on_off_rr="e_rr",
                                                                                            t_j=m_t_j_available[
                                                                                                i, j, k],
                                                                                            v_supply=v_supply_chosen,
                                                                                            r_g=m_r_g_rr_available[
                                                                                                i, j, k],
                                                                                            normalize_t_to_v=10)
                            m_e_rr[i, j, k] = np.interp(m_i[i, j, k], transistor_list[m].wp.e_rr.graph_i_e[0],
                                                        transistor_list[m].wp.e_rr.graph_i_e[1]) * v_supply_list[
                                                  m] / v_supply_chosen * 1000000000

                points = (t_j_available, r_g_rr_available, vec_i)
                values = m_e_rr

                if t_j_list[m] >= min(t_j_available) and t_j_list[m] <= max(t_j_available):
                    vec_e_rr = np.zeros_like(vec_i)
                    for n in range(len(vec_i)):
                        point = ([t_j_list[m], r_g_off_list[m], vec_i[n]])
                        vec_e_rr[n] = interpn(points, values, point) / 1000000000
                    label = f"{transistor_list[m].name}"
                else:
                    vec_e_rr_min = np.zeros_like(vec_i)
                    vec_e_rr_max = np.zeros_like(vec_i)
                    for n in range(len(vec_i)):
                        point = ([min(t_j_available), r_g_off_list[m], vec_i[n]])
                        vec_e_rr_min[n] = interpn(points, values, point) / 1000000000
                        point = ([max(t_j_available), r_g_off_list[m], vec_i[n]])
                        vec_e_rr_max[n] = interpn(points, values, point) / 1000000000

                    # self written estimation in case of selected t_j is out of bounds to interpolate via interpn-function
                    mean_max = sum(vec_e_rr_max) / len(vec_e_rr_max)
                    mean_min = sum(vec_e_rr_min) / len(vec_e_rr_min)

                    mean_diff = (mean_max-mean_min)/mean_max
                    temp_diff_max_min = max(t_j_available) - min(t_j_available)

                    if t_j_list[m] < min(t_j_available):
                        temp_diff = min(t_j_available) - t_j_list[m]
                        if mean_diff*temp_diff/temp_diff_max_min < 1:
                            vec_e_rr = vec_e_rr_min * (1 - mean_diff * temp_diff / temp_diff_max_min)
                        else:
                            vec_e_rr = np.zeros_like(vec_e_rr_min)


                    elif t_j_list[m] > max(t_j_available):
                        temp_diff = t_j_list[m] - max(t_j_available)
                        vec_e_rr = vec_e_rr_max * (1+mean_diff*temp_diff/temp_diff_max_min)


                    label = f"{transistor_list[m].name} (data estimated)"

                matplotlibwidget.axis.plot(vec_i, vec_e_rr, color=color_list[m], label=label)

        except:
            MainWindow.show_popup_message(MainWindow, f"Diode energy i_e curve is not available for <b>{transistor_list[m].name}</b>!")

        try:
            matplotlibwidget.axis.legend(fontsize=5)
            matplotlibwidget.axis.set(xlabel="Current in A",
                                      ylabel="Loss energy in J")
            matplotlibwidget.axis.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
            matplotlibwidget.axis.set_position([0.12, 0.2, 0.9, 0.7])
            matplotlibwidget.axis.grid()
            matplotlibwidget.figure.canvas.draw_idle()

            matplotlibwidget.cursor = Cursor(matplotlibwidget.axis, horizOn=True, vertOn=True, useblit=True,
                                             color="Green", linewidth=1)
            matplotlibwidget.figure.canvas.mpl_connect("button_press_event", clicked)
        except:
            pass