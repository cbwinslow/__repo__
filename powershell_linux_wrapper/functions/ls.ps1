<#
.SYNOPSIS
    Mimics the Linux `ls` command to list directory contents.
.DESCRIPTION
    Lists files and directories in the specified path. If no path is given, it lists the current directory.
.PARAMETER Path
    The path of the directory to list contents from. Defaults to the current directory.
.OUTPUTS
    System.IO.FileInfo, System.IO.DirectoryInfo
.EXAMPLE
    Ls -Path "C:\temp"
#>
function Ls {
    param (
        [string]$Path = "."
    )

    try {
        # List the contents of the directory
        Get-ChildItem -Path $Path -ErrorAction Stop
    } catch {
        Write-Error "Error: Unable to list directory contents. $_"
    }
}
