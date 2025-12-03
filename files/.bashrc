# for nodes of this type, we don't define module or slurm
if [[ $SLURM_JOB_PARTITION == 'cip101-' ]]; then
	export HOSTNAME=monordi
	export HOME=/home/$USER/.monordi
	export PS1="[\u@monordi \W]$ "
	mkdir -p "$HOME/Mes Documents"
	cd .monordi
	touch "$HOME/Mes Documents/document.txt"
	export PATH=/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin
	unset module
else
	source /cvmfs/soft.computecanada.ca/config/profile/bash.sh
	squeue() {
	        /opt/software/slurm/bin/squeue $@ | grep --color=auto -v spawner-jupyte
	}

	sq() {
	        /opt/software/slurm/bin/squeue -u $USER $@ | grep --color=auto -v spawner-jupyte
	}

	export SALLOC_PARTITION="nodepool"
fi


