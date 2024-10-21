<#
.SYNOPSIS
    Mimics the Linux `rm` command to delete files or directories.
.DESCRIPTION
    Deletes the specified file or directory. For directories, the -Recurse option is used.
.PARAMETER Path
    The path of the file or directory to delete.
.OUTPUTS
    None
.EXAMPLE
    Rm -Path "C:\temp\file.txt"
#>
function Rm {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Path
    )

    try {
        # Delete the file or directory with a confirmation prompt
        Remove-Item -Path $Path -Recurse -Force -ErrorAction Stop
        Write-Host "Deleted $Path"
    } catch {
        Write-Error "Error: Unable to delete the file or directory. $_"
    }
}
