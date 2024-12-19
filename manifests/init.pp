class cqedu (
  Boolean $patch_domain_before_restore = false,
) {
  $tutor_user = 'tutor'
  $tutor_backup_dir = "/${tutor_user}/.local/share/tutor/env/backup/"

  Yumrepo<| tag == 'epel' |> -> Package<| tag == 'restic' |>
  Restic::Repository<| |> -> Exec<| tag == tutor |>

  # ensure at least one restore is done when restic is first configured
  exec { 'systemctl start restic_restore_restore_edx_repo':
    unless  => 'ls /backups/prod',
    require => Restic::Repository['restore_edx_repo'],
    before  => Class['tutor'],
    path    => ['/bin', '/usr/bin']
  }
  exec { 'systemctl start restic_restore_restore_edx_dev_repo':
    unless  => 'ls /backups/dev',
    require => Restic::Repository['restore_edx_dev_repo'],
    before  => Class['tutor'],
    path    => ['/bin', '/usr/bin']
  }

  if $patch_domain_before_restore {
    $backup_to_restore = lookup('tutor::backup_to_restore')

    $date = $backup_to_restore['date']
    $path = $backup_to_restore['path']
    $filename = "backup.${date}.tar.xz"

    exec { "tar xf ${path}/${filename} -C /tmp && sed -i -e 's/edu.calculquebec.cloud/edu-dev.calculquebec.cloud/g' /tmp/data/mysql_dump.sql && cd /tmp && tar cfJ ${path}/${filename} data && rm -rf /tmp/data":
      unless      => "grep -w ${date} /${tutor_user}/.backup_restored",
      before      => Exec["cp ${path}/${filename} ${tutor_backup_dir}"],
      require     => [Exec['systemctl start restic_restore_restore_edx_repo'], Exec['systemctl start restic_restore_restore_edx_dev_repo'], File[$tutor_backup_dir], Tutor::Plugin['backup']],
      path => ['/bin/', '/usr/bin'],
    }
  }
}
