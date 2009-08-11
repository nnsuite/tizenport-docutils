#! /usr/bin/env python

# $Id$
# Author: engelbert gruber <grubert@users.sourceforge.net>
# Copyright: This module has been placed in the public domain.

"""
Tests for latex2e writer.
"""

from __init__ import DocutilsTestSupport

from docutils._compat import b

def suite():
    settings = {'use_latex_toc': 0}
    s = DocutilsTestSupport.PublishTestSuite('latex', suite_settings=settings)
    s.generateTests(totest)
    settings['use_latex_toc'] = 1
    s.generateTests(totest_latex_toc)
    settings['use_latex_toc'] = 0
    settings['sectnum_xform'] = 0
    s.generateTests(totest_latex_sectnum)
    settings['sectnum_xform'] = 1
    settings['use_latex_citations'] = 1
    s.generateTests(totest_latex_citations)
    return s

latex_head_prefix = b(
r"""% generated by Docutils <http://docutils.sourceforge.net/>
\documentclass[a4paper,english]{article}
\usepackage{babel}
%\usepackage[OT1]{fontenc}
\usepackage[latin1]{inputenc}
\usepackage{ifthen}
\usepackage{fixltx2e} % fix LaTeX2e shortcomings
""")

latex_requirements = b('')

latex_head = b(r"""
%%% User specified packages and stylesheets

%%% Fallback definitions for Docutils-specific commands
% hyperref (PDF hyperlinks):
\ifthenelse{\isundefined{\hypersetup}}{
  \usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}
}{}
""")

latex_requirements_table = b(r"""\usepackage{longtable}
\usepackage{array}
\setlength{\extrarowheight}{2pt}
\newlength{\DUtablewidth} % internal use in tables
""")

latex_requirements_graphicx = b("""\usepackage{graphicx}
""")


totest = {}
totest_latex_toc = {}
totest_latex_sectnum = {}
totest_latex_citations = {}

totest['url_chars'] = [
["http://nowhere/url_with%28parens%29",
latex_head_prefix + latex_requirements + latex_head + b(r"""
%%% Body
\begin{document}

\href{http://nowhere/url_with\%28parens\%29}{http://nowhere/url\_with\%28parens\%29}

\end{document}
""")],
]

totest['table_of_contents'] = [
# input
["""\
.. contents:: Table of Contents

Title 1
=======
Paragraph 1.

Title 2
-------
Paragraph 2.
""",
## # expected output
latex_head_prefix + latex_requirements + latex_head + b(r"""
%%% Body
\begin{document}
\subsubsection*{~\hfill Table of Contents\hfill ~%
  \phantomsection%
  \addcontentsline{toc}{section}{Table of Contents}%
  \label{table-of-contents}%
}
%
\begin{list}{}{}

\item \hyperref[title-1]{Title 1}
%
\begin{list}{}{}

\item \hyperref[title-2]{Title 2}

\end{list}

\end{list}


%___________________________________________________________________________

\section*{Title 1%
  \phantomsection%
  \addcontentsline{toc}{section}{Title 1}%
  \label{title-1}%
}

Paragraph 1.


%___________________________________________________________________________

\subsection*{Title 2%
  \phantomsection%
  \addcontentsline{toc}{subsection}{Title 2}%
  \label{title-2}%
}

Paragraph 2.

\end{document}
""")],

]

totest_latex_toc['no_sectnum'] = [
# input
["""\
.. contents::

first section
-------------
""",
## # expected output
latex_head_prefix + latex_requirements + latex_head + b(r"""
%%% Body
\begin{document}

\renewcommand{\contentsname}{Contents}
\tableofcontents



%___________________________________________________________________________

\section*{first section%
  \phantomsection%
  \addcontentsline{toc}{section}{first section}%
  \label{first-section}%
}

\end{document}
""")],
]

totest_latex_toc['sectnum'] = [
# input
["""\
.. contents::
.. sectnum::

first section
-------------
""",
## # expected output
latex_head_prefix + latex_requirements + latex_head + b(r"""
%%% Body
\begin{document}

\renewcommand{\contentsname}{Contents}
\tableofcontents



%___________________________________________________________________________

\section*{1~~~first section%
  \phantomsection%
  \addcontentsline{toc}{section}{1~~~first section}%
  \label{first-section}%
}

\end{document}
""")],
]


totest_latex_sectnum['no_sectnum'] = [
# input
["""\
some text

first section
-------------
""",
## # expected output
latex_head_prefix + latex_requirements + b(r"""\setcounter{secnumdepth}{0}
""") + latex_head + b(r"""
%%% Body
\begin{document}

some text


%___________________________________________________________________________

\section{first section%
  \label{first-section}%
}

\end{document}
""")],
]

totest_latex_sectnum['sectnum'] = [
# input
["""\
.. sectnum::

some text

first section
-------------
""",
## # expected output
latex_head_prefix + latex_requirements + latex_head + b(r"""
%%% Body
\begin{document}

some text


%___________________________________________________________________________

\section{first section%
  \label{first-section}%
}

\end{document}
""")],
]

totest_latex_citations['citations_with_underscore'] = [
# input
["""\
Just a test citation [my_cite2006]_.

.. [my_cite2006]
   The underscore is mishandled.
""",
## # expected output
latex_head_prefix + latex_requirements + latex_head + b(r"""
%%% Body
\begin{document}

Just a test citation \cite{my_cite2006}.

\begin{thebibliography}{my\_cite2006}
\bibitem[my\_cite2006]{my_cite2006}{
The underscore is mishandled.
}
\end{thebibliography}

\end{document}
""")],
]


