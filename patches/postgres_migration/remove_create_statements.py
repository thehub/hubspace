from re import sub, compile, I, M

def remove_create_statements():
    dump = open('./hubdata2.dump', 'r+');
    text = dump.read()
    dump.close()

    #remove the table create statements
    tables = compile('^CREATE TABLE[a-zA-Z0-9\s\n\(\),_\'\"]*;\n', I | M)
    text = tables.sub('', text)

    single_backslash = compile(r"(\\)([^\\]+)", M)
    text = single_backslash.sub("\\\\\\\\\\2", text)

    dump = file('/tmp/postgres_compatible.dump', 'w+')
    dump.write(text)
    dump.close()

