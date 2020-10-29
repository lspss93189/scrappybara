if __name__ == "__main__":
    import sys
    from scrappybara.cli.download import download
    from scrappybara.cli.extract_items import extract_items

    commands = {
        'download': download,
        'extract_items': extract_items,
    }

    if len(sys.argv) == 1:
        print('Available commands:', ', '.join(commands))
    command = sys.argv.pop(1)
    if command in commands:
        commands[command](*sys.argv[1:])
    else:
        print('Available commands:', ', '.join(commands))
