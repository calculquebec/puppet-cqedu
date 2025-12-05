# for nodes of this type, we don't define module or slurm
hostname=$(hostname -f)
if [[ $hostname == evolo1* && $- == *i* ]]; then
	/home/.skel/.fakepass || exit
fi

if [[ $SLURM_JOB_PARTITION == 'cip101-' ]]; then
	export HOSTNAME=monordi
	export HOME=/home/$USER/.monordi
	export PS1="[\u@monordi \W]$ "
	mkdir -p "$HOME/Documents"
	cd .monordi
	touch "$HOME/Documents/document.txt"
	export PATH=/cvmfs/soft.computecanada.ca/gentoo/2023/x86-64-v3/usr/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin
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


