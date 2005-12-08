# Author: Chris Liechti
# Contact: cliechti@gmx.net
# Author: David Goodger
# Contact: goodger@python.org
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
S5/HTML Slideshow Writer.
"""

__docformat__ = 'reStructuredText'


import sys
import os
import docutils
from docutils import frontend, nodes, utils, writers
from docutils.writers import html4css1
from docutils.parsers.rst import directives

support_path = utils.relative_path(
    os.path.join(os.getcwd(), 'dummy'),
    os.path.join(writers.support_path, 's5_html'))

def find_theme(name):
    # Where else to look for a theme?
    # Check working dir?  Destination dir?  Config dir?  Plugins dir?
    path = os.path.join(support_path, name)
    if not os.path.isdir(path):
        raise docutils.ApplicationError('Theme directory not found: %r' % name)
    return path


class Writer(html4css1.Writer):

    settings_spec = html4css1.Writer.settings_spec + (
        'S5 Slideshow Specific Options',
        'For the S5/HTML writer, the --no-toc-backlinks option '
        '(defined in General Docutils Options above) is the default, '
        'and should not be changed.',
        (('Specify an installed S5 theme by name.  Overrides --theme-url.  '
          'The default theme name is "default".  The theme files will be '
          'copied into a "ui/<theme>" directory, in the same directory as the '
          'destination file (output HTML).  Note that existing theme files '
          'will not be overwritten (unless --overwrite-theme-files is used).',
          ['--theme'],
          {'default': 'default', 'metavar': '<name>',
           'overrides': 'theme_url'}),
         ('Specify an S5 theme URL.  The destination file (output HTML) will '
          'link to this theme; nothing will be copied.  Overrides --theme.',
          ['--theme-url'],
          {'metavar': '<URL>', 'overrides': 'theme'}),
         ('Allow existing theme files in the ``ui/<theme>`` directory to be '
          'overwritten.  The default is not to overwrite theme files.',
          ['--overwrite-theme-files'],
          {'action': 'store_true'}),
         ('Keep existing theme files in the ``ui/<theme>`` directory; do not '
          'overwrite any.  This is the default.',
          ['--keep-theme-files'],
          {'dest': 'overwrite_theme_files', 'action': 'store_false'}),
         ('Enable the current slide indicator ("1 / 15").  '
          'The default is to disable it.',
          ['--current-slide'],
          {'action': 'store_true'}),
         ('Disable the current slide indicator.  This is the default.',
          ['--no-current-slide'],
          {'dest': 'current_slide', 'action': 'store_false'}),))

    settings_default_overrides = {'toc_backlinks': 0}

    config_section = 's5_html writer'
    config_section_dependencies = ('writers', 'html4css1 writer')

    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = S5HTMLTranslator


class S5HTMLTranslator(html4css1.HTMLTranslator):

    doctype = (
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"'
        ' "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')

    s5_stylesheet_template = """\
<!-- configuration parameters -->
<meta name="defaultView" content="slideshow" />
<meta name="controlVis" content="hidden" />
<!-- style sheet links -->
<link rel="stylesheet" href="%(path)s/slides.css"
      type="text/css" media="projection" id="slideProj" />
<link rel="stylesheet" href="%(path)s/outline.css"
      type="text/css" media="screen" id="outlineStyle" />
<link rel="stylesheet" href="%(path)s/print.css"
      type="text/css" media="print" id="slidePrint" />
<link rel="stylesheet" href="%(path)s/opera.css"
      type="text/css" media="projection" id="operaFix" />
<script src="%(path)s/slides.js" type="text/javascript"></script>\n"""

    disable_current_slide = """
<style type="text/css">
#currentSlide {display: none;}
</style>\n"""

    layout_template = """\
