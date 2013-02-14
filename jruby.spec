%global yecht_commitversion 157cf13
%global yecht_dlversion 0.0.2-0-g157cf13
%global yecht_cluster olabini

Name:           jruby
Version:        1.6.3
Release:        5%{?dist}
Summary:        Pure Java implementation of the Ruby interpreter
Group:          Development/Languages
License:        (CPL or GPLv2+ or LGPLv2+) and ASL 1.1 and MIT and Ruby
URL:            http://jruby.org/
BuildArch:      noarch
Source0:        http://jruby.org.s3.amazonaws.com/downloads/%{version}/jruby-src-%{version}.tar.gz
Source1:        http://github.com/%{yecht_cluster}/yecht/tarball/0.0.2/%{yecht_cluster}-yecht-%{yecht_dlversion}.tar.gz
Patch1:         add-classpath-to-jruby-start-script.patch
Patch2:         dont-include-jar-dependencies-in-build-xml.patch
Patch3:         remove-invoke-dynamic-support.patch
Patch5:         jruby-dont-use-jruby-until-build-is-complete.patch

# this patch contains the following upstream change
# https://github.com/jruby/jruby/commit/6c1d41aedfde705c969abf10cf5384e2be69f10a
Patch6:         remove-builtin-yecht-jar.patch

Patch7:         yecht-only-build-bindings.patch

BuildRequires:  java-devel >= 1.6
BuildRequires:  jpackage-utils >= 1.5
BuildRequires:  ant >= 1.6
BuildRequires:  objectweb-asm
BuildRequires:  bytelist >= 1.0.8
BuildRequires:  jnr-constants
BuildRequires:  jline
BuildRequires:  jcodings >= 1.0.5
BuildRequires:  joni >= 1.1.2
BuildRequires:  jna
BuildRequires:  jnr-ffi >= 0.5.10
BuildRequires:  jffi >= 1.0.10
BuildRequires:  joda-time
BuildRequires:  yydebug
BuildRequires:  nailgun
BuildRequires:  emma
BuildRequires:  jgrapht
BuildRequires:  bsf
BuildRequires:  jnr-netdb
BuildRequires:  yecht
BuildRequires:  jakarta-commons-logging
BuildRequires:  jarjar
BuildRequires:  ant-junit
BuildRequires:  junit4
BuildRequires:  felix-osgi-core >= 1.4.0
BuildRequires:  snakeyaml
BuildRequires:  jnr-posix >= 1.1.8

# these normally get installed as gems during the test process
BuildRequires:  rubygem(rake)
BuildRequires:  rubygem(rspec-core)
BuildRequires:  rubygem(rspec-mocks)
BuildRequires:  rubygem(rspec-expectations)
BuildRequires:  rubygem(ruby-debug)
BuildRequires:  rubygem(ruby-debug-base)
BuildRequires:  rubygem(columnize)

Requires:  objectweb-asm
Requires:  bytelist >= 1.0.8
Requires:  jnr-constants
Requires:  jline
Requires:  jcodings >= 1.0.1
Requires:  joni >= 1.1.2
Requires:  jna
Requires:  jnr-ffi >= 0.5.10
Requires:  jffi >= 1.0.10
Requires:  joda-time
Requires:  yydebug
Requires:  nailgun
Requires:  emma
Requires:  jgrapht
Requires:  bsf
Requires:  jnr-netdb
Requires:  jruby-yecht
Requires:  jnr-posix >= 1.1.8


%description
JRuby is a 100% Java implementation of the Ruby programming language.
It is Ruby for the JVM. JRuby provides a complete set of core "builtin"
classes and syntax for the Ruby language, as well as most of the Ruby
Standard Libraries.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Documentation
Requires:       %{name} = %{version}-%{release}

%description    javadoc
Javadoc for %{name}.

# yecht / jruby bindings
# http://jira.codehaus.org/browse/JRUBY-5352
%package        yecht
Summary:        Bindings used to load yecht in jruby
Group:          Development/Libraries
BuildRequires:  yecht
Requires:       yecht
Requires:       %{name} = %{version}-%{release}

%description yecht
The bindings for the yecht library for internal use in jruby

%prep
%setup -q -n %{name}-%{version}
%patch1 -p0
%patch2 -p0
%patch3 -p0
%patch5 -p0
%patch6 -p0

tar xzvf %{SOURCE1}
mv %{yecht_cluster}-yecht-%{yecht_commitversion} yecht

# delete all embedded jars
find -name *.jar -exec rm -f '{}' \;

# delete windows specific files
find -name *.exe -exec rm -f '{}' \;
find -name *.dll -exec rm -f '{}' \;

