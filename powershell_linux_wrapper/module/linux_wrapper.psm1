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
