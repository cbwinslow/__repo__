#!/usr/bin/env python3
"""
File Name: network_diagnostic_tool.py
Author: [Your Name]
Date: [Current Date]
Purpose: Comprehensive Network Diagnostic Script
Description:
    This Python script is designed to gather a variety of system and network
    information to help diagnose connectivity and configuration problems, 
    such as those encountered with VoIP phones, VLAN setups, and more.
    
    The script is written with Object-Oriented Programming principles
    and aims to be easily extensible. It automatically detects the 
    underlying operating system and runs the appropriate commands or 
    library calls for Windows or Linux/macOS.

Usage:
    1. Make sure Python 3 is installed.
    2. Place this file in a directory of your choice.
    3. Run: python network_diagnostic_tool.py
    4. Review the generated summary report in the console.

Inputs:
    - None (executed directly via command line).
    - Can be extended to accept command-line arguments or input prompts.

Outputs:
    - Prints a formatted report to the console.
    - Could be extended to save a JSON or plain text file with results.

Notes:
    - This script attempts to run various OS-native commands like `ipconfig`, 
      `ifconfig`, `ip`, `route`, `tracert`, `traceroute`, `arp`, etc. 
    - Make sure your user has permissions to execute these commands, 
      and that they're available on the system's PATH.

File Path:
    - network_diagnostic_tool.py (modifiable as needed)
"""

import platform
import subprocess
import sys
from typing import List, Dict, Any

