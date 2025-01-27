from __future__ import annotations
import numpy as np
import warnings
import pymongo
from pymongo.errors import ServerSelectionTimeoutError

# ---------------------------------
# check functions
# ---------------------------------


def check_realnum(float_to_check: float) -> bool:
    """
    Check if argument is real numeric scalar. Raise TypeError if not. None is also accepted because it is valid for
    optional keys. Mandatory keys that must not contain None are checked somewhere else beforehand.

    :param float_to_check: input argument
    :type float_to_check: float

    :raises TypeError: if float_to_check is not numeric

    :return: True in case of numeric scalar.
    :rtype: bool
    """
    if isinstance(float_to_check, (int, float, np.integer, np.floating)) or float_to_check is None:
        return True
    raise TypeError(f"{float_to_check} is not numeric.")


def check_2d_dataset(dataset_to_check: np.array) -> bool:
    """
    Check if argument is real 2D-dataset of right shape. None is also accepted because it is
    valid for optional keys. Mandatory keys that must not contain None are checked somewhere else beforehand.

    :param dataset_to_check: 2d-dataset
    :type dataset_to_check: np.array

    :raises TypeError: if the passed argument is a 2D-numpy array with real numeric values

    :return: True in case of valid 2d-dataset
    :rtype: bool
    """
    if dataset_to_check is None:
        return True
    if isinstance(dataset_to_check, np.ndarray):
        if np.all(np.isreal(dataset_to_check)):
            if dataset_to_check.ndim == 2:
                if dataset_to_check.shape[0] == 2:
                    return True
    raise TypeError("Invalid dataset. Must be 2D-numpy array with shape (2,x) and real numeric values.")


def check_str(string_to_check: str) -> bool:
    """
    Check if argument is string. Function not necessary but helpful to keep raising of errors
    consistent with other type checks. None is also accepted because it is valid for optional keys. Mandatory keys that
    must not contain None are checked somewhere else beforehand.

    :param string_to_check: input string
    :type string_to_check: str
    :raises TypeError: if the argument is not of type string
    :return: True in case of valid string
    :rtype: bool
    """
    if isinstance(string_to_check, str) or string_to_check is None:
        return True
    raise TypeError(f"{string_to_check} is not a string.")


def csv2array(csv_filename: str, first_xy_to_00: bool = False, second_y_to_0: bool = False,
              first_x_to_0: bool = False, mirror_xy_data: bool = False) -> np.array:
    """
    Imports a .csv file and extracts its input to a numpy array. Delimiter in .csv file must be ';'. Both ',' or '.'
    are supported as decimal separators. .csv file can generated from a 2D-graph for example via
    https://apps.automeris.io/wpd/

    .. todo: Check if array needs to be transposed? (Always the case for webplotdigitizer)

    :param csv_filename: Insert .csv filename, e.g. "switch_channel_25_15v"
    :type csv_filename: str
    :param first_xy_to_00: Set 'True' to change the first value pair to zero. This is necessary in
        case of webplotdigitizer returns the first value pair e.g. as -0,13; 0,00349.
    :type first_xy_to_00: bool
    :param second_y_to_0: Set 'True' to set the second y-value to zero. This is interesting in
        case of diode / igbt forward channel characteristic, if you want to make sure to set the point where the ui-graph
        leaves the u axis on the u-point to zero. Otherwise there might be a very small (and negative) value of u.
    :type second_y_to_0: bool
    :param first_x_to_0: Set 'True' to set the first x-value to zero. This is interesting in
        case of nonlinear input/output capacities, e.g. c_oss, c_iss, c_rss
    :type first_x_to_0: bool
    :param mirror_xy_data: Takes the absolute() of both axis. Used for given mirrored data, e.g. some datasheet show diode data in the 3rd quadrant instead of the 1st quadrant
    :type mirror_xy_data: bool

    :return: 1d array, ready to use in the transistor database
    :rtype: np.array
    """
    # See issue #5: German csv-files use ; as separator, english systems use , as separator
    # if ; is available in the file, csv-file generation was made by a german-language operating system
    file1 = open(csv_filename, "r")
    readfile = file1.read()
    if ';' in readfile:
        # csv-file was generated by a german language system
        array = np.genfromtxt(csv_filename, delimiter=";",
                              converters={0: lambda s: float(s.decode("UTF-8").replace(",", ".")),
                                          1: lambda s: float(s.decode("UTF-8").replace(",", "."))})
    else:
        # csv-file was generated by a english language system
        array = np.genfromtxt(csv_filename, delimiter=",")
    file1.close()

    if first_xy_to_00:
        array[0][0] = 0  # x value
        array[0][1] = 0  # y value

    if second_y_to_0:
        array[1][1] = 0  # y value

    if first_x_to_0:
        array[0][0] = 0  # x value

    if mirror_xy_data:
        array = np.abs(array)

    return np.transpose(array)


