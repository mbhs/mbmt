#/bin/zsh
tmux split-window -h
tmux send-keys -t 2 'source venv/bin/activate' Enter
tmux send-keys -t 2 'python manage.py runserver' Enter
tmux send-keys -t 1 'nvim' Enter
tmux resize-pane -t 1 -Z