class NetworkDiagnosticTool:
    """
    Main class for performing system and network diagnostics.
    
    Attributes:
        os_type (str): A string indicating the detected operating system
                       ('Windows', 'Linux', 'Darwin', etc.).
        report_data (dict): A dictionary holding all gathered diagnostics 
                            for easy access and serialization.
    """
    def __init__(self):
        """
        Constructor for NetworkDiagnosticTool.
        Detects the operating system and initializes a data structure for storing results.
        """
        self.os_type = platform.system()  # 'Windows', 'Linux', or 'Darwin' (for macOS)
        self.report_data: Dict[str, Any] = {
            "os_type": self.os_type,
            "ip_info": "",
            "gateway_info": "",
            "dns_info": "",
            "arp_table": "",
            "routing_table": "",
            "additional_checks": []
        }

    def gather_ip_info(self) -> None:
        """
        Gathers IP configuration details (IP addresses, subnet masks, etc.).
        Updates self.report_data['ip_info'] with the command output.
        
        Raises:
            subprocess.CalledProcessError: if the command fails to run.
        """
        try:
            if self.os_type == "Windows":
                cmd = ["ipconfig", "/all"]
            else:
                # For Linux / macOS, prefer `ip addr`; fallback to `ifconfig`
                # if `ip` is not available
                ip_cmd = self.which_command(["ip"])
                if ip_cmd:
                    cmd = [ip_cmd, "addr", "show"]
                else:
                    cmd = ["ifconfig"]

            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            self.report_data["ip_info"] = result.strip()
        
        except subprocess.CalledProcessError as e:
            self.report_data["ip_info"] = f"Error gathering IP info: {e.output}"

    def gather_gateway_info(self) -> None:
        """
        Retrieves default gateway information and routing details.
        Updates self.report_data['gateway_info'].

        Raises:
            subprocess.CalledProcessError: if the command fails to run.
        """
        try:
            if self.os_type == "Windows":
                # On Windows, `ipconfig` shows gateway, but `route print` is more explicit
                cmd = ["route", "print"]
            else:
                # On Linux / macOS, use `ip route`; fallback to `netstat -rn`
                ip_cmd = self.which_command(["ip"])
                if ip_cmd:
                    cmd = [ip_cmd, "route", "show"]
                else:
                    cmd = ["netstat", "-rn"]

            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            self.report_data["gateway_info"] = result.strip()
        
        except subprocess.CalledProcessError as e:
            self.report_data["gateway_info"] = f"Error gathering gateway info: {e.output}"

    def gather_dns_info(self) -> None:
        """
        Attempts to retrieve DNS server information.
        For Windows, uses `ipconfig /all`. 
        For Linux/macOS, reads /etc/resolv.conf (if present).

        Raises:
            OSError: if reading /etc/resolv.conf fails.
        """
        try:
            if self.os_type == "Windows":
                # We can parse DNS from the same ipconfig /all output.
                # For brevity, reuse the IP info if needed or call again
                cmd = ["ipconfig", "/all"]
                result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
                # Optionally parse for "DNS Servers" lines. For now, store raw output.
                self.report_data["dns_info"] = result.strip()

            else:
                # Linux / macOS typically store DNS info in /etc/resolv.conf
                try:
                    with open("/etc/resolv.conf", "r", encoding="utf-8") as f:
                        resolv_data = f.read().strip()
                    self.report_data["dns_info"] = resolv_data
                except FileNotFoundError:
                    self.report_data["dns_info"] = (
                        "No /etc/resolv.conf found. Unable to gather DNS info."
                    )
        except subprocess.CalledProcessError as e:
            self.report_data["dns_info"] = f"Error gathering DNS info: {e.output}"

    def gather_arp_table(self) -> None:
        """
        Gathers ARP (Address Resolution Protocol) table to see local MAC-IP mappings.
        Updates self.report_data['arp_table'].
        
        Raises:
            subprocess.CalledProcessError: if the command fails to run.
        """
        try:
            if self.os_type == "Windows":
                cmd = ["arp", "-a"]
            else:
                cmd = ["arp", "-a"]
            
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            self.report_data["arp_table"] = result.strip()
        
        except subprocess.CalledProcessError as e:
            self.report_data["arp_table"] = f"Error gathering ARP info: {e.output}"

    def gather_routing_table(self) -> None:
        """
        Gathers the system's routing table for advanced troubleshooting.
        On Windows, `route print` also reveals this info, 
        but we separate it for clarity. On Linux/macOS, `netstat -rn` or `ip route show`.

        Raises:
            subprocess.CalledProcessError: if the command fails to run.
        """
        try:
            if self.os_type == "Windows":
                cmd = ["route", "print"]
            else:
                ip_cmd = self.which_command(["ip"])
                if ip_cmd:
                    cmd = [ip_cmd, "route", "show"]
                else:
                    cmd = ["netstat", "-rn"]

            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            self.report_data["routing_table"] = result.strip()
        
        except subprocess.CalledProcessError as e:
            self.report_data["routing_table"] = f"Error gathering routing table: {e.output}"

    def perform_additional_checks(self) -> None:
        """
        This method can hold advanced logic or 'decision-tree' checks,
        such as:
          - Ping/Traceroute to known hosts
          - Checking phone system IP (if known)
          - VLAN detection (if available through OS commands or special tools)

        The results will be appended to self.report_data['additional_checks'] as a list of strings.
        """
        checks_output = []

        # 1. Basic ping check to a known public host
        checks_output.append(self._ping_test("8.8.8.8"))

        # 2. Attempt a traceroute/tracert to check path
        checks_output.append(self._traceroute_test("8.8.8.8"))

        # More advanced logic or decision trees can go here:
        # - If ping fails, attempt next host or adjust firewall rules
        # - If traceroute fails at first hop, suspect default gateway issues
        # - Etc.

        self.report_data["additional_checks"] = checks_output

    def _ping_test(self, host: str) -> str:
        """
        Private helper to ping a specified host and return the command output.
        
        Args:
            host (str): The host or IP to ping.

        Returns:
            str: The raw output of the ping command or an error message.
        """
        try:
            if self.os_type == "Windows":
                cmd = ["ping", "-n", "4", host]
            else:
                cmd = ["ping", "-c", "4", host]

            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            return f"Ping Test to {host}:\n{output}"
        
        except subprocess.CalledProcessError as e:
            return f"Error performing ping to {host}: {e.output}"

    def _traceroute_test(self, host: str) -> str:
        """
        Private helper to run traceroute (or tracert on Windows) to the given host.
        
        Args:
            host (str): The host or IP to trace to.

        Returns:
            str: The raw output of the traceroute command or an error message.
        """
        trace_cmd = "tracert" if self.os_type == "Windows" else "traceroute"
        
        # It's possible that 'traceroute' isn't installed by default on some systems.
        # We can try to detect it or just catch errors.
        try:
            cmd_path = self.which_command([trace_cmd])
            if cmd_path is None:
                return f"{trace_cmd} is not installed or not found in PATH."
            else:
                cmd = [cmd_path, host]
                output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
                return f"{trace_cmd.capitalize()} to {host}:\n{output}"
        except subprocess.CalledProcessError as e:
            return f"Error performing {trace_cmd} to {host}: {e.output}"

    @staticmethod
    def which_command(commands: List[str]) -> str:
        """
        Utility function to check if any of the provided commands exist in the PATH.
        
        Args:
            commands (List[str]): A list of command names to check.

        Returns:
            str: The first command found in PATH, or None if none are found.
        """
        import shutil

        for cmd in commands:
            found_path = shutil.which(cmd)
            if found_path is not None:
                return found_path
        return None

    def generate_report(self) -> None:
        """
        Prints a comprehensive, formatted report of all diagnostic data
        stored in self.report_data.
        """
        print("==============================================================")
        print("        Network Diagnostic Tool - Summary Report             ")
        print("==============================================================")
        print(f"Operating System Detected: {self.report_data['os_type']}")
        print("\n---------------------- IP Configuration ----------------------")
        print(self.report_data["ip_info"])
        print("\n---------------------- Default Gateway -----------------------")
        print(self.report_data["gateway_info"])
        print("\n---------------------- DNS Information -----------------------")
        print(self.report_data["dns_info"])
        print("\n--------------------- ARP (MAC Table) ------------------------")
        print(self.report_data["arp_table"])
        print("\n-------------------- Routing Table ---------------------------")
        print(self.report_data["routing_table"])
        print("\n----------------- Additional Diagnostic Checks --------------")
        for idx, item in enumerate(self.report_data["additional_checks"], 1):
            print(f"Check #{idx}:\n{item}\n")
        print("==============================================================")
        print("End of Network Diagnostic Report\n")

    def run_all_diagnostics(self) -> None:
        """
        Higher-level method to run all diagnostic functions in sequence 
        and then produce a report.
        
        This is where you can add or remove diagnostic steps to customize 
        your data collection logic.
        """
        self.gather_ip_info()
        self.gather_gateway_info()
        self.gather_dns_info()
        self.gather_arp_table()
        self.gather_routing_table()
        self.perform_additional_checks()
        self.generate_report()


def main():
    """
    Main function to instantiate and run the NetworkDiagnosticTool.
    """
    diag_tool = NetworkDiagnosticTool()
    diag_tool.run_all_diagnostics()


if __name__ == "__main__":
    main()
