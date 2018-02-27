Name: python-docutils
Summary: A Python Document Utilities
Version: 0.14
Release: 0
Group: Development/Languages/Python
License: BSD-3-Clause
Source0: %{name}-%{version}.tar.gz
Source1001: %{name}.manifest

BuildRequires:  python-devel
BuildRequires:  python-nose
BuildRequires:  python-xml
Requires:       python-xml
Provides:       python-docutil

%description
Docutils is a modular system for processing documentation into useful formats,
such as HTML, XML, and LaTeX. For input Docutils supports reStructuredText, an
easy-to-read, what-you-see-is-what-you-get plaintext markup syntax.

%prep
%setup -q
cp %{SOURCE1001} .
# Remove useless ".py" ending from executables:
for i in tools/rst*; do mv "$i" "${i/.py}"; done
sed -i "s|'tools/\(rst.*\)\.py'|'tools/\1'|" setup.py
# Remove shebang from non-executable files
for i in {'code_analyzer','error_reporting','punctuation_chars','smartquotes','math/latex2mathml','math/math2html','math/tex2mathml_extern'}; do
    sed -i -e "1d" "docutils/utils/$i.py"
done
sed -i -e "1d" "docutils/writers/xetex/__init__.py" "docutils/writers/_html_base.py"

%build
%{__python} setup.py build

%install
python setup.py install --prefix=%{_prefix} --root=%{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%manifest %{name}.manifest
%{_bindir}/rst2html
%{_bindir}/rst2html4
%{_bindir}/rst2html5
%{_bindir}/rst2latex
%{_bindir}/rst2man
%{_bindir}/rst2odt
%{_bindir}/rst2odt_prepstyles
%{_bindir}/rst2pseudoxml
%{_bindir}/rst2s5
%{_bindir}/rst2xetex
%{_bindir}/rst2xml
%{_bindir}/rstpep2html
%{python_sitelib}/docutils/
%{python_sitelib}/docutils-%{version}-py%{python_version}.egg-info

%changelog
* Tue Feb 27 2018 Jijoong Moon <jijoong.moon@samsung.com>
- Initial import
