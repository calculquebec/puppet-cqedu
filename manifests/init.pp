class cqedu {
  #Yumrepo['epel'] -> Package<| tag == Restic::Package |>
  exec { 'systemctl start restic_restore_restore_edx_repo':
    unless  => 'ls /backups/prod',
    require => Restic::Repository['restore_edx_repo'],
    before  => Package['tutor'],
    path    => ['/bin', '/usr/bin']
  }
}