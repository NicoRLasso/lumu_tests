# DNS Log Parsing and Analysis
### Description
This project involves a script designed to parse DNS query logs, send parsed data to the Lumu Custom Collector API, and calculate and display statistics about the queries. The script handles large log files efficiently, using parallel processing for log parsing and asynchronous I/O for network requests.

### Features
- Parses BIND DNS server logs to extract query information.
- Sends parsed data to Lumu's Custom Collector API asynchronously.
- Calculates and displays statistics on client IPs and queried hosts.
- Efficiently handles large log files using parallel processing.

### Computational Complexity
The computational complexity of the ranking algorithm primarily depends on the operations performed to calculate the statistics, which include counting occurrences and sorting.

1. Counting Occurrences: The script uses Python's collections.Counter to count the occurrences of client IPs and hostnames. The complexity of counting occurrences in a list of n elements is O(n), as each element is processed once.

2. Sorting for Ranking: The most_common() method of the Counter class is used to sort the counted items. This method internally uses a sorting algorithm (Timsort in Python) with a worst-case complexity of O(n log n), where n is the number of unique items.

Overall, the computational complexity of the ranking algorithm can be considered O(n log n) due to the sorting step, which dominates the overall complexity.

### Setup and Usage
1. Clone the repository or download the project files.
2. Create a virtual environment: `python -m venv venv`
3. Add the following environment variables: `LUMU_CLIENT_KEY` and `COLLECTOR_ID` for sending data to Lumu.
4. Activate the virtual environment:
On Windows: `venv\Scripts\activate`
On macOS/Linux: `source venv/bin/activate`
5. Install required packages: `pip install aiohttp click`
6. Run the script: `python dns_log_parser.py <log_file_path> [--send] [--host] [--client]`
    - <log_file_path>: Path to the DNS log file.
    - --send: Optional flag to send data to Lumu.
    - --host: Optional flag to print host statistics.
    - --client: Optional flag to print client IP statistics.
