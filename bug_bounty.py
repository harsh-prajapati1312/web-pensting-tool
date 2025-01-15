import os
import platform
import sys
import subprocess

file_contents = {}

def run_command(command, shell=False):
  try:
    subprocess.run(command, shell=shell, check=True)
  except subprocess.CalledProcessError as e:
    print(f"[ERROR] Command failed: {e.cmd}")
    
def install_dependencies_linux():
  print("[INFO] Installing dependencies for Linux...")
  deps = [
    "git", "curl", "wget", "python3", "python3-pip", "build-essential", "libssl-dev", "libffi-dev", "python3-venv", "nmap", "jq",
    "snapd", "chromium-browser", "ruby-full"
  ]
  run_command(["sudo", "apt", "update"])
  run_command(["sudo", "apt", "install", "-y"] + deps)
def install_dependencies_windows():
  print("[INFO] Installing dependencies for Windows...")
  run_command(["choco", "install", "-y", "git", "curl", "wget", "python", "nmap"])

def install_go():
  print("[INFO] Installing Go...")
  go_version = "1.20.5"
  go_url = f"https://golang.org/dl/go{go_version}.{ 'windows-amd64.zip' if platform.system() == 'Windows' else 'linux-amd64.tar.gz'}"
  go_archive = "go.zip" if platform.system() == 'Windows' else "go.tar.gz"

  run_command(["wget", go_url, "-O", go_archive])
  if platform.system() == "Windows":
    run_command(["tar", "-xf", go_archive, "-C", "C:\\Program Files"])
    os.environ["PATH"] += ";C:\\Program Files\\go\\bin"
  else:
    run_command(["sudo", "tar", "-C", "/usr/local", "-xzf", go_archive])
    os.environ["PATH"] += ":/usr/local/go/bin"
  run_command(["rm", go_archive])
    
def install_tools():
  print("[INFO] Installing bug bounty tools...")
    
  tools = {
    "httpx": "github.com/projectdiscovery/httpx/cmd/httpx",
    "subfinder": "github.com/projectdiscovery/subfinder/v2/cmd/subfinder",
    "nuclei": "github.com/projectdiscovery/nuclei/v2/cmd/nuclei",
    "katana": "github.com/projectdiscovery/katana/cmd/katana",
    "gf": "github.com/tomnomnom/gf",
  }
    
  for tool, repo in tools.items():
    print(f"[INFO] Installing {tool}...")
    run_command(["go", "install", "-v", f"{repo}@latest"])
    
  # Install additional tools
  print("[INFO] Installing BBot...")
  run_command(["pip", "install", "bbot"])
  print("[INFO] Cloning GF patterns repository...")
    
def bug_bounty_methodology(target):
  print(f"[INFO] Starting bug bounty methodology for target: {target}\n")
    
  output_dir = os.path.expanduser(f"./{target}")
  print(f"[INFO] Creating output directory: {output_dir}")
    
  # Step 1: Subdomain Enumeration
  print("[INFO] Starting subdomain enumeration...")
  run_command(["bbot", "-d", target], shell=True)
  run_command(["subfinder", "-d", target, "-nW", "-silent", "-o", f"{output_dir}/subdomain.txt"], shell=True)

  # Step 2: Filtering live subdomains
  print("[INFO] Filtering live subdomains...")
  with open(f"{output_dir}/subdomain.txt", "r") as infile, open(f"{output_dir}/live_subdomains.txt", "w") as outfile:
    subprocess.run(["httpx", "-silent", "-mc", "200,300,301,302,400,401,402"], stdin=infile, stdout=outfile)
 
  # Step 3: Clean and sort subdomains
  print("[INFO] Cleaning and sorting subdomains...")
  with open(f"{output_dir}/live_subdomains.txt", "r") as infile, open(f"{output_dir}/sorted_sub.txt", "w") as outfile:
    for line in infile:
      outfile.write(line.replace("https://", "").replace("http://", "").strip() + "\n")

  # Step 4: Nmap Scanning
  print("[INFO] Starting Nmap scan...")
  run_command(["nmap", "-iL", f"{output_dir}/sorted_sub.txt", "-Pn", "-p-", "-v", "-oN", f"{output_dir}/nmap.txt"], shell=True)
    
  # Step 5: Endpoint Discovery
  print("[INFO] Discovering endpoints using Katana...")
  run_command(["katana", "-list", f"{output_dir}/live_subdomains.txt", "-o", f"{output_dir}/endpoints.txt"], shell=True)

  # Step 6: Taking Screenshots
  print("[INFO] Taking screenshots of live subdomains...")
  run_command(["eyewitness", "--web", "-f", f"{output_dir}/live_subdomains.txt", "--threads", "5", "-d", f"{output_dir}/screenshots"], shell=True)
 
  # Step 7: Vulnerability Scanning
  print("[INFO] Scanning vulnerabilities with Nuclei...")
  run_command(["nuclei", "-l", f"{output_dir}/live_subdomains.txt", "-t", "templates/", "-o", f"{output_dir}/nuclei_results.txt"], shell=True)
  
  # Step 8: Filter URLs with GF Tool
  print("[INFO] Filtering URLs using GF tool...")
  gf_output_dir = os.path.join(output_dir, "gf")
  os.makedirs(gf_output_dir, exist_ok=True)
    
  patterns = [
    "aws-keys", "base64", "cors", "debug-pages", "debug_logic", "firebase", "fw", "go-functions", "http-auth", "idor",
    "img-traversal", "interestingEXT", "interestingparams", "interestingsubs", "ip", "json-sec", "jsvar", "lfi",
    "meg-headers", "php-curl", "php-errors", "php-serialized", "php-sinks", "php-sources", "rce", "redirect",
    "s3-buckets", "sec", "servers", "sqli", "ssrf", "ssti", "strings", "takeovers", "upload-fields", "urls", "xss"
  ]
    
  input_file = f"{output_dir}/endpoints.txt"
  if os.path.exists(input_file):
    for pattern in patterns:
      output_file = os.path.join(gf_output_dir, f"{pattern}.txt")
      run_command(["gf", pattern, input_file], shell=True)
  else:
    print("[ERROR] Input file for GF does not exist.")

  print(f"[INFO] Bug bounty methodology completed. Results stored in {output_dir}")

def cleanup():
  print("[INFO] Cleaning up...")
  if platform.system() == "Linux":
    run_command(["sudo", "apt", "autoremove", "-y"])
    run_command(["sudo", "apt", "autoclean"])
    
def main():
  if platform.system() == "Linux":
    install_dependencies_linux()
  elif platform.system() == "Windows":
    install_dependencies_windows()
  
  install_go()
  install_tools()
  cleanup()
    
  if len(sys.argv) > 1:
    target = sys.argv[1]
    
    if target:
      bug_bounty_methodology(target)
  else:
    print("[INFO] No target domain provided.")
  print("[INFO] Installation and methodology execution complete. Please verify all tools are installed correctly.")
    
if __name__ == "__main__":
  main()
