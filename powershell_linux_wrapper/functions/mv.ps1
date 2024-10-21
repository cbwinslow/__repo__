<#
.SYNOPSIS
    Mimics the Linux `mv` command to move or rename files or directories.
.DESCRIPTION
    Moves or renames a file or directory.
.PARAMETER Source
    The path of the file or directory to move or rename.
.PARAMETER Destination
    The new path or name for the file or directory.
.OUTPUTS
    None
.EXAMPLE
    Mv -Source "C:\temp\file.txt" -Destination "C:\temp\newfile.txt"
#>
function Mv {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Source,

        [Parameter(Mandatory=$true)]
        [string]$Destination
    )

    try {
        # Move or rename the file or directory
        Move-Item -Path $Source -Destination $Destination -ErrorAction Stop
        Write-Host "Moved $Source to $Destination"
    } catch {
        Write-Error "Error: Unable to move or rename the file or directory. $_"
    }
}
