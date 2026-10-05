if status is-interactive
    # Commands to run in interactive sessions can go here
end

set -U fish_greeting ""

fastfetch

set -gx fish_color_user white
set -gx fish_color_host white
set -gx fish_color_host_remote white
set -gx fish_color_cwd white
set -gx fish_color_cwd_root white
set -gx fish_color_status white

alias cf="clear && fastfetch"

set -gx EDITOR nvim
