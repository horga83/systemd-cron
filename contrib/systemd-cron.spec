# https://fedoraproject.org/wiki/Packaging:ScriptletSnippets#Systemd
# https://github.com/systemd/systemd/blob/42911a567dc22c3115fb3ee3c56a7dcfb034f102/src/core/macros.systemd.in

# "If your package includes one or more systemd units that need
# to be enabled by default on package installation,
# they must be covered by the Fedora preset policy."

Name:           systemd-cron
Version:        1.5.3
Release:        2
License:        MIT
Summary:        systemd units to provide cron daemon & anacron functionality
Url:            https://github.com/systemd-cron/systemd-cron/
Group:          System Environment/Base
Source:         https://github.com/systemd-cron/systemd-cron/archive/v%{version}.tar.gz
Provides:       cronie
Provides:       cronie-anacron
Conflicts:      cronie
Conflicts:      cronie-anacron
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Requires:       crontabs
Requires:       systemd

%description
Provides systemd units to run cron jobs in /etc/cron.hourly cron.daily
cron.weekly and cron.monthly directories, without having cron
or anacron installed.
It also provides a generator that dynamically translate /etc/crontab,
/etc/cron.d/* and user cronjobs in systemd units.

%pre
touch /run/crond.reboot

%preun
%systemd_preun cron.target

%post
# XXX this macro doesn't seems to do anything
%systemd_post cron.target
if [ $1 -eq 1 ] ; then
	systemctl daemon-reload
	systemctl enable cron.target
	systemctl start cron.target
fi

%postun
%systemd_postun_with_restart cron.target

%prep
%setup -q

%build
./configure --enable-persistent=yes --prefix=/usr --confdir=/etc --enable-boot=no
make

%install
make DESTDIR=$RPM_BUILD_ROOT install
sed -i '/Persistent=true/d' $RPM_BUILD_ROOT/usr/lib/systemd/system/cron-hourly.timer
mkdir -p $RPM_BUILD_ROOT/var/spool/cron
mkdir -p $RPM_BUILD_ROOT/etc/cron.d/
mkdir -p $RPM_BUILD_ROOT/etc/cron.weekly/
cat << EOF > $RPM_BUILD_ROOT/etc/cron.weekly/systemd-cron
#!/bin/sh
test -x /usr/bin/python3 || exit 0
test -x /lib/systemd-cron/remove_stale_stamps || exit 0
exec /lib/systemd-cron/remove_stale_stamps
EOF
mkdir -p $RPM_BUILD_ROOT/usr/lib/systemd/system-preset/
echo 'enable cron.target' > $RPM_BUILD_ROOT/usr/lib/systemd/system-preset/50-systemd-cron.preset

%files
%license LICENSE
%doc README.md CHANGELOG
%dir /etc/cron.d/
/etc/cron.weekly/
/usr/bin/crontab
/usr/lib/systemd-cron/mail_on_failure
/usr/lib/systemd-cron/boot_delay
/usr/lib/systemd-cron/remove_stale_stamps
/usr/lib/systemd/system-preset/50-systemd-cron.preset
/usr/lib/systemd/system/cron.target
/usr/lib/systemd/system/cron-weekly.service
/usr/lib/systemd/system/cron-update.path
/usr/lib/systemd/system/cron-monthly.timer
/usr/lib/systemd/system/cron-hourly.target
/usr/lib/systemd/system/cron-weekly.timer
/usr/lib/systemd/system/cron-monthly.service
/usr/lib/systemd/system/cron-weekly.target
/usr/lib/systemd/system/cron-failure@.service
/usr/lib/systemd/system/cron-daily.timer
/usr/lib/systemd/system/cron-daily.service
/usr/lib/systemd/system/cron-daily.target
/usr/lib/systemd/system/cron-hourly.service
/usr/lib/systemd/system/cron-update.service
/usr/lib/systemd/system/cron-hourly.timer
/usr/lib/systemd/system/cron-monthly.target
/usr/lib/systemd/system-generators/systemd-crontab-generator
%{_mandir}/man1/crontab.*
%{_mandir}/man5/crontab.*
%{_mandir}/man5/anacrontab.*
%{_mandir}/man7/systemd.cron.*
%{_mandir}/man8/systemd-crontab-generator.*
%dir /var/spool/cron
