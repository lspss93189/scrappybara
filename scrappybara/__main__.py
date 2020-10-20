if __name__ == "__main__":
    import sys
    from scrappybara.cli.download import download

    commands = {
        'download': download,
    }

    if len(sys.argv) == 1:
        print('Available commands:', ', '.join(commands))
    command = sys.argv.pop(1)
    if command in commands:
        commands[command]()
    else:
        print('Available commands:', ', '.join(commands))
