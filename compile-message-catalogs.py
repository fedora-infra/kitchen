#!/usr/bin/python -tt

import ConfigParser
import glob
import os
import shutil

import babel.messages.frontend

if __name__ == '__main__':
    # Get the directory with message catalogs
    # Reuse transifex's config file first as it will know this
    cfg = ConfigParser.SafeConfigParser()
    cfg.read('.tx/config')
    babel_cmd = babel.messages.frontend.CommandLineInterface()
    try:
        shutil.rmtree('locale')
    except OSError, e:
        # If the error is that locale does not exist, we're okay.  We're
        # deleting it here, afterall
        if e.errno != 2:
            raise

    for section in (s for s in cfg.sections() if s != 'main'):
        try:
            file_filter = cfg.get(section, 'file_filter')
        except ConfigParser.NoOptionError:
            pass
        glob_pattern = file_filter.replace('<lang>', '*')
        compile_args = ['pybbel', 'compile', '-D', 'kitchen', '-d', 'locale', '-i', '<lang>.po', '-l', '<lang>']
        for po_file in glob.glob(glob_pattern):
            file_pattern = os.path.basename(po_file)
            lang = file_pattern.replace('.po','')
            compile_args[7] = po_file
            compile_args[9] = lang
            os.makedirs(os.path.join('locale', lang, 'LC_MESSAGES'))
            print compile_args
            babel_cmd.run(compile_args)
