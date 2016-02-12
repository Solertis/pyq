import click
import os

from .astmatch import ASTMatchEngine
from pygments import highlight
from pygments.lexers.python import PythonLexer
from pygments.formatters.terminal import TerminalFormatter


@click.command()
@click.argument('selector')
@click.option('-l/--files', is_flag=True,
              help='Only print filenames containing matches.')
@click.argument('path', nargs=-1)
@click.pass_context
def main(ctx, selector, path, **opts):
    m = ASTMatchEngine()

    if len(path) == 0:
        path = ['.']

    for fn in walk_files(ctx, path):
        if fn.endswith('.py'):
            display_matches(m, selector, os.path.relpath(fn), opts)


def walk_files(ctx, paths):
    for i, p in enumerate(paths):
        p = click.format_filename(p)

        if p == '.' or os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                for fn in files:
                    yield os.path.join(root, fn)

        elif os.path.exists(p):
            yield p

        elif i == 0:
            ctx.fail('{}: No such file or directory'.format(p))
            break


def display_matches(m, selector, filename, opts):
    matches = matching_lines(m.match(selector, filename), filename)

    if opts.get('l'):
        files = {}
        for line, no in matches:
            if opts.get('l'):
                if filename not in files:
                    click.echo(filename)
                    # do not repeat files
                    files[filename] = True

    else:
        for line, no in matches:
            text = highlight(line.strip(), PythonLexer(), TerminalFormatter())
            output = '{}:{}  {}'.format(filename, no, text)
            click.echo(output, nl=False)


def matching_lines(matches, filename):
    fp = None
    for match, lineno in matches:
        if fp is None:
            fp = open(filename, 'rb')
        else:
            fp.seek(0)

        i = 1
        while True:
            line = fp.readline()

            if not line:
                break

            if i == lineno:
                text = line.decode('utf-8')
                yield text, lineno
                break

            i += 1

    if fp is not None:
        fp.close()


if __name__ == '__main__':
    main()
