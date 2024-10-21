<#
.SYNOPSIS
    Mimics the Linux `cp` command to copy files or directories.
.DESCRIPTION
    Copies a file or directory from one location to another.
.PARAMETER Source
    The path of the file or directory to copy.
.PARAMETER Destination
    The path to copy the file or directory to.
.OUTPUTS
    None
.EXAMPLE
    Cp -Source "C:\temp\file.txt" -Destination "C:\backup\file.txt"
#>
function Cp {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Source,

        [Parameter(Mandatory=$true)]
        [string]$Destination
    )

    try {
        # Copy the item to the destination path
        Copy-Item -Path $Source -Destination $Destination -Recurse -ErrorAction Stop
        Write-Host "Copied $Source to $Destination"
    } catch {
        Write-Error "Error: Unable to copy the file or directory. $_"
    }
}