# delete prebuilt gems in the build dir
rm build_lib/*.gem

# delete all vcs files
find -name .gitignore -exec rm -f '{}' \;
find -name .cvsignore -exec rm -f '{}' \;

# replace them with symlinks
build-jar-repository -s -p build_lib \
     objectweb-asm/asm objectweb-asm/asm-util \
     objectweb-asm/asm-commons objectweb-asm/asm-analysis objectweb-asm/asm-tree \
     bytelist constantine jline jcodings joni jna jaffl jffi joda-time  felix/org.osgi.core \
     yydebug nailgun emma jnr-posix jgrapht bsf jnr-netdb commons-logging jarjar junit junit4 \
     yecht snakeyaml emma_ant

# required as jruby was shipping the core java tools jar
ln -s /usr/lib/jvm/java/lib/tools.jar build_lib/apt-mirror-api.jar

# remove hidden .document files
find lib/ruby/ -name '*.document' -exec rm -f '{}' \;

# We don't have source to support accessing the jar this accesses
rm src/org/jruby/runtime/invokedynamic/InvokeDynamicSupport.java
rm src/org/jruby/compiler/impl/InvokeDynamicInvocationCompiler.java

# change included stdlib to use jruby rather than some arcane ruby install
#find lib/ruby/ -name '*.rb' -exec sed --in-place "s|^#!/usr/local/bin/ruby|#!/usr/bin/env jruby|" '{}' \;

# lib/ruby scripts shouldn't contain shebangs as they are not executable on their own
find lib/ruby/ -name '*.rb' -exec sed --in-place "s|^#!/usr/local/bin/ruby||" '{}' \;
find lib/ruby/ -name '*.rb' -exec sed --in-place "s|^#!/usr/bin/env ruby||" '{}' \;

# this file needs to be marked as executable for one of the tests to pass
chmod +x test/org/jruby/util/shell_launcher_test

# the yecht library needs to be accessible from ruby
pushd yecht
mkdir -p lib/ build/classes/ruby
%patch7 -p0

%build
ant
ant apidocs

# remove bat files
rm bin/*.bat

pushd yecht
ant ext-ruby-jar

%install
install -d -m 755 %{buildroot}%{_datadir}
install -p -d -m 755 %{buildroot}%{_datadir}/%{name}
cp -ar samples/ %{buildroot}%{_datadir}/%{name}/ # samples
cp -ar lib/     %{buildroot}%{_datadir}/%{name}/ # stdlib + jruby.jar
cp -ar bin/     %{buildroot}%{_datadir}/%{name}/ # startup scripts

ln -s %{_datadir}/%{name}/lib/%{name}.jar %{buildroot}%{_datadir}/%{name}.jar

# /usr prefix startup scripts
install -d -m 755 %{buildroot}%{_bindir}
ln -s %{_datadir}/%{name}/bin/jruby %{buildroot}%{_bindir}/jruby
ln -s %{_datadir}/%{name}/bin/jirb  %{buildroot}%{_bindir}/jirb

# javadoc
install -p -d -m 755 %{buildroot}%{_javadocdir}/%{name}
cp -a docs/api/* %{buildroot}%{_javadocdir}/%{name}

# jruby-yecht
install -d -m 755 %{buildroot}%{_javadir}
cp yecht/lib/yecht-ruby-0.0.2.jar %{buildroot}%{_datadir}/%{name}-yecht.jar
ln -s %{_datadir}/%{name}-yecht.jar %{buildroot}%{_javadir}/%{name}-yecht.jar

# pom
%add_to_maven_depmap org.jruby %{name} %{version} JPP %{name}
mkdir -p $RPM_BUILD_ROOT%{_mavenpomdir}
cp pom.xml  $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-java.pom

# java dir
install -d -m 755 %{buildroot}%{_javadir}
ln -s %{_datadir}/%{name}/lib/%{name}.jar %{buildroot}%{_javadir}/%{name}.jar

%check
#ant test

%files
%defattr(-,root,root,-)
%doc COPYING
%doc docs/CodeConventions.txt docs/README.test

%attr(0755,root,root) %{_bindir}/%{name}
%attr(0755,root,root) %{_bindir}/jirb
%{_datadir}/%{name}
%{_datadir}/%{name}.jar
%{_javadir}/%{name}.jar

%{_mavendepmapfragdir}/%{name}
%{_mavenpomdir}/*

%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/%{name}

%files yecht
%defattr(-,root,root,-)
%{_datadir}/%{name}-yecht.jar
%{_javadir}/%{name}-yecht.jar

%changelog
* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Mo Morsi <mmorsi@redhat.com> - 1.6.3-3
- rename jaffl dependency to jnr-ffi (BZ#723191)
- change build dep on rspec 1.x to 2.x

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Aug 02 2011 Mo Morsi <mmorsi@redhat.com> - 1.6.3-1
- update to latest upstream release
- include missing symlink to jruby-yecht

* Wed Jul 06 2011 Mo Morsi <mmorsi@redhat.com> - 1.6.2-2
- install jruby to _datadir not _javadir
- remove windows specific files (exes, dlls, etc)

* Wed May 25 2011 Mo Morsi <mmorsi@redhat.com> - 1.6.2-1
- Updated to latest upstream release

* Tue Dec 07 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.5.6-2
- Remove pre-built gems
- Started to add bits to get test suite in working order
- Added yecht bindings used internally in jruby

* Mon Dec 06 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.5.6-1
- Updated jruby to latest upstream release
- Updates to conform to pkging guidelines

* Thu Dec 02 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.5.5-1
- Updated jruby to latest upstream release

* Mon Oct 25 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.5.3-1
- Updated jruby to latest upstream release

* Thu Jan 28 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.4.0-1
- Unorphaned / updated jruby

* Fri Mar 6 2009 Conrad Meyer <konrad@tylerc.org> - 1.1.6-3
- debug_package nil, as this is a pure-java package (that can't
  be built with gcj).

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Dec 18 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.6-1
- Bump to 1.1.6.

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
