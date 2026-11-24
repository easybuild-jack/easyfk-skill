#!/bin/sh
# 安装 easyfk-skill 套件：把 easyfk-framework-skill、easyfk-dev-skill、easyfk-reverse-skill、
# easyfk-generator-skill 复制到目标 skills 目录的第一层，并移除改名前的旧版 easyfk-skill。
#
# 用法：
#   sh install.sh                          # 装到 ~/.cursor/skills
#   sh install.sh /path/to/proj/.cursor/skills
set -e

SRC=$(cd "$(dirname "$0")" && pwd)
TARGET=${1:-"$HOME/.cursor/skills"}
SKILLS="easyfk-framework-skill easyfk-dev-skill easyfk-reverse-skill easyfk-generator-skill"

for name in $SKILLS; do
  if [ ! -f "$SRC/$name/SKILL.md" ]; then
    echo "安装包不完整，缺少 $name/SKILL.md：$SRC" >&2
    exit 1
  fi
done

mkdir -p "$TARGET"
TARGET=$(cd "$TARGET" && pwd)
if [ "$TARGET" = "$SRC" ]; then
  echo "目标目录就是安装包所在目录，无需安装：$TARGET" >&2
  exit 1
fi

LEGACY="$TARGET/easyfk-skill"
if [ -f "$LEGACY/SKILL.md" ] && grep -Eq '^name:[[:space:]]*easyfk-skill[[:space:]]*$' "$LEGACY/SKILL.md"; then
  rm -rf "$LEGACY"
  echo "已移除旧版：$LEGACY"
fi

for name in $SKILLS; do
  rm -rf "$TARGET/$name"
  cp -R "$SRC/$name" "$TARGET/$name"
  echo "已安装：$TARGET/$name"
done

echo "完成。重启 IDE 或新开会话后生效。"
