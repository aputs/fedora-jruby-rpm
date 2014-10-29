%global jruby_vendordir %{_datadir}/%{name}/lib
%global jruby_sitedir %{_prefix}/local/share/%{name}/lib
%global rubygems_dir %{_datadir}/rubygems

#%%global preminorver dev
#%%global commit 4e93f318f3301cf99ed483522bf6a5d75253918b
%global release 0
%global enable_check 0

%global jar_deps \\\
     objectweb-asm/asm \\\
     objectweb-asm/asm-analysis \\\
     objectweb-asm/asm-commons \\\
     objectweb-asm/asm-tree \\\
     objectweb-asm/asm-util \\\
     bcprov \\\
     bcmail \\\
     bsf \\\
     bytelist \\\
     commons-logging \\\
     coro-mock \\\
     invokebinder \\\
     jansi \\\
     jarjar \\\
     jcodings \\\
     jffi \\\
     jline \\\
     jna \\\
     jnr-constants \\\
     jnr-enxio \\\
     jnr-ffi \\\
     jnr-netdb \\\
     jnr-posix \\\
     jnr-unixsocket \\\
     joda-time \\\
     joni \\\
     junit \\\
     jzlib \\\
     nailgun \\\
     felix/org.osgi.core \\\
     snakeyaml \\\
     yydebug

Name:           jruby
Version:        1.7.16.1
Release:        %{?preminorver:0.}%{release}%{?preminorver:.%{preminorver}}%{?dist}.1
Summary:        Pure Java implementation of the Ruby interpreter
Group:          Development/Languages
# (CPL or GPLv2+ or LGPLv2+) - JRuby itself
# BSD - some files under lib/ruby/shared
# (GPLv2 or Ruby) - Ruby 1.8 stdlib
# (BSD or Ruby) - Ruby 1.9 stdlib
License:        (CPL or GPLv2+ or LGPLv2+) and BSD and (GPLv2 or Ruby) and (BSD or Ruby)
URL:            http://jruby.org/
BuildArch:      noarch
%if 0%{?preminorver:1}
Source0:        https://github.com/%{name}/%{name}/archive/%{commit}/%{name}-%{commit}.tar.gz
%else
Source0:        https://s3.amazonaws.com/jruby.org/downloads/%{version}/%{name}-src-%{version}.tar.gz
%endif
### Patches for JRuby itself
# Adds $FEDORA_JAVA_OPTS, that is dynamically replaced by Fedora specific paths from the specfile
# This way we can use macros for the actual locations and not hardcode them in the patch
Patch0:         jruby-executable-add-fedora-java-opts-stub.patch
# Adds all the required jars to boot classpath
# We don't want any directories defined by JRuby, everything is taken from Fedora's rubygems
Patch6:         jruby-remove-rubygems-dirs-definition.patch
patch7:         jruby-ant-build-apidocs.patch

### Patches for tests
# UDP multicast test hangs
# http://jira.codehaus.org/browse/JRUBY-6758
Patch100:         jruby-skip-network-tests.patch

BuildRequires:  maven-local
BuildRequires:  apache-commons-logging
BuildRequires:  bouncycastle
BuildRequires:  bouncycastle-mail
BuildRequires:  bsf
BuildRequires:  bytelist >= 1.0.8
BuildRequires:  coro-mock
BuildRequires:  felix-osgi-core >= 1.4.0
BuildRequires:  invokebinder
BuildRequires:  jansi
BuildRequires:  jarjar
BuildRequires:  jline
BuildRequires:  jffi >= 1.0.10
BuildRequires:  jna
BuildRequires:  jnr-constants
BuildRequires:  jnr-enxio
BuildRequires:  jnr-ffi >= 0.5.10
BuildRequires:  jnr-netdb
BuildRequires:  jnr-posix >= 1.1.8
BuildRequires:  jnr-unixsocket
BuildRequires:  jzlib
BuildRequires:  joda-time
BuildRequires:  joni >= 1.1.2
BuildRequires:  jzlib
BuildRequires:  nailgun
BuildRequires:  objectweb-asm
BuildRequires:  snakeyaml
BuildRequires:  yydebug

