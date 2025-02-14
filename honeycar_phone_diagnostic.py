#!/usr/bin/env python3
"""
File Name: network_diagnostic_tool.py
Author: [Your Name]
Date: [Current Date]
Purpose: Comprehensive Network Diagnostic + PBX & Polycom Phone Checks
Description:
    This Python script is an extended version of a Network Diagnostic Tool
    that gathers system and network details to help diagnose connectivity
    and configuration problems. It also includes additional PBX/VoIP checks
    and Polycom VVX 450 phone queries to assist with common IP phone issues.

    The script automatically detects the underlying operating system
    (Windows, Linux, macOS) and runs the appropriate commands to gather
    network information. It then attempts to verify PBX connectivity
    (via ping or optional SIP check) and queries Polycom phones by IP to
    gather basic registration/status data (if the phone's web interface
    is reachable and credentials are known).

Usage:
    1. Make sure Python 3 is installed.
    2. Place this file in a directory of your choice.
    3. Run: python network_diagnostic_tool.py
    4. Review the generated summary report in the console.

Inputs:
    - None (executed directly via command line).
    - You can expand it to accept command-line arguments (e.g., PBX IP, phone IPs).

Outputs:
    - Prints a formatted report to the console summarizing network and PBX checks.
    - Could be extended to save a JSON or plain text file with the results.

Notes:
    - This script attempts to run various OS-native commands like `ipconfig`,
      `ifconfig`, `ip`, `route`, `tracert`, `traceroute`, `arp`, etc.
    - The PBX checks here are generic examples (Ping, optional HTTP or SIP check).
      More advanced SIP checks may require specialized Python SIP libraries.
    - The Polycom VVX 450 phone check is an example of how to query the
      phone's web interface (HTTP/HTTPS). You must know the phone IP(s)
      and have valid credentials if the device requires admin authentication.

File Path:
    - network_diagnostic_tool.py (modifiable as needed)
"""

import platform
import subprocess
import sys
from typing import List, Dict, Any, Optional

import socket
import http.client
import urllib.request

