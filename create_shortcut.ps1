$ShortcutPath = "C:\Users\Ryan\Desktop\Crosshair.lnk"
$ExePath = "$pwd\dist\crosshair_overlay.exe"
$IconPath = "$pwd\icon.ico"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($ShortcutPath)
$shortcut.TargetPath = $ExePath
$shortcut.WorkingDirectory = "$pwd\dist"
$shortcut.IconLocation = $IconPath
$shortcut.Save()