<div class="layout">
<div id="controls"></div>
<div id="currentSlide"></div>
<div id="header">
%(header)s
</div>
<div id="footer">
%(title)s%(footer)s
</div>
</div>\n"""
# <div class="topleft"></div>
# <div class="topright"></div>
# <div class="bottomleft"></div>
# <div class="bottomright"></div>

    default_theme = 'default'
    """Name of the default theme."""

    base_theme_file = '__base__'
    """Name of the file containing the name of the base theme."""

    direct_theme_files = (
        'slides.css', 'outline.css', 'print.css', 'opera.css', 'slides.js')
    """Names of theme files directly linked to in the output HTML"""

    indirect_theme_files = (
        's5-core.css', 'framing.css', 'pretty.css', 'blank.gif', 'iepngfix.htc')
    """Names of files used indirectly; imported or used by files in
    `direct_theme_files`."""

    required_theme_files = indirect_theme_files + direct_theme_files
    """Names of mandatory theme files."""

    def __init__(self, *args):
        html4css1.HTMLTranslator.__init__(self, *args)
        #insert S5-specific stylesheet and script stuff:
        self.theme_file_path = None
        self.setup_theme()
        self.stylesheet.append(self.s5_stylesheet_template
                               % {'path': self.theme_file_path})
        if not self.document.settings.current_slide:
            self.stylesheet.append(self.disable_current_slide)
        self.add_meta('<meta name="version" content="S5 1.1" />\n')
        self.s5_footer = []
        self.s5_header = []
        self.section_count = 0
        self.theme_files_copied = None

    def setup_theme(self):
        if self.document.settings.theme:
            self.copy_theme()
        elif self.document.settings.theme_url:
            self.theme_file_path = self.document.settings.theme_url
        else:
            raise docutils.ApplicationError(
                'No theme specified for S5/HTML writer.')

    def copy_theme(self):
        """
        Locate & copy theme files.

        A theme may be explicitly based on another theme via a '__base__'
        file.  The default base theme is 'default'.  Files are accumulated
        from the specified theme, any base themes, and 'default'.
        """
        settings = self.document.settings
        path = find_theme(settings.theme)
        theme_paths = [path]
        self.theme_files_copied = {}
        copied = {}
        # This is a link (URL) in HTML, so we use "/", not os.sep:
        self.theme_file_path = '%s/%s' % ('ui', settings.theme)
        if settings._destination:
            dest = os.path.join(
                os.path.dirname(settings._destination), 'ui', settings.theme)
            if not os.path.isdir(dest):
                os.makedirs(dest)
        else:
            # no destination, so we can't copy the theme
            return
        default = 0
        while path:
            for f in os.listdir(path):  # copy all files from each theme
                if f == self.base_theme_file:
                    continue            # ... except the "__base__" file
                if ( self.copy_file(f, path, dest)
                     and f in self.required_theme_files):
                    copied[f] = 1
            if default:
                break                   # "default" theme has no base theme
            # Find the "__base__" file in theme directory:
            base_theme_file = os.path.join(path, self.base_theme_file)
            # If it exists, read it and record the theme path:
            if os.path.isfile(base_theme_file):
                lines = open(base_theme_file).readlines()
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        path = find_theme(line)
                        if path in theme_paths: # check for duplicates (cycles)
                            path = None         # if found, use default base
                        else:
                            theme_paths.append(path)
                        break
                else:                   # no theme name found
                    path = None         # use default base
            else:                       # no base theme file found
                path = None             # use default base
            if not path:
                path = find_theme(self.default_theme)
                theme_paths.append(path)
                default = 1
        if len(copied) != len(self.required_theme_files):
            # Some all required files weren't found & couldn't be copied.
            required = list(self.required_theme_files)
            for f in copied.keys():
                required.remove(f)
            raise docutils.ApplicationError(
                'Theme files not found: %s'
                % ', '.join(['%r' % f for f in required]))

    def copy_file(self, name, source_dir, dest_dir):
        """
        Copy file `name` from `source_dir` to `dest_dir`.
        Return 1 if the file exists in either `source_dir` or `dest_dir`.
        """
        source = os.path.join(source_dir, name)
        dest = os.path.join(dest_dir, name)
        if self.theme_files_copied.has_key(dest):
            return 1
        else:
            self.theme_files_copied[dest] = 1
        if os.path.isfile(source):
            settings = self.document.settings
            if os.path.exists(dest) and not settings.overwrite_theme_files:
                settings.record_dependencies.add(dest)
            else:
                src_file = open(source, 'rb')
                src_data = src_file.read()
                src_file.close()
                dest_file = open(dest, 'wb')
                dest_file.write(src_data.replace(
                    'ui/default', dest_dir[dest_dir.rfind('ui/'):]))
                dest_file.close()
                settings.record_dependencies.add(source)
            return 1
        if os.path.isfile(dest):
            return 1

    def depart_document(self, node):
        header = ''.join(self.s5_header)
        footer = ''.join(self.s5_footer)
        title = ''.join(self.html_title).replace('<h1 class="title">', '<h1>')
        layout = self.layout_template % {'header': header,
                                         'title': title,
                                         'footer': footer}
        self.fragment.extend(self.body)
        self.body_prefix.extend(layout)
        self.body_prefix.append('<div class="presentation">\n')
        self.body_prefix.append(
            self.starttag({'classes': ['slide'], 'ids': ['slide0']}, 'div'))
        self.body_suffix.insert(0, '</div>\n')
        # skip content-type meta tag with interpolated charset value:
        self.html_head.extend(self.head[1:])
        self.html_body.extend(self.body_prefix[1:] + self.body_pre_docinfo
                              + self.docinfo + self.body
                              + self.body_suffix[:-1])

    def depart_footer(self, node):
        start = self.context.pop()
        self.s5_footer.append('<h2>')
        self.s5_footer.extend(self.body[start:])
        self.s5_footer.append('</h2>')
        del self.body[start:]

    def depart_header(self, node):
        start = self.context.pop()
        header = ['<div id="header">\n']
        header.extend(self.body[start:])
        header.append('\n</div>\n')
        del self.body[start:]
        self.s5_header.extend(header)

    def visit_section(self, node):
        if not self.section_count:
            self.body.append('\n</div>\n')
        self.section_count += 1
        self.section_level += 1
        if self.section_level > 1:
            # dummy for matching div's
            self.body.append(self.starttag(node, 'div', CLASS='section'))
        else:
            self.body.append(self.starttag(node, 'div', CLASS='slide'))

    def visit_subtitle(self, node):
        if isinstance(node.parent, nodes.section):
            level = self.section_level + self.initial_header_level - 1
            if level == 1:
                level = 2
            tag = 'h%s' % level
            self.body.append(self.starttag(node, tag, ''))
            self.context.append('</%s>\n' % tag)
        else:
            html4css1.HTMLTranslator.visit_subtitle(self, node)

    def visit_title(self, node, move_ids=0):
        html4css1.HTMLTranslator.visit_title(self, node, move_ids=move_ids)