class NetworkDiagnosticTool:
    """
    Main class for performing system, network, and PBX/Phone diagnostics.

    Attributes:
        os_type (str): A string indicating the detected operating system
                       ('Windows', 'Linux', 'Darwin', etc.).
        report_data (dict): A dictionary holding all gathered diagnostics
                            for easy access and serialization.
        pbx_address (str): The IP or hostname of the PBX server (if known).
        phone_ips (List[str]): A list of Polycom phone IPs to query.
        phone_admin_user (str): Admin or user credential for phone web interface (if needed).
        phone_admin_pass (str): The corresponding phone password for phone web interface.
    """
    def __init__(self,
                 pbx_address: Optional[str] = None,
                 phone_ips: Optional[List[str]] = None,
                 phone_admin_user: Optional[str] = None,
                 phone_admin_pass: Optional[str] = None):
        """
        Constructor for NetworkDiagnosticTool.
        Detects the operating system and initializes a data structure for storing results.
        Also accepts optional PBX and phone data for more advanced checks.
        """
        self.os_type = platform.system()  # 'Windows', 'Linux', or 'Darwin' (for macOS)
        self.report_data: Dict[str, Any] = {
            "os_type": self.os_type,
            "ip_info": "",
            "gateway_info": "",
            "dns_info": "",
            "arp_table": "",
            "routing_table": "",
            "additional_checks": [],
            "pbx_checks": [],
            "phone_checks": []
        }
        # Store PBX and phone details if provided
        self.pbx_address = pbx_address
        self.phone_ips = phone_ips if phone_ips else []
        self.phone_admin_user = phone_admin_user
        self.phone_admin_pass = phone_admin_pass

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
            self.report_data["gateway_info"] = result.strip()

        except subprocess.CalledProcessError as e:
            self.report_data["gateway_info"] = f"Error gathering gateway info: {e.output}"

    def gather_dns_info(self) -> None:
        """
        Attempts to retrieve DNS server information.
        For Windows, uses 'ipconfig /all'.
        For Linux/macOS, reads /etc/resolv.conf (if present).
        """
        try:
            if self.os_type == "Windows":
                cmd = ["ipconfig", "/all"]
                result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
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
        """
        try:
            cmd = ["arp", "-a"]  # Works on Windows, Linux, macOS
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            self.report_data["arp_table"] = result.strip()

        except subprocess.CalledProcessError as e:
            self.report_data["arp_table"] = f"Error gathering ARP info: {e.output}"

    def gather_routing_table(self) -> None:
        """
        Gathers the system's routing table for advanced troubleshooting.
        On Windows, 'route print'. On Linux/macOS, 'ip route show' or 'netstat -rn'.
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
          - VLAN detection (if possible)
        The results will be appended to self.report_data['additional_checks'] as a list of strings.
        """
        checks_output = []

        # 1. Basic ping check to a known public host (Google DNS)
        checks_output.append(self._ping_test("8.8.8.8"))

        # 2. Attempt a traceroute/tracert to check path
        checks_output.append(self._traceroute_test("8.8.8.8"))

        self.report_data["additional_checks"] = checks_output

    def check_pbx_connectivity(self) -> None:
        """
        If a PBX address was provided, attempts to verify connectivity 
        using ping, and optionally, a SIP or HTTP check.
        
        Populates self.report_data['pbx_checks'] with results.
        """
        if not self.pbx_address:
            self.report_data["pbx_checks"].append("No PBX address provided.")
            return

        checks = []
        # 1. Ping the PBX address
        checks.append(self._ping_test(self.pbx_address))

        # 2. (Optional) Check if SIP port is open. For a simplistic approach,
        #    we can do a TCP connection test to port 5060 (common SIP port).
        #    This won't fully confirm SIP registration, but can show connectivity.
        sip_port_check = self._check_tcp_port(self.pbx_address, 5060, "SIP")
        checks.append(sip_port_check)

        # 3. (Optional) If PBX offers an HTTP/HTTPS portal, we can attempt a quick GET.
        #    e.g., check port 80 or 443. This might help confirm the PBX web UI is reachable.
        #    We'll check port 80 (HTTP) in this example. Adjust as needed.
        http_check = self._check_tcp_port(self.pbx_address, 80, "HTTP")
        checks.append(http_check)

        # Additional logic:
        # - If SIP port is open, we could attempt a more thorough OPTIONS or REGISTER request
        #   using a SIP library (e.g., pjsip or aiosip in Python).
        # - We keep it simple here for demonstration.

        self.report_data["pbx_checks"] = checks

    def check_polycom_phones(self) -> None:
        """
        Attempts to check each Polycom VVX 450 phone in self.phone_ips list.
        We'll do:
          - Ping test
          - (Optional) HTTP/HTTPS GET to phone's web interface 
            (default is typically http://<phone-ip> or https://<phone-ip>).
        Stores results in self.report_data['phone_checks'].
        """
        phone_results = []
        if not self.phone_ips:
            self.report_data["phone_checks"].append("No phone IPs provided.")
            return

        for ip in self.phone_ips:
            msg_list = [f"Checking Polycom VVX 450 Phone @ IP: {ip}"]

            # 1. Ping Test
            ping_result = self._ping_test(ip)
            msg_list.append(ping_result)

            # 2. Attempt to open phone’s web interface
            #    Many Polycom phones default to HTTP on port 80 or HTTPS on 443.
            #    We'll try HTTP on port 80 for demonstration.
            port_check = self._check_tcp_port(ip, 80, "Polycom Web")
            msg_list.append(port_check)

            # 3. Optional: If port 80 is open, attempt a simple GET request to see if the page loads.
            if "open" in port_check.lower():
                http_result = self._http_get_request(ip, 80)
                msg_list.append(http_result)
                
                # Further advanced logic: 
                # - If the phone uses HTTPS on 443, swap port 443 or detect automatically.
                # - If credentials are required, we could try basic authentication, etc.

            phone_results.append("\n".join(msg_list))

        self.report_data["phone_checks"] = phone_results

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

    def _check_tcp_port(self, host: str, port: int, label: str) -> str:
        """
        Checks if a TCP port is open on a given host by attempting to create a socket.

        Args:
            host (str): The hostname or IP address to check.
            port (int): The port number to attempt.
            label (str): A short label for reporting (e.g., "SIP", "HTTP", "Polycom Web").

        Returns:
            str: A message indicating success or failure.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)  # 3-second timeout
        try:
            sock.connect((host, port))
            return f"{label} Port Check: Port {port} on {host} is OPEN."
        except (socket.timeout, socket.error) as e:
            return f"{label} Port Check: Unable to reach port {port} on {host}. Error: {str(e)}"
        finally:
            sock.close()

    def _http_get_request(self, host: str, port: int) -> str:
        """
        Attempts a simple HTTP GET request to the given host and port.

        Args:
            host (str): The hostname or IP address to target.
            port (int): The port number to use (80 for HTTP, 443 for HTTPS, etc.).

        Returns:
            str: A brief result string indicating success or error details.
        """
        url = f"http://{host}:{port}/"
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                status_code = response.getcode()
                return f"HTTP GET to {url} succeeded with status code {status_code}."
        except Exception as e:
            return f"HTTP GET to {url} failed: {str(e)}"

    @staticmethod
    def which_command(commands: List[str]) -> Optional[str]:
        """
        Utility function to check if any of the provided commands exist in the PATH.

        Args:
            commands (List[str]): A list of command names to check.

        Returns:
            str or None: The first command found in PATH, or None if none are found.
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
        print("        Network Diagnostic + PBX/Phone Checks - Report       ")
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

        print("\n-------------------- PBX Connectivity Checks -----------------")
        if self.report_data["pbx_checks"]:
            for idx, item in enumerate(self.report_data["pbx_checks"], 1):
                print(f"* PBX Check #{idx}: {item}")
        else:
            print("No PBX checks performed or no PBX address provided.")

        print("\n-------------------- Polycom Phone Checks --------------------")
        if self.report_data["phone_checks"]:
            for idx, phone_result in enumerate(self.report_data["phone_checks"], 1):
                print(f"Phone #{idx} Results:\n{phone_result}\n")
        else:
            print("No phone checks performed or no phone IPs provided.")

        print("==============================================================")
        print("End of Network Diagnostic Report\n")

    def run_all_diagnostics(self) -> None:
        """
        Higher-level method to run all diagnostic functions in sequence
        and then produce a report.
        
        This includes:
            - Basic network checks
            - Additional checks (ping/traceroute to known host)
            - PBX connectivity checks
            - Polycom phone checks
        """
        self.gather_ip_info()
        self.gather_gateway_info()
        self.gather_dns_info()
        self.gather_arp_table()
        self.gather_routing_table()
        self.perform_additional_checks()

        # Run PBX check only if PBX address is supplied
        if self.pbx_address:
            self.check_pbx_connectivity()

        # Run Polycom phone checks if IPs are supplied
        if self.phone_ips:
            self.check_polycom_phones()

        # Finally, generate the combined report
        self.generate_report()


def main():
    """
    Main function to instantiate and run the NetworkDiagnosticTool.
    
    You can customize the arguments below (pbx_address, phone_ips, etc.)
    or parse them from command-line arguments or config files as needed.
    """
    # Example usage with optional PBX and phone data:
    pbx_ip = "192.168.1.100"  # Replace with your actual PBX IP if known
    polycom_phones = ["192.168.1.101", "192.168.1.102"]  # Example phone IPs
    phone_admin_user = "PolycomAdmin"  # Example user
    phone_admin_pass = "YourPassword"  # Example pass

    diag_tool = NetworkDiagnosticTool(
        pbx_address=pbx_ip,
        phone_ips=polycom_phones,
        phone_admin_user=phone_admin_user,
        phone_admin_pass=phone_admin_pass
    )
    diag_tool.run_all_diagnostics()


if __name__ == "__main__":
    main()