def check_float(float_to_check: int | float) -> bool:
    """
    Checks if argument is a float.
    :param float_to_check: number to check
    :type float_to_check: int | float

    :return: True for float, False for everything else
    :rtype: bool
    """
    try:
        float(float_to_check)
        return True
    except ValueError:
        return False

# ---------------------------------
# functions to generate a transistor
# ---------------------------------


def merge_curve(curve: np.array, curve_detail: np.array) -> np.array:
    """
    Merges two equal curves, one of which contains an enlarged section of the first curve.
    Use case is the merging of capacity curves, here often two curves (normal and zoom) are given in the data sheets.

    :param curve: full curve
    :type curve: np.array
    :param curve_detail: curve with zoom on x-axis
    :type curve_detail: np.array

    :return: merged curve
    :rtype: np.array

    :Example: (e.g. merges c_oss curve from 0-200V and from 0-1000V)

    >>> import transistordatabase as tdb
    >>> c_oss_normal = tdb.csv2array('transistor_c_oss.csv', first_x_to_0=True)
    >>> c_oss_detail = tdb.csv2array('transistor_c_oss_detail.csv', first_x_to_0=True)
    >>> c_oss_merged = tdb.merge_curve(c_oss_normal, c_oss_detail)

    """

    # find out max(x) from detailed curve
    curve_detail_max_x = max(curve_detail[0])

    merged_curve = curve_detail.copy()

    # cut all values that are smaller than max(x) from
    for x in range(len(curve[0])):
        if curve[0][x] > curve_detail_max_x:
            merged_curve = np.append(merged_curve, [[curve[0][x]], [curve[1][x]]], axis=1)
            type(merged_curve)
    return merged_curve

# ---------------------------------
# Database interactions
# ---------------------------------


def print_TDB(filters: list[str] | None = None, collection_name: str = "local") -> list[str]:
    warnings.warn("'print_TDB'-function will be deprecated soon. Use 'print_tdb' instead.")
    return print_tdb(filters=filters, collection_name=collection_name)


def print_tdb(filters: list[str] | None = None, collection_name: str = "local") -> list[str]:
    """
    Print all transistorelements stored in the local database

    :param filters: filters for searching the database, e.g. 'name' or 'type'
    :type filters: List[str]
    :param collection_name: Choose database name in local mongodb client. Default name is "collection"
    :type collection_name: str

    :return: Return a list with all transistor objects fitting to the search-filter
    :rtype: list

    :Example:

    >>> import transistordatabase as tdb
    >>> tdb.print_tdb()
    >>> # or
    >>> tdb.print_tdb(collection = 'type')
    """
    # Note: Never use mutable default arguments
    # see https://florimond.dev/en/posts/2018/08/python-mutable-defaults-are-the-source-of-all-evil/
    # This is the better solution
    filters = filters or []

    if collection_name == "local":
        mongodb_collection = connect_local_tdb()
    else:
        # TODO: support other collections. As of now, other database connections also connects to local-tdb
        warnings.warn("Connection of other databases than the local on not implemented yet. Connect so local database")
        mongodb_collection = connect_local_tdb()
    if not isinstance(filters, list):
        if isinstance(filters, str):
            filters = [filters]
        else:
            raise TypeError(
                "The 'filters' argument must be specified as a list of strings or a single string but is"
                f" {type(filters)} instead.")
    if "name" not in filters:
        filters.append("name")
    """Filters must be specified according to the respective objects they're associated with. 
    e.g. 'type' for type of Transistor or 'diode.technology' for technology of Diode."""
    returned_cursor = mongodb_collection.find({}, filters)
    name_list = []
    for tran in returned_cursor:
        print(tran)
        name_list.append(tran['name'])
    return name_list


# ---------------------------------
# MongoDB database interactions
# ---------------------------------

