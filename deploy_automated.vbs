Set WshShell = WScript.CreateObject("WScript.Shell")

' Function to run Railway command and send Enter key
Function RunRailwayCommand(cmd)
    WshShell.Run "cmd /c cd /d C:\Users\elamuruganm\Desktop\Desktop\Zap\Cursor\saas_app && " & cmd, 1, False
    WScript.Sleep 3000
    ' Send Enter to accept defaults
    WshShell.SendKeys "{ENTER}"
    WScript.Sleep 2000
    WshShell.SendKeys "{ENTER}"
    WScript.Sleep 2000
End Function

' Link project
WshShell.Run "cmd /c cd /d C:\Users\elamuruganm\Desktop\Desktop\Zap\Cursor\saas_app && railway link --project 5fad707a-bcd2-4fb6-805f-282da19a459a --environment production", 1, True
WScript.Sleep 3000

' Add PostgreSQL
RunRailwayCommand "railway add -d postgres"
WScript.Sleep 20000

MsgBox "PostgreSQL added. Press OK to continue with backend deployment."

' Add backend
WshShell.Run "cmd /c cd /d C:\Users\elamuruganm\Desktop\Desktop\Zap\Cursor\saas_app && railway add -r autobotela-sys/saas-copy-trading -s backend", 1, True
WScript.Sleep 5000

MsgBox "Backend added. Press OK to continue with frontend deployment."

' Add frontend
WshShell.Run "cmd /c cd /d C:\Users\elamuruganm\Desktop\Desktop\Zap\Cursor\saas_app && railway add -r autobotela-sys/saas-copy-trading -s frontend", 1, True

MsgBox "Deployment complete! Check Railway dashboard."