totest_latex_citations['adjacent_citations'] = [
# input
["""\
Two non-citations: [MeYou2007]_[YouMe2007]_.

Need to be separated for grouping: [MeYou2007]_ [YouMe2007]_.

Two spaces (or anything else) for no grouping: [MeYou2007]_  [YouMe2007]_.

But a line break should work: [MeYou2007]_
[YouMe2007]_.

.. [MeYou2007] not.
.. [YouMe2007] important.
""",
## # expected output
latex_head_prefix + latex_requirements + latex_head + b(r"""
%%% Body
\begin{document}

Two non-citations: {[}MeYou2007{]}\_{[}YouMe2007{]}\_.

Need to be separated for grouping: \cite{MeYou2007,YouMe2007}.

Two spaces (or anything else) for no grouping: \cite{MeYou2007}  \cite{YouMe2007}.

But a line break should work: \cite{MeYou2007,YouMe2007}.

\begin{thebibliography}{MeYou2007}
\bibitem[MeYou2007]{MeYou2007}{
not.
}
\bibitem[YouMe2007]{YouMe2007}{
important.
}
\end{thebibliography}

\end{document}
""")],
]


totest['enumerated_lists'] = [
# input
["""\
1. Item 1.
2. Second to the previous item this one will explain

  a) nothing.
  b) or some other.

3. Third is 

  (I) having pre and postfixes
  (II) in roman numerals.
""",
# expected output
latex_head_prefix + latex_requirements + latex_head + b(r"""
%%% Body
\begin{document}
\newcounter{listcnt0}
\begin{list}{\arabic{listcnt0}.}
{
\usecounter{listcnt0}
\setlength{\rightmargin}{\leftmargin}
}

\item Item 1.

\item Second to the previous item this one will explain
\end{list}
%
\begin{quote}
\setcounter{listcnt0}{0}
\begin{list}{\alph{listcnt0})}
{
\usecounter{listcnt0}
\setlength{\rightmargin}{\leftmargin}
}

\item nothing.

\item or some other.
\end{list}

\end{quote}
\setcounter{listcnt0}{0}
\begin{list}{\arabic{listcnt0}.}
{
\usecounter{listcnt0}
\addtocounter{listcnt0}{2}
\setlength{\rightmargin}{\leftmargin}
}

\item Third is
\end{list}
%
\begin{quote}
\setcounter{listcnt0}{0}
\begin{list}{(\Roman{listcnt0})}
{
\usecounter{listcnt0}
\setlength{\rightmargin}{\leftmargin}
}

\item having pre and postfixes

\item in roman numerals.
\end{list}

\end{quote}

\end{document}
""")],
]

# BUG: need to test for quote replacing if language is de (ngerman).

totest['quote_mangling'] = [
# input
["""\
Depending on language quotes are converted for latex.
Expecting "en" here.

Inside literal blocks quotes should be left untouched
(use only two quotes in test code makes life easier for
the python interpreter running the test)::

    ""
    This is left "untouched" also *this*.
    ""

.. parsed-literal::

    should get "quotes" and *italics*.


Inline ``literal "quotes"`` should be kept.
""",
latex_head_prefix + latex_requirements_graphicx + latex_head + b(r"""
%%% Body
\begin{document}

Depending on language quotes are converted for latex.
Expecting ``en'' here.

Inside literal blocks quotes should be left untouched
(use only two quotes in test code makes life easier for
the python interpreter running the test):
%
\begin{quote}{\ttfamily \raggedright \noindent
"{}"\\
This~is~left~"untouched"~also~*this*.\\
"{}"
}
\end{quote}
%
\begin{quote}{\ttfamily \raggedright \noindent
should~get~"quotes"~and~\emph{italics}.
}
\end{quote}

Inline \texttt{literal "quotes"} should be kept.

\end{document}
""")],
]

totest['table_caption'] = [
# input
["""\
.. table:: Foo

   +-----+-----+
   |     |     |
   +-----+-----+
   |     |     |
   +-----+-----+
""",
latex_head_prefix + latex_requirements_table + latex_head + b(r"""
%%% Body
\begin{document}

\leavevmode
\setlength{\DUtablewidth}{\linewidth}
\begin{longtable}[c]{|p{0.075\DUtablewidth}|p{0.075\DUtablewidth}|}
\caption{Foo}\\
\hline
 &  \\
\hline
 &  \\
\hline
\end{longtable}

\end{document}
""")],
]

totest['table_class'] = [
# input
["""\
.. table::
   :class: borderless

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
   |  3  |  4  |
   +-----+-----+
""",
latex_head_prefix + latex_requirements_table + latex_head + b(r"""
%%% Body
\begin{document}

\leavevmode
\setlength{\DUtablewidth}{\linewidth}
\begin{longtable}[c]{p{0.075\DUtablewidth}p{0.075\DUtablewidth}}

1
 & 
2
 \\

3
 & 
4
 \\
\end{longtable}

\end{document}
""")],
]

# The "[" needs to be protected (otherwise it will be seen as an
# option to "\\", "\item", etc. ).

totest['brackett_protection'] = [
# input
["""\
::

  something before to get a end of line.
  [

  the empty line gets tested too
  ]
""",
latex_head_prefix + latex_requirements_graphicx + latex_head + b(r"""
%%% Body
\begin{document}
%
\begin{quote}{\ttfamily \raggedright \noindent
something~before~to~get~a~end~of~line.\\
{[}\\
~\\
the~empty~line~gets~tested~too\\
{]}
}
\end{quote}

\end{document}
""")],
]

totest['raw'] = [
[r""".. raw:: latex

   \noindent

A paragraph.

.. |sub| raw:: latex

   (some raw text)

Foo |sub|
same paragraph.
""",
latex_head_prefix + latex_requirements + latex_head + b(r"""
%%% Body
\begin{document}
\noindent
A paragraph.

Foo (some raw text)
same paragraph.

\end{document}
""")],
]

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
