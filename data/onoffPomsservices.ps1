# PowerShell Script to Start or Stop Multiple Windows Services

# --- Configuration ---
# Define the list of service names you want to control.
$ServiceNamesToManage = @(
	"PomsManagementService",
	"ALSService"
)

# --- Functions ---

# Function to display the status of a given service
function Get-ServiceDetailedStatus {
    param (
        [string]$Name
    )
    try {
        $service = Get-Service -Name $Name -ErrorAction Stop
        Write-Host "  Service: $($service.DisplayName) ($($service.Name))" -ForegroundColor Cyan
        Write-Host "  Current Status: $($service.Status)" -ForegroundColor Yellow
        Write-Host "  Startup Type: $($service.StartType)" -ForegroundColor Yellow
        return $service
    }
    catch {
        Write-Warning "Service '$Name' not found or inaccessible: $($_.Exception.Message)"
        return $null
    }
}

# --- Main Script Logic ---

Write-Host "--- Multiple Windows Service Control ---" -ForegroundColor Green
Write-Host "Services to manage:" -ForegroundColor DarkGreen
$ServiceNamesToManage | ForEach-Object { Write-Host "  - $_" }
Write-Host ""

# Prompt user for action
$action = Read-Host "Do you want to (S)tart or (P)ause these services? (S/P)"
$action = $action.Trim().ToUpper()

Write-Host "" # Add a blank line for readability

switch ($action) {
    "S" {
        Write-Host "Attempting to START services..." -ForegroundColor Green
        foreach ($serviceName in $ServiceNamesToManage) {
            Write-Host "`nProcessing service: $serviceName" -ForegroundColor DarkYellow
            $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue

            if ($null -eq $service) {
                Write-Error "Service '$serviceName' not found on this system. Skipping."
                continue
            }

            if ($service.Status -eq "Running") {
                Write-Host "  Service '$serviceName' is already running." -ForegroundColor White
            }
            else {
                try {
                    Start-Service -Name $serviceName -ErrorAction Stop
                    $service | Get-ServiceDetailedStatus # Re-check and display status after attempt
                    Write-Host "  Service '$serviceName' started successfully." -ForegroundColor Green
                }
                catch {
                    Write-Error "  Failed to start service '$serviceName': $($_.Exception.Message)"
                    Write-Host "  Ensure PowerShell is running as administrator and service is not disabled." -ForegroundColor Red
                }
            }
        }
    }
    "P" {
        Write-Host "Attempting to STOP services..." -ForegroundColor Red
        foreach ($serviceName in $ServiceNamesToManage) {
            Write-Host "`nProcessing service: $serviceName" -ForegroundColor DarkYellow
            $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue

            if ($null -eq $service) {
                Write-Error "Service '$serviceName' not found on this system. Skipping."
                continue
            }

            if ($service.Status -eq "Stopped") {
                Write-Host "  Service '$serviceName' is already stopped." -ForegroundColor White
            }
            else {
                try {
                    # -Force is important to stop services that might have dependencies
                    Stop-Service -Name $serviceName -Force -ErrorAction Stop
                    $service | Get-ServiceDetailedStatus # Re-check and display status after attempt
                    Write-Host "  Service '$serviceName' stopped successfully." -ForegroundColor Green
                }
                catch {
                    Write-Error "  Failed to stop service '$serviceName': $($_.Exception.Message)"
                    Write-Host "  Ensure PowerShell is running as administrator and check service dependencies." -ForegroundColor Red
                }
            }
        }
    }
    Default {
        Write-Warning "Invalid action selected. No services were modified. Please choose 'S' for Start or 'P' for Pause."
    }
}

Write-Host "`n--- Script Finished ---" -ForegroundColor Green

