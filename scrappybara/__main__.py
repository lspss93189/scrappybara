if __name__ == "__main__":
    import sys
    from scrappybara.cli.extract_classes import extract_classes
    from scrappybara.cli.extract_items import extract_items
    from scrappybara.cli.extract_forms import extract_forms
    from scrappybara.cli.extract_bags import extract_bags
    from scrappybara.cli.push_data import push_data
    from scrappybara.cli.download import download
    from scrappybara.cli.build_langmodel import build_langmodel

    commands = {
        'build_langmodel': build_langmodel,
        'extract_classes': extract_classes,
        'extract_items': extract_items,
        'extract_forms': extract_forms,
        'extract_bags': extract_bags,
        'push_data': push_data,
        'download': download,
    }

    if len(sys.argv) == 1:
        print('Available commands:', ', '.join(commands))
    command = sys.argv.pop(1)
    if command in commands:
        commands[command](*sys.argv[1:])
    else:
        print('Available commands:', ', '.join(commands))
