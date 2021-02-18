import persistent
import datetime
import numpy as np
import re
from typing import List
from matplotlib import pyplot as plt


class Transistor(persistent.Persistent):
    """Groups data of all other classes for a single transistor. Methods are specified in such a way that only
    user-interaction with this class is necessary (ToDo!)
    Documentation on how to add or extract a transistor-object to/from the database can be found in (ToDo!)
    """
    name: str  # Name of the transistor. Choose as specific as possible. # Mandatory
    transistor_type: str  # Mandatory
    # User-specific data
    author: str  # Mandatory
    comment: [str, None]  # Optional
    # Date and template data. Should not be changed manually.
    # ToDo: Add methods to automatically determine dates and template_version on construction or update.
    template_version: str  # Mandatory/Automatic
    template_date: "datetime.date"  # Mandatory/Automatic
    creation_date: "datetime.date"  # Mandatory/Automatic
    last_modified: "datetime.date"  # Mandatory/Automatic
    # Manufacturer- and part-specific data
    manufacturer: str  # Mandatory
    datasheet_hyperlink: [str, None]  # Make sure this link is valid.  # Optional
    datasheet_date: ["datetime.date", None]  # Optional
    datasheet_version: [str, None]  # Optional
    housing_area: float  # Unit: mm^2  # Mandatory # ToDo: Also SI Units?
    cooling_area: float  # Unit: mm^2  # Mandatory
    housing_type: str  # e.g. TO-220, etc. # Mandatory. Must be from a list of specific strings.
    # These are documented in their respective class definitions
    switch: "Switch"
    diode: "Diode"
    meta: "Metadata"
    # Thermal data. See git for equivalent thermal circuit diagram.
    r_th_cs: [float, int, None]  # Unit: K/W  # Optional
    r_th_switch_cs: [float, int, None]  # Unit: K/W  # Optional
    r_th_diode_cs: [float, int, None]  # Unit: K/W  # Optional
    # Absolute maximum ratings
    v_max: [float, int]  # Unit: V  # Mandatory
    i_max: [float, int]  # Unit: A  # Mandatory
    # Rated operation region
    i_cont: [float, int, None]  # Unit: A  # e.g. Fuji: I_c, Semikron: I_c,nom # Mandatory

    def __init__(self, transistor_args, switch_args, diode_args):
        if self.isvalid_dict(transistor_args, 'Transistor'):
            self.name = transistor_args.get('name')
            self.transistor_type = transistor_args.get('transistor_type')
            self.author = transistor_args.get('author')
            self.technology = transistor_args.get('meta_type')
            self.template_version = transistor_args.get('template_version')
            self.template_date = transistor_args.get('template_date')
            self.creation_date = transistor_args.get('creation_date')
            self.last_modified = transistor_args.get('last_modified')
            self.comment = transistor_args.get('comment')
            self.manufacturer = transistor_args.get('manufacturer')
            self.datasheet_hyperlink = transistor_args.get('datasheet_hyperlink')
            self.datasheet_date = transistor_args.get('datasheet_date')
            self.datasheet_version = transistor_args.get('datasheet_version')
            self.housing_area = transistor_args.get('housing_area')
            self.cooling_area = transistor_args.get('cooling_area')
            # ToDo: This is a little ugly because the file "housing_types.txt" has to be opened twice.
            # Import list of valid housing types from "housing_types.txt"
            with open("housing_types.txt", "r") as housing_types_txt:
                housing_types = [line.replace("\n", "") for line in housing_types_txt.readlines()]
            # Remove all non alphanumeric characters from housing_type names and convert to lowercase for comparison
            alphanum_housing_types = [re.sub("[^A-Za-z0-9]+", "", line).lstrip().lower() for line in housing_types]
            housing_type = transistor_args.get('housing_type')
            # Get index where the housing_type was found in "housing_types.txt"
            idx = alphanum_housing_types.index(re.sub("[^A-Za-z0-9]+", "", housing_type).lstrip().lower())
            # Don't use the name in transistor_args but the matching name in "housing_types.txt"
            self.housing_type = housing_types[idx]
            self.r_th_cs = transistor_args.get('r_th_cs')
            self.r_th_switch_cs = transistor_args.get('r_th_switch')
            self.r_th_diode_cs = transistor_args.get('r_th_diode_cs')
            self.v_max = transistor_args.get('v_max')
            self.i_max = transistor_args.get('i_max')
            self.i_cont = transistor_args.get('i_cont')
        else:
            # ToDo: Is this a value or a type error?
            # ToDo: Move these raises to isvalid_dict() by checking dict_type for 'None' or empty dicts?
            raise TypeError("Dictionary 'transistor_args' is empty or 'None'. This is not allowed since following keys"
                            "are mandatory: 'name', 'transistor_type', 'author', 'manufacturer', 'housing_area', "
                            "'cooling_area', 'housing_type', 'v_max', 'i_max', 'i_cont'")

        self.diode = self.Diode(diode_args)
        self.switch = self.Switch(switch_args)

    @staticmethod
    def isvalid_dict(dataset_dict, dict_type):
        """This method checks input argument dictionaries for their validity. It is checked whether all mandatory keys
        are present, have the right type and permitted values (e.g. 'MOSFET' or 'IGBT' or 'SiC-MOSFET' for 'transistor_type').
        Returns 'False' if dictionary is 'None' or Empty. These cases should be handled outside this method.
        Raises appropriate errors if dictionary invalid in other ways."""
        # ToDo: Add structure for Errors. e.g.: xx has wrong type, xx has wrong type, etc.
        # ToDo: Error if given key is not allowed?
        if dataset_dict is None:
            return False  # None represents an empty dataset. Can be valid depending on circumstances, hence no error.
        elif not isinstance(dataset_dict, dict):
            raise TypeError("Expected dictionary with " + str(dict_type) + " arguments but got "
                            + str(type(dataset_dict)) + " instead.")
        elif not bool(dataset_dict):
            return False  # Empty dictionary. Can be valid depending on circumstances, hence no error.

        elif dict_type == 'ChannelData':
            # ToDo: v_g mandatory for switch, but nut for diode
            # Determine necessary keys.
            check_keys = {'t_j', 'v_i_data'}
            # Check if all necessary keys are contained in the dict.
            if dataset_dict.keys() < check_keys:
                raise KeyError("Dictionary does not contain all keys necessary for ChannelData object "
                               "creation. Mandatory keys: 't_j', 'v_i_data'")
            # Check if all values have appropriate types.
            elif check_realnum(dataset_dict.get('t_j')) and check_2d_dataset(dataset_dict.get('v_i_data')):
                # TypeError is raised in 'check_realnum()' or 'check_2d_dataset()' if check fails.
                return True

        elif dict_type == 'SwitchEnergyData':
            if 'dataset_type' not in dataset_dict:
                raise KeyError("Dictionary does not contain 'dataset_type' key necessary for SwitchEnergyData object "
                               "creation. 'dataset_type' must be 'single', 'r_e' or 'i_e'. Check SwitchEnergyData class"
                               " for further information.")
            # Determine necessary keys.
            elif dataset_dict.get('dataset_type') == 'single':
                check_keys = {'t_j', 'v_supply', 'v_g', 'e_x', 'r_g', 'i_x'}
                numeric_keys = {'t_j', 'v_supply', 'v_g', 'e_x', 'r_g', 'i_x'}
                array_keys = {}
            elif dataset_dict.get('dataset_type') == 'graph_r_e':
                check_keys = {'t_j', 'v_supply', 'v_g', 'r_e_data', 'i_x'}
                numeric_keys = {'t_j', 'v_supply', 'v_g', 'i_x'}
                array_keys = {'r_e_data'}
            elif dataset_dict.get('dataset_type') == 'graph_i_e':
                check_keys = {'t_j', 'v_supply', 'v_g', 'i_e_data', 'r_g'}
                numeric_keys = {'t_j', 'v_supply', 'v_g', 'r_g'}
                array_keys = {'i_e_data'}
            else:
                raise ValueError("Wrong dataset_type for creation of SwitchEnergyData object. Must be 'single', "
                                 "'graph_r_e' or 'graph_i_e'. Check SwitchEnergyData class for further "
                                 "information.")
            # Check if all necessary keys are contained in the dict.
            if dataset_dict.keys() < check_keys:
                raise KeyError("Dictionary does not contain all keys necessary for SwitchEnergyData object "
                               "creation. Mandatory keys are documented in the SwitchEnergyData class.")
            # Check if all values have appropriate types.
            elif all([check_realnum(dataset_dict.get(numeric_key)) for numeric_key in numeric_keys]) and \
                    all([check_2d_dataset(dataset_dict.get(array_key)) for array_key in array_keys]):
                # TypeError is raised in 'check_realnum()' or 'check_2d_dataset()' if check fails.
                return True

        elif dict_type == 'Switch_LinearizedModel':
            # Determine necessary keys.
            check_keys = {'t_j', 'v_g', 'i_channel', 'r_channel', 'v0_channel'}
            numeric_keys = {'t_j', 'v_g', 'i_channel', 'r_channel', 'v0_channel'}
            # Check if all necessary keys are contained in the dict.
            if dataset_dict.keys() < check_keys:
                raise KeyError("Dictionary does not contain all keys necessary for Switch LinearizedModel object "
                               "creation. Mandatory keys: 't_j', 'v_g', 'i_channel', 'r_channel', 'v0_channel'")
            # Check if all values have appropriate types.
            elif all([check_realnum(dataset_dict.get(numeric_key)) for numeric_key in numeric_keys]):
                # TypeError is raised in 'check_realnum()' if check fails.
                return True

        elif dict_type == 'Diode_LinearizedModel':
            # Determine necessary keys.
            check_keys = {'t_j', 'v_g', 'i_channel', 'r_channel'}
            numeric_keys = {'t_j', 'v_g', 'i_channel', 'r_channel', 'v0_channel'}
            # Check if all necessary keys are contained in the dict.
            if dataset_dict.keys() < check_keys:
                raise KeyError("Dictionary does not contain all keys necessary for Diode LinearizedModel object "
                               "creation. Mandatory keys: 't_j', 'v_g', 'i_channel', 'r_channel'")
            # Check if all values have appropriate types.
            elif all([check_realnum(dataset_dict.get(numeric_key)) for numeric_key in numeric_keys]):
                # TypeError is raised in 'check_realnum()' if check fails.
                return True

        elif dict_type == 'Transistor':
            # ToDo: Add type checks for optional arguments
            check_keys = {'name', 'transistor_type', 'author', 'manufacturer', 'housing_area', 'cooling_area',
                          'housing_type', 'v_max', 'i_max', 'i_cont'}
            str_keys = {'name', 'transistor_type', 'author', 'manufacturer', 'housing_type'}
            numeric_keys = {'housing_area', 'cooling_area', 'v_max', 'i_max', 'i_cont'}
            if dataset_dict.keys() < check_keys:
                raise KeyError("Dictionary 'transistor_args' does not contain all keys necessary for Transistor object "
                               "creation. Mandatory keys: 'name', 'transistor_type', 'author', 'manufacturer', "
                               "'housing_area', 'cooling_area', 'housing_type', 'v_max', 'i_max', 'i_cont'")
            elif dataset_dict.get('transistor_type') not in ['MOSFET', 'IGBT', 'SiC-MOSFET']:
                raise ValueError("'transistor_type' must be either 'MOSFET' or 'IGBT' or 'SiC-MOSFET'")
            # Check if all values have appropriate types.
            else:
                # Import list of valid housing types from "housing_types.txt"
                with open("housing_types.txt", "r") as housing_types_txt:
                    housing_types = [line.replace("\n", "") for line in housing_types_txt.readlines()]
                # Remove all non alphanumeric characters from housing_type names and convert to lowercase for comparison
                alphanum_housing_types = [re.sub("[^A-Za-z0-9]+", "", line).lstrip().lower() for line in housing_types]
                housing_type = dataset_dict.get('housing_type')
                if re.sub("[^A-Za-z0-9]+", "", housing_type).lstrip().lower() not in alphanum_housing_types:
                    raise ValueError("Housing type " + str(housing_type) + " is not allowed. See file "
                                     "'housing_types.txt' for a list of supported types.")
                # Check if all attributes have valid type.
                elif all([check_realnum(dataset_dict.get(numeric_key)) for numeric_key in numeric_keys]) and \
                        all([check_str(dataset_dict.get(str_key)) for str_key in str_keys]):
                    # TypeError is raised in 'check_realnum()' or 'check_str()' if check fails.
                    return True

        elif dict_type == 'FosterThermalModel':
            # FosterThermalModel does not have mandatory keys.
            # Check which optional keys are given.
            check_keys = list(dataset_dict.keys())
            numeric_keys = {'r_th_total', 'c_th_total', 'tau_total'}  # possible keys
            numeric_keys = {numeric_key for numeric_key in numeric_keys if numeric_key in check_keys}  # actual keys
            list_keys = {'r_th_vector', 'c_th_vector', 'tau_vector'}  # possible keys
            list_keys = {list_key for list_key in list_keys if list_key in check_keys}  # actual keys
            array_keys = {'transient_data'}  # possible keys
            array_keys = {array_key for array_key in array_keys if array_key in check_keys}  # actual keys
            # Check if all elements in 'r_th_vector', 'c_th_vector', 'tau_vector' are real numeric (float, int)
            bool_list_numeric = all([all([check_realnum(single_value) for single_value in dataset_dict.get(list_key)])
                                    for list_key in list_keys])
            # Check if 'r_th_vector', 'c_th_vector', 'tau_vector' have same length
            # ToDo: Check if at least 2/3 of C, R, tau are given.
            list_sizes = [len(dataset_dict.get(list_key)) for list_key in list_keys]
            if not list_sizes.count(list_sizes[0]) == len(list_sizes):
                raise TypeError("The lists 'r_th_vector', 'c_th_vector', 'tau_vector' (if given) must be the same "
                                "size.")
            # Check if all values have appropriate types.
            if all([check_realnum(dataset_dict.get(numeric_key)) for numeric_key in numeric_keys]) and \
                    all([check_2d_dataset(dataset_dict.get(array_key)) for array_key in array_keys]) and \
                    bool_list_numeric:
                # TypeError is raised in 'check_realnum()' or 'check_2d_dataset()' if check fails.
                return True

        elif dict_type == 'Switch':
            # Switch does not have mandatory keys.
            # Check which optional keys are given.
            check_keys = list(dataset_dict.keys())
            str_keys = {'comment', 'manufacturer', 'technology'}  # possible keys
            str_keys = {str_key for str_key in str_keys if str_key in check_keys}  # actual keys
            numeric_keys = {'c_oss', 'c_iss', 'c_rss'}  # possible keys
            numeric_keys = {numeric_key for numeric_key in numeric_keys if numeric_key in check_keys}  # actual keys
            # Check if all values have appropriate types.
            if all([check_realnum(dataset_dict.get(numeric_key)) for numeric_key in numeric_keys]) and \
                    all([check_str(dataset_dict.get(str_key)) for str_key in str_keys]):
                # TypeError is raised in 'check_realnum()' or 'check_str()' if check fails.
                return True

        elif dict_type == 'Diode':
            # Diode does not have mandatory keys.
            # Check which optional keys are given.
            check_keys = list(dataset_dict.keys())
            str_keys = {'comment', 'manufacturer', 'technology'}  # possible keys
            str_keys = {str_key for str_key in str_keys if str_key in check_keys}  # actual keys
            # Check if all values have appropriate types.
            if all([check_str(dataset_dict.get(str_key)) for str_key in str_keys]):
                # TypeError is raised in 'check_realnum()' or 'check_str()' if check fails.
                return True

    class FosterThermalModel:
        """Contains data to specify parameters of the Foster thermal model. This model describes the transient
        temperature behavior as a thermal RC-network. The necessary parameters can be estimated by curve-fitting
        transient temperature data supplied in transient_data or by manually specifying the individual 2 out of 3 of the
         parameters R, C, and tau."""
        # ToDo: Add function to estimate parameters from transient data.
        # ToDo: Add function to automatically calculate missing parameters from given ones.
        # Thermal resistances of RC-network (array).
        r_th_vector: ["np.ndarray[np.float64]", None]  # Unit: K/W  # Optional
        # Sum of thermal resistances of n-pole RC-network (scalar).
        r_th_total: ["np.ndarray[np.float64]", None]  # Unit: K/W  # Optional
        # Thermal capacitances of n-pole RC-network (array).
        c_th_vector: ["np.ndarray[np.float64]", None]  # Unit: J/K  # Optional
        # Sum of thermal capacitances of n-pole low pass as (scalar).
        c_th_total: ["np.ndarray[np.float64]", None]  # Unit: J/K  # Optional
        # Thermal time constants of n-pole RC-network (array).
        tau_vector: ["np.ndarray[np.float64]", None]  # Unit: s  # Optional
        # Sum of thermal time constants of n-pole RC-network (scalar).
        tau_total: ["np.ndarray[np.float64]", None]  # Unit: s  # Optional
        # Transient data for extraction of the thermal parameters specified above.
        # Represented as a 2xm Matrix where row 1 is the time and row 2 the temperature.
        transient_data: ["np.ndarray[np.float64]", None]  # Units: Row 1: s; Row 2: K/W  # Optional

        def __init__(self, args):
            if Transistor.isvalid_dict(args, 'FosterThermalModel'):
                self.r_th_total = args.get('r_th_total')
                self.r_th_vector = args.get('r_th_vector')
                self.c_th_total = args.get('c_th_total')
                self.c_th_vector = args.get('c_th_vector')
                self.tau_total = args.get('tau_total')
                self.tau_vector = args.get('tau_vector')
                self.transient_data = args.get('transient_data')
            else:  # Can be constructed from empty or 'None' argument dictionary since no attributes are mandatory.
                self.r_th_total = None
                self.r_th_vector = None
                self.c_th_total = None
                self.c_th_vector = None
                self.tau_total = None
                self.tau_vector = None
                self.transient_data = None

    class Switch:
        """Contains data associated with the switchting-characteristics of a MOSFET/SiC-MOSFET or IGBT. Can contain multiple
        channel-, e_on- and e_off-datasets. """
        # Metadata
        comment: [str, None]  # Optional
        manufacturer: [str, None]  # Optional
        technology: [str, None]  # Semiconductor technology. e.g. IGBT3/IGBT4/IGBT7  # Optional
        # These are documented in their respective class definitions.
        thermal: "FosterThermalModel"  # Transient thermal model.  # Optional
        channel: List["ChannelData"]  # Switch channel voltage and current data.
        e_on: List["SwitchEnergyData"]  # Switch on energy data.
        e_off: List["SwitchEnergyData"]  # Switch of energy data.
        linearized_switch: List["LinearizedModel"]  # Static data valid for a specific operating point.
        # Constant Capacitances
        c_oss: [float, int, None]  # Unit: pF  # Optional
        c_iss: [float, int, None]  # Unit: pF  # Optional
        c_rss: [float, int, None]  # Unit: pF  # Optional

        def __init__(self, switch_args):
            # Current behavior on empty 'foster' dictionary: thermal object is still created but with empty attributes.
            # ToDo: Is this the right behavior or should the 'thermal' attribute be left empty istead?
            self.thermal = Transistor.FosterThermalModel(switch_args.get('foster'))
            if Transistor.isvalid_dict(switch_args, 'Switch'):
                self.c_oss = switch_args.get('c_oss')
                self.c_iss = switch_args.get('c_iss')
                self.c_rss = switch_args.get('c_rss')
                self.comment = switch_args.get('comment')
                self.manufacturer = switch_args.get('manufacturer')
                self.technology = switch_args.get('technology')
                # This currently accepts dictionaries and lists of dictionaries. Validity is only checked by keys and
                # not their values.
                self.channel = []  # Default case: Empty list
                if isinstance(switch_args.get('channel'), list):
                    # Loop through list and check each dict for validity. Only create ChannelData objects from valid
                    # dicts. 'None' and empty dicts are ignored.
                    for dataset in switch_args.get('channel'):
                        try:
                            if Transistor.isvalid_dict(dataset, 'ChannelData'):
                                self.channel.append(Transistor.ChannelData(dataset))
                        # If KeyError occurs during this, raise KeyError and add index of list occurrence to the message
                        except KeyError as error:
                            dict_list = switch_args.get('channel')
                            if not error.args:
                                error.args = ('',)  # This syntax is necessary because error.args is a tuple
                            error.args = ('KeyError occurred for index [' + str(dict_list.index(dataset)) + '] in list '
                                          'of Switch-ChannelData dictionaries: ',) + error.args
                            raise
                elif Transistor.isvalid_dict(switch_args.get('channel'), 'ChannelData'):
                    # Only create ChannelData objects from valid dicts
                    self.channel.append(Transistor.ChannelData(switch_args.get('channel')))

                self.e_on = []  # Default case: Empty list
                if isinstance(switch_args.get('e_on'), list):
                    # Loop through list and check each dict for validity. Only create SwitchEnergyData objects from
                    # valid dicts. 'None' and empty dicts are ignored.
                    for dataset in switch_args.get('e_on'):
                        try:
                            if Transistor.isvalid_dict(dataset, 'SwitchEnergyData'):
                                self.e_on.append(Transistor.SwitchEnergyData(dataset))
                        # If KeyError occurs during this, raise KeyError and add index of list occurrence to the message
                        except KeyError as error:
                            dict_list = switch_args.get('e_on')
                            if not error.args:
                                error.args = ('',)  # This syntax is necessary because error.args is a tuple
                            error.args = ('KeyError occurred for index [' + str(dict_list.index(dataset)) + '] in list '
                                          'of Switch-SwitchEnergyData dictionaries for e_on: ',) + error.args
                            raise
                elif Transistor.isvalid_dict(switch_args.get('e_on'), 'SwitchEnergyData'):
                    # Only create SwitchEnergyData objects from valid dicts
                    self.e_on.append(Transistor.SwitchEnergyData(switch_args.get('e_on')))

                self.e_off = []  # Default case: Empty list
                if isinstance(switch_args.get('e_off'), list):
                    for dataset in switch_args.get('e_off'):
                        try:
                            if Transistor.isvalid_dict(dataset, 'SwitchEnergyData'):
                                self.e_off.append(Transistor.SwitchEnergyData(dataset))
                        # If KeyError occurs during this, raise KeyError and add index of list occurrence to the message
                        except KeyError as error:
                            dict_list = switch_args.get('e_off')
                            if not error.args:
                                error.args = ('',)  # This syntax is necessary because error.args is a tuple
                            error.args = ('KeyError occurred for index [' + str(dict_list.index(dataset)) + '] in list '
                                          'of Switch-SwitchEnergyData dictionaries for e_off: ',) + error.args
                            raise
                elif Transistor.isvalid_dict(switch_args.get('e_off'), 'SwitchEnergyData'):
                    self.e_off.append(Transistor.SwitchEnergyData(switch_args.get('e_off')))

                self.linearized_switch = []  # Default case: Empty list
                if isinstance(switch_args.get('linearized_switch'), list):
                    # Loop through list and check each dict for validity. Only create LinearizedModel objects from
                    # valid dicts. 'None' and empty dicts are ignored.
                    for dataset in switch_args.get('linearized_switch'):
                        try:
                            if Transistor.isvalid_dict(dataset, 'Switch_LinearizedModel'):
                                self.linearized_switch.append(Transistor.LinearizedModel(dataset))
                        # If KeyError occurs during this, raise KeyError and add index of list occurrence to the message
                        except KeyError as error:
                            dict_list = switch_args.get('linearized_switch')
                            if not error.args:
                                error.args = ('',)  # This syntax is necessary because error.args is a tuple
                            error.args = ('KeyError occurred for index [' + str(dict_list.index(dataset)) + '] in list '
                                          'of Switch-LinearizedModel dictionaries: ',) + error.args
                            raise
                elif Transistor.isvalid_dict(switch_args.get('linearized_switch'), 'Switch_LinearizedModel'):
                    # Only create LinearizedModel objects from valid dicts
                    self.linearized_switch.append(Transistor.LinearizedModel(switch_args.get('linearized_switch')))

            else:  # Can be constructed from empty or 'None' argument dictionary since no attributes are mandatory.
                self.c_oss = None
                self.c_iss = None
                self.c_rss = None
                self.comment = None
                self.manufacturer = None
                self.technology = None
                self.channel = []
                self.e_on = []
                self.e_off = []
                self.linearized_switch = []

        def plot_all_channel_data(self):
            """ Plot all channel data """
            plt.figure()
            for i_channel in np.array(range(0,len(self.channel))):
                labelplot = "vg = " + str(self.channel[i_channel].v_g) + " V, T_J = " + str(self.channel[i_channel].t_j) + " °C"
                plt.plot(self.channel[i_channel].v_i_data[0], self.channel[i_channel].v_i_data[1], label=labelplot)

            plt.legend()
            plt.xlabel('Voltage in V')
            plt.ylabel('Current in A')
            plt.grid()
            plt.show()

        def plot_channel_data_vge(self, gatevoltage):
            """ Plot channel data with a chosen gate-voltage"""
            plt.figure()
            for i_channel in np.array(range(0,len(self.channel))):
                if self.channel[i_channel].v_g == gatevoltage:
                    labelplot = "vg = " + str(self.channel[i_channel].v_g) + " V, T_J = " + str(self.channel[i_channel].t_j) + " °C"
                    plt.plot(self.channel[i_channel].v_i_data[0], self.channel[i_channel].v_i_data[1], label=labelplot)

            plt.legend()
            plt.xlabel('Voltage in V')
            plt.ylabel('Current in A')
            plt.grid()
            plt.show()

        def plot_channel_data_temp(self, temperature):
            """ Plot channel data with chosen temperature"""
            plt.figure()
            for i_channel in np.array(range(0,len(self.channel))):
                if self.channel[i_channel].t_j == temperature:
                    labelplot = "vg = " + str(self.channel[i_channel].v_g) + " V, T_J = " + str(self.channel[i_channel].t_j) + " °C"
                    plt.plot(self.channel[i_channel].v_i_data[0], self.channel[i_channel].v_i_data[1], label=labelplot)

            plt.legend()
            plt.xlabel('Voltage in V')
            plt.ylabel('Current in A')
            plt.grid()
            plt.show()


        def plot_energy_data(self):
            """ Plot all switching data """
            plt.figure()
            # look for e_on losses
            for i_energy_data in np.array(range(0,len(self.e_on))):
                if self.e_on[i_energy_data].dataset_type == 'graph_i_e':
                    labelplot = "e_on: v_supply = " + str(self.e_on[i_energy_data].v_supply) + "V, vg = " + str(self.e_on[i_energy_data].v_g) + " V, T_J = " + str(self.e_on[i_energy_data].t_j) + " °C, R_g = " + str(self.e_on[i_energy_data].r_g) + " Ohm"
                    plt.plot(self.e_on[i_energy_data].i_e_data[0], self.e_on[i_energy_data].i_e_data[1], label=labelplot)

            # look for e_off losses
            for i_energy_data in np.array(range(0, len(self.e_off))):
                if self.e_off[i_energy_data].dataset_type == 'graph_i_e':
                    labelplot = "e_off: v_supply = " + str(self.e_off[i_energy_data].v_supply) + "V, vg = " + str(
                        self.e_off[i_energy_data].v_g) + " V, T_J = " + str(
                        self.e_off[i_energy_data].t_j) + " °C, R_g = " + str(
                        self.e_off[i_energy_data].r_g) + " Ohm"
                    plt.plot(self.e_off[i_energy_data].i_e_data[0], self.e_off[i_energy_data].i_e_data[1],
                             label=labelplot)

            plt.legend()
            plt.xlabel('Current in A')
            plt.ylabel('Loss-energy in J')
            plt.grid()
            plt.show()

    class Diode:
        """Contains data associated with the (reverse) diode-characteristics of a MOSFET/SiC-MOSFET or IGBT. Can contain multiple
        channel- and e_rr- datasets."""
        # Metadata
        comment: [str, None]  # Optional
        manufacturer: [str, None]  # Optional
        technology: [str, None]  # Semiconductor technology. e.g. IGBT3/IGBT4/IGBT7  # Optional
        # These are documented in their respective class definitions.
        thermal: ["FosterThermalModel", None]  # Transient thermal model.
        channel: List["ChannelData"]  # Diode forward voltage and forward current data.
        e_rr: List["SwitchEnergyData"]  # Reverse recovery energy data.
        linearized_diode: List["LinearizedModel"]  # Static data. Valid for a specific operating point.

        def __init__(self, diode_args):
            # Current behavior on empty 'foster' dictionary: thermal object is still created but with empty attributes.
            # ToDo: Is this the right behavior or should the 'thermal' attribute be left empty istead?
            self.thermal = Transistor.FosterThermalModel(diode_args.get('foster'))
            if Transistor.isvalid_dict(diode_args, 'Diode'):
                self.comment = diode_args.get('comment')
                self.manufacturer = diode_args.get('manufacturer')
                self.technology = diode_args.get('technology')
                # This currently accepts dictionaries and lists of dictionaries.
                self.channel = []  # Default case: Empty list
                if isinstance(diode_args.get('channel'), list):
                    # Loop through list and check each dict for validity. Only create ChannelData objects from valid
                    # dicts. 'None' and empty dicts are ignored.
                    for dataset in diode_args.get('channel'):
                        try:
                            if Transistor.isvalid_dict(dataset, 'ChannelData'):
                                self.channel.append(Transistor.ChannelData(dataset))
                        # If KeyError occurs during this, raise KeyError and add index of list occurrence to the message
                        except KeyError as error:
                            dict_list = diode_args.get('channel')
                            if not error.args:
                                error.args = ('',)  # This syntax is necessary because error.args is a tuple
                            error.args = ('KeyError occurred for index [' + str(dict_list.index(dataset)) + '] in list '
                                          'of Diode-ChannelData dictionaries: ',) + error.args
                            raise
                elif Transistor.isvalid_dict(diode_args.get('channel'), 'ChannelData'):
                    # Only create ChannelData objects from valid dicts
                    self.channel.append(Transistor.ChannelData(diode_args.get('channel')))

                self.e_rr = []  # Default case: Empty list
                if isinstance(diode_args.get('e_rr'), list):
                    # Loop through list and check each dict for validity. Only create SwitchEnergyData objects from
                    # valid dicts. 'None' and empty dicts are ignored.
                    for dataset in diode_args.get('e_rr'):
                        try:
                            if Transistor.isvalid_dict(dataset, 'SwitchEnergyData'):
                                self.e_rr.append(Transistor.SwitchEnergyData(dataset))
                        # If KeyError occurs during this, raise KeyError and add index of list occurrence to the message
                        except KeyError as error:
                            dict_list = diode_args.get('e_rr')
                            if not error.args:
                                error.args = ('',)  # This syntax is necessary because error.args is a tuple
                            error.args = ('KeyError occurred for index [' + str(
                                dict_list.index(dataset)) + '] in list '
                                                            'of Diode-SwitchEnergyData dictionaries for e_rr: ',) + error.args
                            raise
                elif Transistor.isvalid_dict(diode_args.get('e_rr'), 'SwitchEnergyData'):
                    # Only create SwitchEnergyData objects from valid dicts
                    self.e_rr.append(Transistor.SwitchEnergyData(diode_args.get('e_rr')))

                self.linearized_diode = []  # Default case: Empty list
                if isinstance(diode_args.get('linearized_diode'), list):
                    # Loop through list and check each dict for validity. Only create LinearizedModel objects from
                    # valid dicts. 'None' and empty dicts are ignored.
                    for dataset in diode_args.get('linearized_diode'):
                        try:
                            if Transistor.isvalid_dict(dataset, 'Diode_LinearizedModel'):
                                self.linearized_diode.append(Transistor.LinearizedModel(dataset))
                        # If KeyError occurs during this, raise KeyError and add index of list occurrence to the message
                        except KeyError as error:
                            dict_list = diode_args.get('linearized_diode')
                            if not error.args:
                                error.args = ('',)  # This syntax is necessary because error.args is a tuple
                            error.args = ('KeyError occurred for index [' + str(dict_list.index(dataset)) + '] in list '
                                          'of Diode-LinearizedModel dictionaries: ',) + error.args
                            raise
                elif Transistor.isvalid_dict(diode_args.get('linearized_diode'), 'Diode_LinearizedModel'):
                    # Only create LinearizedModel objects from valid dicts
                    self.linearized_diode.append(Transistor.LinearizedModel(diode_args.get('linearized_diode')))

            else:  # Can be constructed from empty or 'None' argument dictionary since no attributes are mandatory.
                self.comment = None
                self.manufacturer = None
                self.technology = None
                self.channel = []
                self.e_rr = []
                self.linearized_diode = []

        def plot_energy_data(self):
            """ Plot all switching data """

            # look for e_off losses
            if len(self.e_rr) != 0:
                plt.figure()
                for i_energy_data in np.array(range(0, len(self.e_rr))):
                    # check if data is available as 'graph_i_e'
                    if self.e_rr[i_energy_data].dataset_type == 'graph_i_e':
                        # add label plot
                        labelplot = "e_rr: v_supply = " + str(
                            self.e_rr[i_energy_data].v_supply) + "V, T_J = " + str(
                            self.e_rr[i_energy_data].t_j) + " °C, R_g = " + str(
                            self.e_rr[i_energy_data].r_g) + " Ohm"
                        # check if gate voltage is given (GaN Transistor, SiC-MOSFET)
                        # if ture, add gate-voltage to label
                        if isinstance(e_rr[i_energy_data].v_g, (int, float)):
                            labelplot = labelplot + ", vg = " + str(
                            self.e_rr[i_energy_data].v_g) + " V"

                        # plot
                        plt.plot(self.e_rr[i_energy_data].i_e_data[0], self.e_rr[i_energy_data].i_e_data[1],
                                 label=labelplot)
                plt.legend()
                plt.xlabel('Current in A')
                plt.ylabel('Loss-energy in J')
                plt.grid()
                plt.show()
            else:
                print("No Data available")

    class LinearizedModel:
        """Contains data for a linearized Switch/Diode depending on given operating point. Operating point specified by
        t_j, i_channel and v_g (not for all diode types)."""
        t_j: [int, float]  # Unit: K # Mandatory
        v_g: [int, float, None]  # Unit: V # Mandatory for Switch, Optional for some Diode types
        i_channel: [int, float]  # Unit: A # Mandatory
        r_channel: [int, float]  # Unit: Ohm Mandatory
        v0_channel: [int, float]  # Unit: V # Mandatory

        def __init__(self, args):
            self.t_j = args.get('t_j')
            self.v_g = args.get('v_g')
            self.i_channel = args.get('i_channel')
            self.r_channel = args.get('r_channel')
            self.v0_channel = args.get('v0_channel')

    class ChannelData:
        """Contains channel V-I data for either switch or diode. Data is given for only one junction temperature t_j.
        For different temperatures: Create additional ChannelData-objects and store them as a list in the respective
        Diode- or Switch-object.
        This data can be used to linearize the transistor at a specific operating point (ToDo!)"""

        # # Test condition: Must be given as scalar. Create additional objects for different temperatures.
        t_j: [int, float]  # Mandatory
        v_g: [int, float]  # Switch: Mandatory, Diode: optional (standard diode useless, for GaN 'diode' necessary
        # Dataset: Represented as a 2xm Matrix where row 1 is the voltage and row 2 the current.
        v_i_data: "np.ndarray[np.float64]"  # Units: Row 1: V; Row 2: A  # Mandatory

        def __init__(self, args):
            # Validity of args is checked in the constructor of Diode/Switch class and thus does not need to be
            # checked again here.
            self.t_j = args.get('t_j')
            self.v_i_data = args.get('v_i_data')
            self.v_g = args.get('v_g')

    class SwitchEnergyData:
        """Contains switching energy data for either switch or diode. The type of Energy (E_on, E_off or E_rr) is
        already implicitly specified by how the respective objects of this class are used in a Diode- or Switch-object.
        For each set (e.g. every curve in the datasheet) of switching energy data a separate object should be created.
        This also includes the reference values in a datasheet given without a graph. (Those are considered as data sets
        with just a single data point.)
        Data sets with more than one point are given as i_e_data with an r_g parameter or as r_e_data with an i_x
        parameter.
        Unused parameters or datasets should be left empty.
        Which of these cases (single point, E vs I dataset, E vs R dataset) is valid for the current object also needs
        to be specified by the dataset_type-property."""

        # Type of the dataset:
        # single: e_x, r_g, i_x are scalars. Given e.g. by a table in the datasheet.
        # graph_r_e: r_e is a 2-dim numpy array with two rows. i_x is a scalar. Given e.g. by an E vs R graph.
        # graph_i_e: i_e is a 2-dim numpy array with two rows. r_g is a scalar. Given e.g. by an E vs I graph.
        dataset_type: str  # Mandatory
        # Test conditions. These must be given as scalars. Create additional objects for e.g. different temperatures.
        t_j: [int, float]  # Unit: °C  # Mandatory
        v_supply: [int, float]  # Unit: V  # Mandatory
        v_g: [int, float]  # Unit: V  # Mandatory
        # Scalar dataset-parameters. Some of these can be 'None' depending on the dataset_type.
        e_x: [int, float, None]  # Unit: J
        r_g: [int, float, None]  # Unit: Ohm
        i_x: [int, float, None]  # Unit: A
        # Dataset. Only one of these is allowed. The other should be 'None'.
        i_e_data: ["np.ndarray[np.float64]", None]  # Units: Row 1: A; Row 2: J
        r_e_data: ["np.ndarray[np.float64]", None]  # Units: Row 1: Ohm; Row 2: J
        # ToDo: Add MOSFET capacitance. Discuss with Philipp.
        # ToDo: Add additional class for linearized switching loss model with capacitances. (See infineon application
        #  note.)
        # ToDo: Option 1: Look up table like it's currently implemented.
        # ToDo: Option 2: https://application-notes.digchip.com/070/70-41484.pdf
        # ToDO: Option 3: K_i, K_v, G_i. Add as empty class with pass.

        def __init__(self, args):
            # Validity of args is checked in the constructor of Diode/Switch class and thus does not need to be
            # checked again here.
            # ToDo: Always check dataset_type and determine which arguments should be ignored.
            self.dataset_type = args.get('dataset_type')
            self.v_supply = args.get('v_supply')
            self.v_g = args.get('v_g')
            self.t_j = args.get('t_j')
            self.e_x = args.get('e_x')
            self.r_g = args.get('r_g')
            self.i_x = args.get('i_x')
            self.i_e_data = args.get('i_e_data')
            self.r_e_data = args.get('r_e_data')

    def linearize_switch_ui_graph(self, temperature, gatevoltage, current):
        """ get interpolated channel parameters. This function searches for ui_graphs with the choosen temperature and gatevoltage. At the desired current,
        the equivalent parameters for u_channel and r_channel are returned"""
        # ToDo: rethink method name. May include switch or diode as a parameter and use one global function
        # ToDo: check if this function works for all types of transistors
        # ToDo: Error handling
        # ToDo: Unittest for this method

        # in case of failure, return None
        v_channel = None
        r_channel = None

        # sweep trough channel array
        for i_channel in np.array(range(0, len(self.switch.channel))):
            # check if input parameters match to stored data. Only 'v_i_data'-data is used
            if self.switch.channel[i_channel].t_j == temperature and self.switch.channel[i_channel].v_g == gatevoltage:

                # interpolate data
                voltage_interpolated = np.interp(current, self.switch.channel[i_channel].v_i_data[1],
                                                 self.switch.channel[i_channel].v_i_data[0])

                # check kind of transistor type due to forward voltage value
                if self.transistor_type == 'MOSFET' or self.transistor_type == 'SiC-MOSFET':
                    # transistor has no forward voltage

                    # return values
                    v_channel = 0  # no forward voltage du to resistance behaviour
                    r_channel = voltage_interpolated / current
                else:
                    # transistor has forward voltage. Other interpolating point will be with 10% more current
                    # ToDo: Test this function if IGBT is available
                    voltage_interpolated_2 = np.interp(current * 1.1, self.switch.channel[i_channel].v_i_data[1],
                                                     self.switch.channel[i_channel].v_i_data[0])
                    r_channel = (voltage_interpolated_2 - voltage_interpolated) (0.1 * current)
                    v_channel = voltage_interpolated - r_channel * current

        return round(v_channel,2), round(r_channel,4)


