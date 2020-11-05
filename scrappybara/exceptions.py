"""Exceptions raised by Scrappybara"""


class DestinationFolderNotEmtpyError(Exception):
    """Raised when running a script whose writing folder is not empty"""

    def __init__(self, folder_path):
        super().__init__('destination folder "%s" not empty' % str(folder_path))


class ArgumentValueError(Exception):
    """Raised when a function is called with wrong call arg value"""

    def __init__(self, arg_name, value, valid_values):
        """Arg valid_values is a set of strings"""
        super().__init__("'%s' is not a valid value for the argument '%s'. Valid values are: %s." % (
            value, arg_name, str(valid_values)))
