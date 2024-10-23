<#
.SYNOPSIS
    Creates a Windows Forms application with a file explorer, script execution buttons, and output display.

.DESCRIPTION
    This script generates a GUI application with the following features:
    - A file explorer on the left side
    - 10 customizable script execution buttons on the right side
    - An output display area at the bottom, switchable between a RichTextBox and a terminal emulator

.PARAMETER NumButtons
    The number of script execution buttons to create. Default is 10.

.PARAMETER InitialPath
    The initial path for the file explorer. Default is the user's desktop.

.EXAMPLE
    .\ScriptName.ps1 -NumButtons 12 -InitialPath "C:\"

.NOTES
    Requires Windows PowerShell 5.1 or later.
    Make sure to run this script with appropriate permissions.
#>

param (
    [int]$NumButtons = 10,
    [string]$InitialPath = [Environment]::GetFolderPath("Desktop")
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Error handling function
function Show-ErrorMessage {
    param (
        [string]$ErrorMessage
    )
    [System.Windows.Forms.MessageBox]::Show($ErrorMessage, "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
}

# Create the main form
$form = New-Object System.Windows.Forms.Form
$form.Text = "PowerShell GUI with File Explorer and Script Buttons"
$form.Size = New-Object System.Drawing.Size(1000, 800)
$form.StartPosition = "CenterScreen"

try {
    # Create the file explorer TreeView
    $treeView = New-Object System.Windows.Forms.TreeView
    $treeView.Location = New-Object System.Drawing.Point(10, 10)
    $treeView.Size = New-Object System.Drawing.Size(300, 400)
    $treeView.Anchor = [System.Windows.Forms.AnchorStyles]::Top -bor [System.Windows.Forms.AnchorStyles]::Bottom -bor [System.Windows.Forms.AnchorStyles]::Left
    $form.Controls.Add($treeView)

    # Populate the TreeView with the file system
    function Add-Node {
        param ($parentNode, $path)
        try {
            $dirs = Get-ChildItem -Path $path -Directory -ErrorAction Stop
            foreach ($dir in $dirs) {
                $newNode = New-Object System.Windows.Forms.TreeNode
                $newNode.Text = $dir.Name
                $newNode.Tag = $dir.FullName
                $parentNode.Nodes.Add($newNode) | Out-Null
                $newNode.Nodes.Add("") | Out-Null  # Placeholder for expandability
            }
        }
        catch {
            Show-ErrorMessage "Error accessing directory: $($_.Exception.Message)"
        }
    }

    $rootNode = New-Object System.Windows.Forms.TreeNode
    $rootNode.Text = "File System"
    $rootNode.Tag = $InitialPath
    $treeView.Nodes.Add($rootNode) | Out-Null
    Add-Node $rootNode $InitialPath

    $treeView.Add_BeforeExpand({
        $node = $_.Node
        if ($node.Nodes.Count -eq 1 -and $node.Nodes[0].Text -eq "") {
            $node.Nodes.Clear()
            Add-Node $node $node.Tag
        }
    })

    # Create script execution buttons
    $buttonPanel = New-Object System.Windows.Forms.FlowLayoutPanel
    $buttonPanel.Location = New-Object System.Drawing.Point(320, 10)
    $buttonPanel.Size = New-Object System.Drawing.Size(650, 400)
    $buttonPanel.FlowDirection = [System.Windows.Forms.FlowDirection]::TopDown
    $buttonPanel.WrapContents = $false
    $buttonPanel.AutoScroll = $true
    $form.Controls.Add($buttonPanel)

    for ($i = 1; $i -le $NumButtons; $i++) {
        $button = New-Object System.Windows.Forms.Button
        $button.Text = "Script $i"
        $button.Size = New-Object System.Drawing.Size(150, 30)
        $button.Tag = $i
        $button.Add_Click({
            $scriptNumber = $this.Tag
            $outputBox.AppendText("Executing Script $scriptNumber`r`n")
            # Here you would add the actual script execution logic
        })
        $buttonPanel.Controls.Add($button)
    }

    # Create the output display area
    $outputBox = New-Object System.Windows.Forms.RichTextBox
    $outputBox.Location = New-Object System.Drawing.Point(10, 420)
    $outputBox.Size = New-Object System.Drawing.Size(960, 330)
    $outputBox.Anchor = [System.Windows.Forms.AnchorStyles]::Bottom -bor [System.Windows.Forms.AnchorStyles]::Left -bor [System.Windows.Forms.AnchorStyles]::Right
    $outputBox.ReadOnly = $true
    $outputBox.Font = New-Object System.Drawing.Font("Consolas", 10)
    $form.Controls.Add($outputBox)

    # Create a toggle button to switch between RichTextBox and Terminal
    $toggleButton = New-Object System.Windows.Forms.Button
    $toggleButton.Text = "Switch to Terminal"
    $toggleButton.Location = New-Object System.Drawing.Point(820, 390)
    $toggleButton.Size = New-Object System.Drawing.Size(150, 30)
    $form.Controls.Add($toggleButton)

    # Terminal emulator (hidden by default)
    $terminal = New-Object System.Windows.Forms.RichTextBox
    $terminal.Location = $outputBox.Location
    $terminal.Size = $outputBox.Size
    $terminal.Anchor = $outputBox.Anchor
    $terminal.Font = $outputBox.Font
    $terminal.BackColor = [System.Drawing.Color]::Black
    $terminal.ForeColor = [System.Drawing.Color]::Green
    $terminal.Visible = $false
    $form.Controls.Add($terminal)

    $toggleButton.Add_Click({
        if ($outputBox.Visible) {
            $outputBox.Visible = $false
            $terminal.Visible = $true
            $toggleButton.Text = "Switch to Output Box"
        } else {
            $outputBox.Visible = $true
            $terminal.Visible = $false
            $toggleButton.Text = "Switch to Terminal"
        }
    })

    # Show the form
    $form.ShowDialog() | Out-Null
}
catch {
    Show-ErrorMessage "An unexpected error occurred: $($_.Exception.Message)"
}
finally {
    # Clean up resources
    if ($null -ne $form) {
        $form.Dispose()
    }
}
