sync:
	rsync -av --exclude  ".github" --exclude "experiments" --exclude  ".venv"  --exclude  ".git" --exclude "rlcard/models/pretrained"  . chauhm@train-bot:/home/chauhm/rlcard/