import dsarv

def print_tokens(tokens):
    if not tokens:
        print("(no tokens)")
        return
    for t in tokens:
        # show token type and lexeme/value (if any) on its own line
        if t.value is not None:
            print(f"{t.type}: {t.value}")
        else:
            print(f"{t.type}")

def main():
    try:
        while True:
            text = input('DSArv > ')
            if not text:
                continue
            tokens, error = dsarv.run('<stdin>', text)
            if error:
                print(error.as_string())
            else:
                print_tokens(tokens)
    except (KeyboardInterrupt, EOFError):
        print('\nExiting.')

if __name__ == '__main__':
    main()