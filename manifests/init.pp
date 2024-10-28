class cqedu {
  Yumrepo<| tag == 'epel' |> -> Package<| tag == 'restic' |>
  Restic::Repository<| |> -> Exec<| tag == tutor |>

  exec { 'systemctl start restic_restore_restore_edx_repo':
    unless  => 'ls /backups/prod',
    require => Restic::Repository['restore_edx_repo'],
    before  => Package['tutor'],
    path    => ['/bin', '/usr/bin']
  }
}
