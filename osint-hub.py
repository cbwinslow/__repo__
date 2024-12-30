import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
import socket
import requests
import json
import whois
import dns.resolver
from datetime import datetime
import threading
import csv
import os
import time
import plotly.graph_objects as go
import shodan
from virus_total_apis import PublicApi as VirusTotalAPI
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from requests_html import HTMLSession
import pandas as pd

class RateLimiter:
    def __init__(self, calls_per_second=1):
        self.calls_per_second = calls_per_second
        self.last_call = 0
        
    def wait(self):
        """Wait if necessary to respect rate limits"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call
        if time_since_last_call < 1.0 / self.calls_per_second:
            time.sleep((1.0 / self.calls_per_second) - time_since_last_call)
        self.last_call = time.time()

class OSINTHub:
    def __init__(self, root):
        self.root = root
        self.root.title("OSINT Research Hub")
        self.root.geometry("1024x768")
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter()
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Initialize tabs
        self.setup_input_tab()
        self.setup_results_tab()
        self.setup_config_tab()
        self.setup_visualization_tab()
        
        # Initialize results storage
        self.results = {}
        self.load_config()
        
    def load_config(self):
        """Load API keys from configuration file"""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.api_keys = config.get('api_keys', {})
        except FileNotFoundError:
            self.api_keys = {}
    
    def save_config(self):
        """Save API keys to configuration file"""
        config = {
            'api_keys': {k: v.get() for k, v in self.api_key_entries.items()}
        }
        with open('config.json', 'w') as f:
            json.dump(config, f)
        messagebox.showinfo("Success", "Configuration saved successfully!")
        
    def setup_input_tab(self):
        # Previous input tab setup code remains the same
        input_frame = ttk.Frame(self.notebook)
        self.notebook.add(input_frame, text="Input")
        
        # Input fields
        ttk.Label(input_frame, text="Email:").grid(row=0, column=0, padx=5, pady=5)
        self.email_entry = ttk.Entry(input_frame, width=40)
        self.email_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Phone Number:").grid(row=1, column=0, padx=5, pady=5)
        self.phone_entry = ttk.Entry(input_frame, width=40)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Name:").grid(row=2, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(input_frame, width=40)
        self.name_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="IP Address:").grid(row=3, column=0, padx=5, pady=5)
        self.ip_entry = ttk.Entry(input_frame, width=40)
        self.ip_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Search options
        self.search_options = ttk.LabelFrame(input_frame, text="Search Options")
        self.search_options.grid(row=4, column=0, columnspan=2, pady=10, padx=5, sticky="ew")
        
        # Checkbuttons for different search types
        self.use_shodan = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.search_options, text="Use Shodan", variable=self.use_shodan).pack(side=tk.LEFT, padx=5)
        
        self.use_virustotal = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.search_options, text="Use VirusTotal", variable=self.use_virustotal).pack(side=tk.LEFT, padx=5)
        
        self.use_haveibeenpwned = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.search_options, text="Use HaveIBeenPwned", variable=self.use_haveibeenpwned).pack(side=tk.LEFT, padx=5)
        
        # Search buttons
        ttk.Button(input_frame, text="Search All", command=self.search_all).grid(row=5, column=0, columnspan=2, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(input_frame, length=300, mode='determinate')
        self.progress.grid(row=6, column=0, columnspan=2, pady=10)
        
    def setup_visualization_tab(self):
        """Setup the visualization tab"""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="Visualizations")
        
        # Create a figure for matplotlib
        self.fig = plt.Figure(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill='both')
        
    def setup_config_tab(self):
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuration")
        
        # API Configuration
        api_frame = ttk.LabelFrame(config_frame, text="API Configuration")
        api_frame.pack(fill='x', padx=5, pady=5)
        
        # Add API key inputs
        self.api_key_entries = {}
        apis = {
            'Shodan': 'Enter Shodan API key',
            'VirusTotal': 'Enter VirusTotal API key',
            'HaveIBeenPwned': 'Enter HaveIBeenPwned API key'
        }
        
        for i, (api, placeholder) in enumerate(apis.items()):
            ttk.Label(api_frame, text=f"{api} API Key:").grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(api_frame, width=40)
            entry.insert(0, self.api_keys.get(api, ''))
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.api_key_entries[api] = entry
        
        # Save configuration button
        ttk.Button(config_frame, text="Save Configuration", command=self.save_config).pack(pady=10)
        
    def search_shodan(self, ip):
        """Search Shodan for IP information"""
        results = []
        api_key = self.api_key_entries['Shodan'].get()
        
        if not api_key:
            return "Shodan API key not configured"
            
        try:
            api = shodan.Shodan(api_key)
            host = api.host(ip)
            
            results.append("=== Shodan Results ===")
            results.append(f"Organization: {host.get('org', 'N/A')}")
            results.append(f"Operating System: {host.get('os', 'N/A')}")
            results.append(f"Open Ports: {', '.join(map(str, host.get('ports', [])))}")
            
            # Add services information
            results.append("\nServices:")
            for service in host.get('data', []):
                results.append(f"Port {service.get('port')}: {service.get('product', 'N/A')}")
                
        except Exception as e:
            results.append(f"Error in Shodan search: {str(e)}")
            
        return "\n".join(results)
        
    def search_virustotal(self, ip_or_domain):
        """Search VirusTotal for IP or domain information"""
        results = []
        api_key = self.api_key_entries['VirusTotal'].get()
        
        if not api_key:
            return "VirusTotal API key not configured"
            
        try:
            vt = VirusTotalAPI(api_key)
            
            if self.validate_ip(ip_or_domain):
                response = vt.get_ip_report(ip_or_domain)
            else:
                response = vt.get_domain_report(ip_or_domain)
                
            if response.get('response_code') == 200:
                results.append("=== VirusTotal Results ===")
                results.append(f"Detection Ratio: {response.get('positives', 0)}/{response.get('total', 0)}")
                results.append(f"Last Scan: {response.get('scan_date', 'N/A')}")
                
                # Add detailed scan results
                if 'scans' in response:
                    results.append("\nScan Results:")
                    for scanner, result in response['scans'].items():
                        if result.get('detected'):
                            results.append(f"{scanner}: {result.get('result', 'N/A')}")
                            
        except Exception as e:
            results.append(f"Error in VirusTotal search: {str(e)}")
            
        return "\n".join(results)
        
    def search_haveibeenpwned(self, email):
        """Search HaveIBeenPwned for email breach information"""
        results = []
        api_key = self.api_key_entries['HaveIBeenPwned'].get()
        
        if not api_key:
            return "HaveIBeenPwned API key not configured"
            
        headers = {
            'hibp-api-key': api_key,
            'User-Agent': 'OSINT Research Hub'
        }
        
        try:
            response = requests.get(
                f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                headers=headers
            )
            
            if response.status_code == 200:
                breaches = response.json()
                results.append("=== HaveIBeenPwned Results ===")
                results.append(f"Found in {len(breaches)} breach(es)")
                
                for breach in breaches:
                    results.append(f"\nBreach: {breach['Name']}")
                    results.append(f"Date: {breach['BreachDate']}")
                    results.append(f"Description: {breach['Description']}")
                    results.append(f"Compromised Data: {', '.join(breach['DataClasses'])}")
            elif response.status_code == 404:
                results.append("No breaches found")
            else:
                results.append(f"Error: {response.status_code}")
                
        except Exception as e:
            results.append(f"Error in HaveIBeenPwned search: {str(e)}")
            
        return "\n".join(results)
        
    def analyze_phone(self, phone_number):
        """Enhanced phone number analysis"""
        results = []
        
        try:
            # Parse phone number
            parsed = phonenumbers.parse(phone_number)
            
            results.append("=== Phone Number Analysis ===")
            results.append(f"Valid: {phonenumbers.is_valid_number(parsed)}")
            results.append(f"Country: {geocoder.description_for_number(parsed, 'en')}")
            results.append(f"Carrier: {carrier.name_for_number(parsed, 'en')}")
            
            # Get possible timezones
            tz = timezone.time_zones_for_number(parsed)
            results.append(f"Possible Timezones: {', '.join(tz)}")
            
            # Number type
            number_type = phonenumbers.number_type(parsed)
            type_map = {
                phonenumbers.PhoneNumberType.MOBILE: "Mobile",
                phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line",
                phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
                phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free",
                phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
                phonenumbers.PhoneNumberType.SHARED_COST: "Shared Cost",
                phonenumbers.PhoneNumberType.VOIP: "VoIP",
                phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
                phonenumbers.PhoneNumberType.PAGER: "Pager",
                phonenumbers.PhoneNumberType.UAN: "UAN",
                phonenumbers.PhoneNumberType.UNKNOWN: "Unknown"
            }
            results.append(f"Number Type: {type_map.get(number_type, 'Unknown')}")
            
        except Exception as e:
            results.append(f"Error in phone analysis: {str(e)}")
            
        return "\n".join(results)
        
    def create_visualizations(self):
        """Create visualizations based on collected data"""
        self.fig.clear()
        
        if not self.results:
            return
            
        # Create subplots
        axs = self.fig.subplots(2, 1)
        
        # Top plot: API Response Timeline
        timestamps = []
        response_times = []
        
        for result in self.results.get('api_responses', []):
            timestamps.append(result['timestamp'])
            response_times.append(result['response_time'])
            
        if timestamps and response_times:
            axs[0].plot(timestamps, response_times, 'bo-')
            axs[0].set_title('API Response Times')
            axs[0].set_xlabel('Time')
            axs[0].set_ylabel('Response Time (s)')
            axs[0].tick_params(axis='x', rotation=45)
            
        # Bottom plot: Data Sources Distribution
        if 'data_sources' in self.results:
            sources = list(self.results['data_sources'].keys())
            values = list(self.results['data_sources'].values())
            
            axs[1].bar(sources, values)
            axs[1].set_title('Data Sources Distribution')
            axs[1].set_xlabel('Source')
            axs[1].set_ylabel('Number of Results')
            axs[1].tick_params(axis='x', rotation=45)
            
        self.fig.tight_layout()
        self.canvas.draw()