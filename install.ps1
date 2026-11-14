<#
  安装 easyfk-skill 套件：把 easyfk-framework-skill、easyfk-dev-skill、easyfk-reverse-skill
  复制到目标 skills 目录的第一层，并移除改名前的旧版 easyfk-skill。

  用法：
    powershell -ExecutionPolicy Bypass -File install.ps1                      # 装到 ~/.cursor/skills
    powershell -ExecutionPolicy Bypass -File install.ps1 -Target D:\proj\.cursor\skills
#>
param(
    [string]$Target = (Join-Path $HOME '.cursor\skills')
)

$ErrorActionPreference = 'Stop'
$skills = @('easyfk-framework-skill', 'easyfk-dev-skill', 'easyfk-reverse-skill')

foreach ($name in $skills) {
    if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot "$name\SKILL.md"))) {
        throw "安装包不完整，缺少 $name\SKILL.md：$PSScriptRoot"
    }
}

New-Item -ItemType Directory -Force -Path $Target | Out-Null
$Target = (Resolve-Path -LiteralPath $Target).Path
if ($Target -eq (Resolve-Path -LiteralPath $PSScriptRoot).Path) {
    throw "目标目录就是安装包所在目录，无需安装：$Target"
}

$legacy = Join-Path $Target 'easyfk-skill'
$legacySkill = Join-Path $legacy 'SKILL.md'
if ((Test-Path -LiteralPath $legacySkill) -and (Select-String -LiteralPath $legacySkill -Pattern '^name:\s*easyfk-skill\s*$' -Quiet)) {
    Remove-Item -LiteralPath $legacy -Recurse -Force
    Write-Host "已移除旧版：$legacy"
}

foreach ($name in $skills) {
    $dest = Join-Path $Target $name
    if (Test-Path -LiteralPath $dest) {
        Remove-Item -LiteralPath $dest -Recurse -Force
    }
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination $dest -Recurse
    Write-Host "已安装：$dest"
}

Write-Host "完成。重启 IDE 或新开会话后生效。"
