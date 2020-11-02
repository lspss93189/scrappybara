if __name__ == "__main__":
    import sys
    from scrappybara.cli.download import download
    from scrappybara.cli.extract_classes import extract_classes
    from scrappybara.cli.extract_items import extract_items
    from scrappybara.cli.extract_forms import extract_forms
    from scrappybara.cli.extract_lexeme_bags import extract_lexeme_bags
    from scrappybara.cli.create_vectors import create_vectors

    commands = {
        'download': download,
        'extract_classes': extract_classes,
        'extract_items': extract_items,
        'extract_forms': extract_forms,
        'extract_lexeme_bags': extract_lexeme_bags,
        'create_vectors': create_vectors,
    }

    if len(sys.argv) == 1:
        print('Available commands:', ', '.join(commands))
    command = sys.argv.pop(1)
    if command in commands:
        commands[command](*sys.argv[1:])
    else:
        print('Available commands:', ', '.join(commands))
