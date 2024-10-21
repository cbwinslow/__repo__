<#
.SYNOPSIS
    Mimics the Linux `touch` command to create a new file or update its timestamp.
.DESCRIPTION
    If the specified file does not exist, it will create a new file. 
    If the file exists, it will update the last write time to the current date and time.
.PARAMETER Path
    The path of the file to be created or updated.
.OUTPUTS
    None
.EXAMPLE
    Touch -Path "C:\temp\file.txt"
#>
function Touch {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Path
    )

    try {
        # Check if the file exists; if not, create it
        if (-Not (Test-Path $Path)) {
            New-Item -Path $Path -ItemType File -ErrorAction Stop
            Write-Host "File created at $Path"
        } else {
            # If the file exists, update its timestamp
            (Get-Item $Path).LastWriteTime = Get-Date
            Write-Host "Timestamp updated for $Path"
        }
    } catch {
        Write-Error "Error: Unable to create or update the file. $_"
    }
}
