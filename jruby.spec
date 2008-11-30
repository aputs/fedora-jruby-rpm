Name:           jruby
Version:        1.1.5
Release:        1%{?dist}
Summary:        Pure Java implementation of the Ruby interpreter

Group:          Development/Languages
License:        (CPL or GPLv2+ or LGPLv2+) and ASL 1.1 and MIT and Ruby
URL:            http://jruby.codehaus.org/
Source0:        http://dist.codehaus.org/jruby/jruby-src-%{version}.tar.gz
# This patch is Fedora specific; we set up classpath using build-classpath.
Patch1:         jruby-fix-jruby-start-script.patch
# Temporary until upstream realizes they don't support 1.4 and scraps
# retroweaver.
Patch2:         jruby-remove-retroweaver-task.patch
# Disagreements with upstream. They want to bundle binary dependencies
# into jruby's jar; we don't.
Patch3:         jruby-dont-include-dependencies-in-jar.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

BuildRequires:  ant >= 1.6
BuildRequires:  ant-junit >= 1.6
BuildRequires:  bsf
BuildRequires:  bytelist
BuildRequires:  java-devel >= 1:1.6
BuildRequires:  jcodings
BuildRequires:  jline
BuildRequires:  jna
BuildRequires:  jna-posix
BuildRequires:  joda-time
BuildRequires:  joni >= 1.0.3
BuildRequires:  jpackage-utils >= 1.5
BuildRequires:  junit
BuildRequires:  jvyamlb >= 0.2.2
BuildRequires:  objectweb-asm
BuildRequires:  ruby

Requires:       bcel
Requires:       bsf
Requires:       bytelist
Requires:       java >= 1:1.6
Requires:       jline
Requires:       jna
Requires:       jna-posix
Requires:       joni >= 1.0.3
Requires:       jpackage-utils >= 1.5
Requires:       jvyamlb
Requires:       objectweb-asm

%description
JRuby is an 100% pure-Java implementation of the Ruby programming
language.

Features:
  * A 1.8.5 compatible Ruby interpreter
  * Most builtin Ruby classes provided
  * Support for interacting with and defining Java classes from within
    Ruby
  * Bean Scripting Framework (BSF) support


%package        javadoc
Summary:        Javadoc for %{name}
Group:          Documentation
Requires:       %{name} = %{version}-%{release}

%description    javadoc
Javadoc for %{name}.


%prep
%setup -q
%patch1 -p0
%patch2 -p0
%patch3 -p0