# Java Requires
Requires:  java >= 1.4
Requires:  apache-commons-logging
Requires:  bouncycastle
Requires:  bouncycastle-mail
Requires:  bsf
Requires:  bytelist >= 1.0.8
Requires:  felix-osgi-core >= 1.4.0
Requires:  invokebinder
Requires:  jansi
Requires:  jcodings >= 1.0.1
Requires:  jffi >= 1.0.10
Requires:  jline
Requires:  jna
Requires:  jnr-constants
Requires:  jnr-enxio
Requires:  jnr-ffi >= 0.5.10
Requires:  jnr-netdb
Requires:  jnr-posix >= 1.1.8
Requires:  jnr-unixsocket
Requires:  joda-time
Requires:  joni >= 1.1.2
Requires:  jzlib
Requires:  nailgun
Requires:  objectweb-asm
Requires:  snakeyaml
Requires:  yydebug

# Other Requires
Requires:  jpackage-utils
Requires:  rubygems
Requires:  rubypick

Provides:  ruby(release) = 1.9.1
Provides:  ruby(release) = 1.8
# For rubypick
Provides:  ruby(runtime_executable)

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

%package        devel
Summary:        JRuby development environment
Group:          Development/Languages
Requires:       jruby
Requires:       jpackage-utils

%description    devel
Macros for building JRuby-specific libraries.

%prep
%setup -q -n %{name}-%{version}%{?preminorver:.%{preminorver}}

%patch0 -p1
%patch7 -p1

%patch100 -p1

# delete all embedded jars - don't delete test jars!
find -path './test' -prune -o -path './spec' -prune -o -type f -name '*.jar' -exec rm -f '{}' \;

# delete windows specific files
find -name '*.exe' -exec rm -f '{}' \;
find -name '*.dll' -exec rm -f '{}' \;
find -name '*.bat' -exec rm -f '{}' \;

# delete all vcs files
find -name .gitignore -exec rm -f '{}' \;
find -name .cvsignore -exec rm -f '{}' \;

# remove hidden .document files
find lib/ruby/ -name '*.document' -exec rm -f '{}' \;

# change included stdlib to use jruby rather than some arcane ruby install
find lib/ruby/ -name '*.rb' -exec sed --in-place 's|^#!/usr/local/bin/ruby|#!/usr/bin/env jruby|' '{}' \;

# lib/ruby scripts shouldn't contain shebangs as they are not executable on their own
find lib/ruby/ -name '*.rb' -exec sed --in-place 's|^#!/usr/local/bin/ruby||' '{}' \;
find lib/ruby/ -name '*.rb' -exec sed --in-place 's|^#!/usr/bin/env ruby||' '{}' \;

%build
ant
ant apidocs

%install
install -p -d -m 755 %{buildroot}%{_datadir}/%{name}/{bin,lib}
cp -ar lib/{ruby,jruby.jar} %{buildroot}%{_datadir}/%{name}/lib # stdlib + jruby.jar
cp -ar bin/{jruby,jrubyc,jgem,jirb} %{buildroot}%{_datadir}/%{name}/bin # startup scripts

# /usr prefix startup scripts
install -d -m 755 %{buildroot}%{_bindir}
ln -s %{_datadir}/%{name}/bin/jgem  %{buildroot}%{_bindir}/gem-jruby
ln -s %{_datadir}/%{name}/bin/jirb  %{buildroot}%{_bindir}/irb-jruby
ln -s %{_datadir}/%{name}/bin/jruby %{buildroot}%{_bindir}/jruby

## Fedora integration stuff
# modify the JRuby executable to contain Fedora specific paths redefinitons
# we need to modify jruby{,sh,bash} to be sure everything is ok
sed -i 's|$FEDORA_JAVA_OPTS|-Dvendor.dir.general=%{jruby_vendordir}\
                            -Dsite.dir.general=%{jruby_sitedir}\
                            -Dvendor.dir.rubygems=%{rubygems_dir}|' \
%{buildroot}%{_datadir}/%{name}/bin/jruby*