def connect_TDB(host: str):
    warnings.warn("'connect_TDB'-function will be deprecated soon. Use 'connect_tdb' instead.")
    return connect_tdb(host)


def connect_tdb(host: str):
    """
    A method for establishing connection with transistordatabase_exchange.

    :param host: "local" is specified by default, other cases need to be investigated
    :type host: str

    :return: transistor_database collection
    """
    if host == "local":
        host = "mongodb://localhost:27017/"
    my_transistor_database = pymongo.MongoClient(host)
    return my_transistor_database.transistor_database.collection


def connect_local_TDB():
    warnings.warn("'connect_local_TDB'-function will be deprecated soon. Use 'connect_local_tdb' instead.")
    return connect_local_tdb()

def connect_local_tdb():
    """
    A method for establishing connection with transistordatabase_exchange.
    Internally used by

      - update_from_fileexchange() method to sync the local with transistordatabase_File_Exchange
      - load() methods for saving and loading the transistor object to local mongodb-database.

    :return: transistor_database collection

    :raises pymongo.errors.ServerSelectionTimeoutError: if there is no mongoDB instance running
    """
    try:
        max_server_delay = 1
        host = "mongodb://localhost:27017/"
        my_client = pymongo.MongoClient(host, serverSelectionTimeoutMS=max_server_delay)
        my_client.server_info()
    except ServerSelectionTimeoutError:
        msg = 'Make sure that your MongoDB instance is running. If not please install it from ' \
              'https://docs.mongodb.com/manual/administration/install-community/'
        raise MissingServerConnection(msg)
    else:
        return my_client.transistor_database.collection


def drop_local_tdb():
    """
    Drop the local database

    :raises pymongo.errors.ServerSelectionTimeoutError: if there is no mongoDB instance running
    """
    try:
        max_server_delay = 1
        host = "mongodb://localhost:27017/"
        my_client = pymongo.MongoClient(host, serverSelectionTimeoutMS=max_server_delay)
        my_client.server_info()
    except ServerSelectionTimeoutError:
        msg = 'Make sure that your MongoDB instance is running. If not please install it from ' \
              'https://docs.mongodb.com/manual/administration/install-community/'
        raise MissingServerConnection(msg)
    else:
        my_client.drop_database('transistor_database')


class MissingServerConnection(ServerSelectionTimeoutError):
    pass

# ---------------------------------
# Functions for matlab exporter
# ---------------------------------


def dict2matlab(input_dict: dict) -> dict:
    """
    Cleans a python dict and makes it compatible with matlab

    Dict must be cleaned from 'None's to np.nan (= NaN in Matlab)
    see https://stackoverflow.com/questions/35985923/replace-none-in-a-python-dictionary

    :param input_dict: dictionary to be cleaned
    :type input_dict: dict

    :return: 'clean' matlab-compatible transistor dictionary
    :rtype: dict
    """
    result = {}
    for key, value in input_dict:
        if value is None:
            value = np.nan
        result[key] = value
    return result


# ---------------------------------
# Misc.
# ---------------------------------
def r_g_max_rapid_channel_turn_off(v_gsth: float, c_ds: float, c_gd: float, i_off: float | list[float],
                                   v_driver_off: float) -> float:
    """
    Calculates the maximum gate resistor to achieve no turn-off losses when working with MOSFETs
    'rapid channel turn-off' (rcto)

    :param v_gsth: gate threshold voltage
    :type v_gsth: float
    :param c_ds: equivalent drain-source capacitance
    :type c_ds: float
    :param c_gd: equivalent gate-drain capacitance
    :type c_gd: float
    :param i_off: turn-off current
    :type i_off: float or List[float]
    :param v_driver_off: Driver voltage during turn-off
    :type v_driver_off: float

    :return: r_g_max_rcto maximum gate resistor to achieve rapid channel turn-off
    :rtype: float

    .. note::
        Input (e.g. i_off can also be a vector)

    .. seealso::
        D. Kubrick, T. Dürbaum, A. Bucher
        'Investigation of Turn-Off Behaviour under the Assumption of Linear Capacitances'
        International Conference of Power Electronics Intelligent Motion Power Quality 2006, PCIM 2006, p. 239 –244
    """
    return (v_gsth - v_driver_off) / i_off * (1 + c_ds / c_gd)
