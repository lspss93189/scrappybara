"""Customized exceptions raised by Scrappybara"""


class ArgumentValueError(Exception):

    def __init__(self, arg_name, value, valid_values):
        """Arg valid_values is a set of strings"""
        super().__init__("'%s' is not a valid value for the argument '%s'. Valid values are: %s." % (
            value, arg_name, str(valid_values)))