# install JRuby specific bits into system RubyGems
mkdir -p %{buildroot}%{rubygems_dir}/rubygems/defaults
cp -a lib/ruby/shared/rubygems/defaults/* %{buildroot}%{rubygems_dir}/rubygems/defaults
# Apply patch6 here to not break tests by changing the rubygems dirs
pushd %{buildroot}%{rubygems_dir}
patch -p4 < %{PATCH6}
popd

# Dump the macros into macros.jruby to use them to build other JRuby libraries.
mkdir -p %{buildroot}%{_sysconfdir}/rpm
cat >> %{buildroot}%{_sysconfdir}/rpm/macros.jruby << \EOF
%%jruby_libdir %%{_datadir}/%{name}/lib/ruby/1.9

# This is the general location for libs/archs compatible with all
# or most of the Ruby versions available in the Fedora repositories.
%%jruby_vendordir vendor_ruby
%%jruby_vendorlibdir %%{jruby_libdir}/%%{jruby_vendordir}
%%jruby_vendorarchdir %%{jruby_vendorlibdir}
EOF

# javadoc
install -p -d -m 755 %{buildroot}%{_javadocdir}/%{name}
##########cp -a docs/api/* %{buildroot}%{_javadocdir}/%{name}

# jruby
install -d -m 755 %{buildroot}%{_javadir}
ln -s ../../..%{_datadir}/%{name}/lib/%{name}.jar %{buildroot}%{_javadir}/%{name}.jar

# poms
mkdir -p $RPM_BUILD_ROOT%{_mavenpomdir}
cp -a pom.xml $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{name}-shared.pom
%add_maven_depmap JPP-%{name}-shared.pom
cp -a maven/jruby/pom.xml $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{name}.pom
%add_maven_depmap JPP-%{name}.pom %{name}.jar

%check
%if 0%{?enable_check}
ant test
%endif

%files -f .mfiles
%doc COPYING LICENSE.RUBY
%doc docs/CodeConventions.txt
%if 0%{?enable_check}
%doc docs/README.test
%endif

%{_bindir}/%{name}
%{_bindir}/gem-jruby
%{_bindir}/irb-jruby
%{_datadir}/%{name}
# exclude bundled gems
%exclude %{jruby_vendordir}/ruby/1.9/rdoc*
%exclude %{jruby_vendordir}/ruby/1.9/rake*
%exclude %{jruby_vendordir}/ruby/gems
# exclude all of the rubygems stuff
%exclude %{jruby_vendordir}/ruby/shared/*ubygems*
%exclude %{jruby_vendordir}/ruby/shared/rbconfig
# own the JRuby specific files under RubyGems dir
%{rubygems_dir}/rubygems/defaults/jruby.rb
%{_javadir}/%{name}.jar

%files javadoc
%doc COPYING LICENSE.RUBY
%doc samples
%{_javadocdir}/%{name}

%files devel
%config(noreplace) %{_sysconfdir}/rpm/macros.jruby

%changelog
* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.2-6.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Aug 22 2013 Vít Ondruch <vondruch@redhat.com> - 1.7.2-5
- Use relative symlinks for compatibility with recent Java packaging macros.
- Fix Ant compatibility.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Jul 11 2013 Orion Poplawski <orion@cora.nwra.com> - 1.7.2-3
- Install the correct poms correctly

* Mon Jul 08 2013 Orion Poplawski <orion@cora.nwra.com> - 1.7.2-2
- Fix pom install
- Remove shipped bouncycastle jars

* Tue Feb 26 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.2-1
- Update to JRuby 1.7.2.

* Fri Dec 07 2012 Bohuslav Kabrda <bkabrda@redhat.com> -1.7.1-2
- Included -devel subpackage with macros.jruby.
- Added missing Requires: jpackage-utils.
- Added a patch for sitedir path.

* Tue Dec 04 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.1-1
- Update to JRuby 1.7.1.
- Update license tags.
- Include licensing files in all independent RPMs generated from this SRPM.
- Exclude the forgotten gems directory from vendordir.

* Fri Nov 30 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.1-0.1.dev
- Update to JRuby 1.7.1.dev.
- Add missing R: and BR: apache-commons-logging

* Fri Nov 09 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-2
- Don't move stuff from build_lib, the issue with including files is solved by
using non-existing file in jruby.jar.zip.includes in build.xml.
- Add missing Requires: snakeyaml.

* Tue Oct 23 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-1
- Updated to JRuby 1.7.0.

* Thu Oct 11 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-0.3.RC2
- Updated to JRuby 1.7.0.RC2.
- Rename jirb and jgem to irb-jruby and gem-jruby.

* Thu Oct 04 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-0.2.RC1
- Use system RubyGems.
- Add path definition that brings JRuby closer to MRI.

* Mon Oct 01 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-0.1.RC1
- Updated to JRuby 1.7.0.RC1.

* Tue Sep 11 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-0.1.preview2
- Updated to JRuby 1.7.0.preview2.

* Thu May 17 2012 Vít Ondruch <vondruch@redhat.com> - 1.6.7.2-1
- Updated to JRuby 1.6.7.2.

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