def check_realnum(x):
    """Check if argument is real numeric scalar. Raise TypeError if not. """
    if not any([isinstance(x, int), isinstance(x, float)]):
        raise TypeError('{0} is not numeric.'.format(x))
    else:
        return True


def check_2d_dataset(x):
    """Check if argument is real 2D-dataset of right shape. Raise TypeError if not. """
    if isinstance(x, np.ndarray):
        if np.all(np.isreal(x)):
            if x.ndim == 2:
                if x.shape[0] == 2:
                    return True
    raise TypeError("Invalid dataset. Must be 2D-numpy array with shape (2,x) and real numeric values.")


def check_str(x):
    """Check if argument is string. Raise TypeError if not. Function not necessary but helpful to keep raising of errors
    consistent with other type checks."""
    if isinstance(x, str):
        return True
    raise TypeError('{0} is not a string.'.format(x))


def csv2array(csv_filename, set_first_value_to_zero, set_second_y_value_to_zero):
    """Imports a .csv file and extracts its input to a numpy array. Delimiter in .csv file must be ';'. Both ',' or '.'
    are supported as decimal separators. .csv file can generated from a 2D-graph for example via
    https://apps.automeris.io/wpd/

    csv_filename: str. Insert .csv filename, e.g. "switch_channel_25_15v"

    set_first_value_to_zero: boolean True/False. Set 'True' to change the first value pair to zero. This is necessary in
        case of webplotdigitizer returns the first value pair e.g. as -0,13; 0,00349.

    set_second_y_value_to_zero: boolean True/False. Set 'True' to set the second y-value to zero. This is interesting in
        case of diode / igbt forward channel characteristic, if you want to make sure to set the point where the ui-graph
        leaves the u axis on the u-point to zero. Otherwise there might be a very small (and negative) value of u.
    """
    array = np.genfromtxt(csv_filename, delimiter=";",
                          converters={0: lambda s: float(s.decode("UTF-8").replace(",", ".")),
                                      1: lambda s: float(s.decode("UTF-8").replace(",", "."))})

    if set_first_value_to_zero == True:
        array[0][0] = 0    # x value
        array[0][1] = 0    # y value

    if set_second_y_value_to_zero == True:
        array[1][1] = 0    # y value

    return np.transpose(array)  # ToDo: Check if array needs to be transposed? (Always the case for webplotdigitizer)
