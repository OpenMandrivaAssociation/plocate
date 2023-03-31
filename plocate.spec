Summary:	Much faster locate
Name:		plocate
Version:	1.1.18
Release:	2
License:	GPLv2+
URL:		https://plocate.sesse.net/
Source0:	https://plocate.sesse.net/download/%{name}-%{version}.tar.gz
Source1:	%{name}.sysusers
Source2:	updatedb.conf
BuildRequires:	meson
BuildRequires:	systemd-rpm-macros
BuildRequires:	pkgconfig(liburing)
BuildRequires:	pkgconfig(libzstd)
Requires(pre):	systemd
%systemd_requires
%rename	mlocate

%description
plocate is a locate(1) based on posting lists, giving much faster
searches on a much smaller index. It is a drop-in replacement for
mlocate in nearly all aspects, and is fast on SSDs and non-SSDs alike.

%prep
%autosetup -p1

%build
%meson -Dsystemunitdir=%{_unitdir} -Dinstall_systemd=true
%meson_build

# Man page alias
cat >locate.1 <<EOF
.so man1/%{name}.1
EOF

%install
%meson_install

install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_sysusersdir}/%{name}.conf
install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/updatedb.conf
ln -s %{name} %{buildroot}%{_bindir}/locate
install -p -D -m 0644 -t %{buildroot}%{_mandir}/man1/ locate.1

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-%{name}.preset << EOF
enable %{name}-updatedb.timer
EOF

%pre
%sysusers_create_package %{name} %{SOURCE1}

%post
%systemd_post %{name}-updatedb.service %{name}-updatedb.timer

%preun
%systemd_preun %{name}-updatedb.service %{name}-updatedb.timer

%postun
%systemd_postun_with_restart %{name}-updatedb.service %{name}-updatedb.timer

%files
%license COPYING
%doc README
%config(noreplace) %{_sysconfdir}/updatedb.conf
%{_sysusersdir}/%{name}.conf
%attr(02755,-,plocate) %{_bindir}/%{name}
%{_bindir}/locate
%{_sbindir}/%{name}-build
%{_sbindir}/updatedb
%{_presetdir}/86-%{name}.preset
%{_unitdir}/%{name}-updatedb.*
%doc %{_mandir}/man1/*.1*
%doc %{_mandir}/man5/*.5*
%doc %{_mandir}/man8/*.8*
%dir %{_sharedstatedir}/%{name}
%{_sharedstatedir}/%{name}/CACHEDIR.TAG
%ghost %attr(0640,-,plocate) %verify(not md5 mtime) %{_sharedstatedir}/%{name}/%{name}.db