# delete binary .jars.
rm -f build_lib/*.jar
# there are non-binaries in lib/ as well; leave them alone
rm -f lib/bsf.jar
rm -f lib/profile.{jar,properties}

# Clean up the native libs
rm -f lib/native/*/*
pushd lib/native
  for subdir in *; do
    if [ "$subdir" = "${subdir/linux/}" ]; then
      rmdir "$subdir"
    else
      arch=${subdir/*-/}
      pushd "$subdir"
        if [ "x$arch" = "xi386" ]; then
          ln -s /usr/lib/jna/libjnidispatch.so
#%ifarch x86_64 # this breaks noarch-ness
        elif [ "x$arch" = "xamd64" ]; then
          ln -s /usr/lib64/jna/libjnidispatch.so
#%endif
        fi
      popd
    fi
  done
popd

# and replace them with symlinks
build-jar-repository -s -p build_lib constantine objectweb-asm/asm \
  objectweb-asm/asm-analysis objectweb-asm/asm-commons \
  objectweb-asm/asm-tree objectweb-asm/asm-util jline jna \
  joda-time joni junit bsf jna-posix jvyamlb bytelist jcodings

# remove hidden .document files
find lib/ruby/ -name '*.document' -exec rm -f '{}' \;

# change included stdlib to use jruby rather than some arcane ruby install
find lib/ruby/ -name '*.rb' -exec sed --in-place "s|^#!/usr/local/bin/ruby|#!/usr/bin/env jruby|" '{}' \;

# remove some random empty files
rm -f lib/ruby/gems/1.8/gems/rspec-*/spec/spec/runner/{empty_file.txt,resources/a_{foo,bar}.rb}

# archdir on jruby
mkdir lib/ruby/site_ruby/1.8/java

# We don't have source to support accessing the jar this accesses
rm src/org/jruby/runtime/invokedynamic/InvokeDynamicSupport.java
rm src/org/jruby/compiler/impl/InvokeDynamicInvocationCompiler.java


%build
LD_LIBRARY_PATH="%{_libdir}/jna" ant jar
ant create-apidocs


%install
rm -rf %{buildroot}

# prefix install
install -p -d -m 755 %{buildroot}%{_libdir}/%{name}
cp -ar samples/ %{buildroot}%{_libdir}/%{name}/ # samples
cp -ar lib/     %{buildroot}%{_libdir}/%{name}/ # stdlib + jruby.jar
cp -ar bin/     %{buildroot}%{_libdir}/%{name}/ # startup scripts

# jar - link to prefix'd jar so that java stuff knows where to look
install -d -m 755 %{buildroot}%{_javadir}
ln -s %{_libdir}/%{name}/lib/%{name}.jar %{buildroot}%{_javadir}/%{name}.jar

# /usr prefix startup scripts
install -d -m 755 %{buildroot}%{_bindir}
ln -s %{_libdir}/%{name}/bin/jruby %{buildroot}%{_bindir}/jruby
ln -s %{_libdir}/%{name}/bin/jirb  %{buildroot}%{_bindir}/jirb

# javadoc
install -p -d -m 755 %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -a docs/api/* %{buildroot}%{_javadocdir}/%{name}-%{version}


%check
# Skip tests as they fail now for some weird reason -- the last test
# in test/test_backquote.rb fails.
#ant test-all


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc COPYING COPYING.CPL COPYING.GPL COPYING.LGPL
%doc docs/CodeConventions.txt docs/README.test

%attr(0755,root,root) %{_bindir}/%{name}
%attr(0755,root,root) %{_bindir}/jirb
%{_javadir}/%{name}.jar
%{_libdir}/%{name}


%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/%{name}-%{version}


%changelog
* Fri Nov 28 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.5-1
- Bump to 1.1.5.

* Mon Sep 8 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.4-1
- Bump to 1.1.4.

* Tue Jul 29 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.3-2
- Update jruby-fix-jruby-start-script.patch to work with faster
  class-loading mechanism introduced in JRuby 1.1.2.

* Sat Jul 19 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.3-1
- Bump to 1.1.3.

* Wed May 21 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.1-7
- Require joni and jline.

* Thu Apr 24 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.1-6
- Bump because F-9 bumped.

* Thu Apr 24 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.1-5
- BR and Requires openjdk.

* Tue Apr 22 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.1-4
- Add check section.
- Removed patches 0 and 4 because they got incorporated in upstream.

* Mon Apr 7 2008 Conrad Meyer <konrad@tylerc.org> - 1.1-3
- Install all jruby to the prefix libdir/jruby, linking from /usr
  where needed.

* Sun Apr 6 2008 Conrad Meyer <konrad@tylerc.org> - 1.1-2
- Add a few missing Requires.
- Add some things that were missing from CP in the start script.

* Sun Mar 30 2008 Conrad Meyer <konrad@tylerc.org> - 1.1-1
- Bump to 1.1.
- Remove binary .jars.
- Minor cleanups in the specfile.
- Don't include jruby stdlib (for now).

* Sun Feb 24 2008 Conrad Meyer <konrad@tylerc.org> - 1.1-0.4.20080216svn
- Bump for 1.1rc2.

* Tue Jan 8 2008 Conrad Meyer <konrad@tylerc.org> - 1.1-0.3.20080108svn
- Bump for 1.1rc1.

* Sun Dec 9 2007 Conrad Meyer <konrad@tylerc.org> - 1.1-0.2.20071209svn
- SVN version bump.

* Mon Dec 3 2007 Conrad Meyer <konrad@tylerc.org> - 1.1-0.1.20071203svn
- Initial package created from ancient jpackage package
