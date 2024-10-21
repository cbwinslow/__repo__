<#
.SYNOPSIS
    Mimics the Linux `cat` command to display file contents.
.DESCRIPTION
    Outputs the content of the specified file to the console.
.PARAMETER Path
    The path of the file to display.
.OUTPUTS
    System.String
.EXAMPLE
    Cat -Path "C:\temp\file.txt"
#>
function Cat {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Path
    )

    try {
        # Display the contents of the file
        Get-Content -Path $Path -ErrorAction Stop
    } catch {
        Write-Error "Error: Unable to read the file. $_"
    }
}
