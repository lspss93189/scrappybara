import getopt
import sys


def parse_cli_args(args=None):
    """Takes values from command line args or assigns default values.
    e.g. parse_args([('a', 'arg_1', 'default'), ('b', 'arg_2', False)]) will try to read from CLI: "-a value, -b"
      For each arg, pass a tuple with the shorthand, long name & default value.
      For any arg, the default value can be None.
      The arg type is detected by the default value (if not equal to None).
      If the default value is a boolean, using the arg will invert its default value.
    """
    if args is None:
        args = []
    # Parse args
    s_args = ''
    l_args = []
    for arg in args:
        short_arg = arg[0]
        long_arg = arg[1]
        default = arg[2]
        if not isinstance(default, bool):
            short_arg += ':'
            long_arg += '='
        s_args += short_arg
        l_args.append(long_arg)
    # Get command line options
    cli_opts = {}
    try:
        opts, _ = getopt.getopt(sys.argv[1:], s_args, l_args)
        for opt, arg in opts:
            cli_opts[opt] = arg
    except getopt.GetoptError as err:
        print(err)
        exit(2)
    arg_values = []
    for arg in args:
        short_arg = '-' + arg[0]
        long_arg = '--' + arg[1]
        default = arg[2]
        if len(arg) >= 4:
            arg_type = arg[3]
        else:
            arg_type = type(arg[2])
        key = ''
        if short_arg in cli_opts:
            key = short_arg
        elif long_arg in cli_opts:
            key = long_arg
        if key:
            if arg_type is bool:
                arg_values.append(not default)
            else:
                arg_values.append(arg_type(cli_opts[key]))
        else:
            arg_values.append(default)
    if len(arg_values) == 1:
        return arg_values[0]
    return arg_values
