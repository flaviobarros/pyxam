# Author: Eric Buss <ebuss@ualberta.ca> 2016
import os
import process_list
import filters
from subprocess import call
from subprocess import check_output
import formatter
import fileutil
import options
import plugin_loader

# TODO move functions to lib_loader
# TODO cleanup
# TODO DVI support


plugin = {
    'name': 'pdf support',
    'author': 'ejrbuss',
    'description': 'pdf export support for LaTeX documents'
}


def error():
    raise plugin_loader.PluginError('This format is only for output!')


compile_format = ''


def load():
    # Add dummy pdf format
    formatter.add_format({
        'extensions': ['pdf', 'pdf'],
        'description': 'pdf export support',
        'parser_preprocessor': error,
        'parser_postprocessor': error,
        'composer_preprocessor': error,
        'composer_postprocessor': error,
        'format': {}
    })
    # Add dummy dvi format
    formatter.add_format({
        'extensions': ['dvi', 'dvi'],
        'description': 'dvi export support',
        'parser_preprocessor': error,
        'parser_postprocessor': error,
        'composer_preprocessor': error,
        'composer_postprocessor': error,
        'format': {}
    })
    # Add bypass
    process_list.run_before('weave', pdf_bypass)
    # Add recompilation option
    options.add_option('recomps', '-r', 'The number of LaTeX recompilations',  1, int)
    return plugin


def pdf_bypass():
    """
    Bypass formatter steps
    :return:
    """
    global compile_format
    if options.state.format() == 'pdf':
        compile_format = 'pdf'
        options.state.format('tex')
        process_list.run_after('export', pdf_compile)
    if options.state.format() == 'dvi':
        compile_format = 'dvi'
        options.state.format('tex')
        process_list.run_after('export', pdf_compile)


def pdf_compile():
    """
    Compile to pdf or dvi
    :return:
    """
    options.state.format(compile_format)
    os.path.curdir = options.state.out()
    for file in fileutil.with_extension('.tex'):
        if compile_format == 'dvi':
            fileutil.write(file, '%&latex\n' + fileutil.read(file))
        for i in range(options.state.recomps()):
            try:
                with open(os.devnull, 'r') as stdin:
                    check_output(['pdflatex', '-shell-escape', file], stdin=stdin, cwd=options.state.out())
                check_compiled(['pdf', 'dvi'], file)
            except:
                print('Failed to compile latex file: ' + file)
                print('Running pdflatex in interactive mode...')
                call(['pdflatex', '-shell-escape', file], cwd=options.state.out())
    for file in fileutil.with_extension('.aux'):
        fileutil.remove(file)
    for file in fileutil.with_extension('.log'):
        fileutil.remove(file)
    return


def check_compiled(extensions, file):
    """
    Check that a file with file compiled to one of the specified extensions. If the file does not compile it is
    recompiled in interactive mode
    :param extensions: The extensions to look for
    :param file: The original file
    :return: None
    """
    compiled = False
    for extension in extensions:
        compiled = compiled or os.path.isfile(file[:-3] + extension)
    if not compiled:
        print('Failed to compile latex file: ' + file)
        print('Running pdflatex in interactive mode...')
        call(['pdflatex', '-shell-escape', file], cwd=options.state.out())


def unload():
    pass



