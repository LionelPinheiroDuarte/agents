# Shared by the claude-edits and claude-projects popups, so they look and
# behave alike: palette, $GITHUB, ages, the fzf version check and the fzf
# options of their grouped lists. Sourced, not run:
#
#   source "$(dirname "$(realpath "$0")")/../lib/popup.sh"

# same fallback as the dotfiles: ~/Repos/github, else ~/repos/github
GITHUB_DIR="${GITHUB:-$HOME/Repos/github}"
[[ ! -d "$GITHUB_DIR" && -d "$HOME/repos/github" ]] && GITHUB_DIR="$HOME/repos/github"

# palette (see the design README in Documents/Design/Claude tools)
DIM=$'\e[38;2;139;147;163m' ORG=$'\e[38;2;240;164;93m'
GRN=$'\e[38;2;140;201;143m' RED=$'\e[38;2;239;143;143m'
BLU=$'\e[38;2;130;170;255m' PRP=$'\e[38;2;195;166;255m'
YLW=$'\e[38;2;229;192;123m' BOLD=$'\e[1m' OFF=$'\e[0m'
KEY=$'\e[48;2;90;98;115m\e[38;2;214;217;223m'
# badges: dark bold text on an accent background
ON_DARK=$'\e[38;2;27;29;35m\e[1m'
BG_ORG=$'\e[48;2;240;164;93m'"$ON_DARK" BG_GRN=$'\e[48;2;140;201;143m'"$ON_DARK"
BG_BLU=$'\e[48;2;130;170;255m'"$ON_DARK"

# "< 1 min", "4 min", "2 h", "hier", "3 j", "2 sem", "1 mois", "3 ans" since <epoch>.
ago() {
  [ -n "$1" ] || return
  local age=$(( EPOCHSECONDS - $1 ))
  if   (( age < 60 ));          then echo "< 1 min"
  elif (( age < 3600 ));        then echo "$(( age / 60 )) min"
  elif (( age < 86400 ));       then echo "$(( age / 3600 )) h"
  elif (( age < 2 * 86400 ));   then echo "hier"
  elif (( age < 14 * 86400 ));  then echo "$(( age / 86400 )) j"
  elif (( age < 60 * 86400 ));  then echo "$(( age / 604800 )) sem"
  elif (( age < 365 * 86400 )); then echo "$(( age / 2592000 )) mois"
  elif (( age < 730 * 86400 )); then echo "1 an"
  else                               echo "$(( age / 31536000 )) ans"; fi
}

# The same as a phrase: "à l'instant", "hier", "il y a 4 min".
since() {
  local a; a=$(ago "$1")
  case $a in
    "< 1 min") echo "à l'instant" ;;
    hier)      echo hier ;;
    *)         echo "il y a $a" ;;
  esac
}

# Stop with a message when fzf is older than the popups need: --footer (0.63)
# and --gutter (0.66) are the newest options they use.
require_fzf() {
  local version major minor
  version=$(fzf --version 2>/dev/null | cut -d' ' -f1)
  IFS=. read -r major minor _ <<<"$version"
  (( ${major:-0} > 0 || ${minor:-0} >= 66 )) && return
  echo "${0##*/} a besoin de fzf >= 0.66 (installé : ${version:-aucun})."
  echo "Lance le playbook dotfiles : ansible-playbook -i inventory.ini playbook.yml --tags fzf -K"
  read -rsn1
  exit 1
}

# POPUP_FZF: the fzf options both popups share, for <accent colour> <title> <ghost>.
# Input lines are "<header>\t<row>\t<key>…": only <row> is searched (--nth 2),
# so group headers drop out as soon as a query is typed, and headers have no
# <key> ({3}): the cursor steps over them and enter ignores them.
popup_fzf_opts() {
  local accent="$1"
  POPUP_FZF=(
    --ansi --layout=reverse --delimiter '\t' --with-nth 1,2 --nth 2 --tabstop 1
    --border=rounded --border-label " $2 " --border-label-pos=3
    --input-border=line --footer-border=line
    --prompt '❯ ' --ghost "$3" --info=inline-right --no-separator
    --pointer '▌' --gutter ' ' --highlight-line --no-scrollbar
    --color "bg+:#2c313c,fg+:#d6d9df,pointer:$accent,hl:$accent,hl+:$accent"
    --color "border:#5a6273,label:$accent:bold,prompt:$accent,info:#d6d9df,ghost:#5a6273"
    --color 'input-border:#5a6273,footer-border:#5a6273,preview-border:#5a6273'
    --bind 'change:first' --bind 'result:transform([ -n {3} ] || echo down)'
    --bind 'down:down+transform([ -n {3} ] || echo down)'
    --bind 'up:up+transform([ -n {3} ] || { [ $FZF_POS -le 1 ] && echo down || echo up; })'
    --bind 'enter:transform([ -n {3} ] && echo accept)'
    --bind 'ctrl-/:toggle-preview'
  )
}
