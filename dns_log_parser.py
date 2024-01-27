import asyncio
from datetime import datetime
import re
import aiohttp
from collections import Counter
import click
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional, Generator

LUMU_CLIENT_KEY: str = ""
COLLECTOR_ID: str = ""
LUMU_API_ENDPOINT: str = "https://api.lumu.io"

pattern: re.Pattern = re.compile(
    r"(\d+-\w+-\d+ \d+:\d+:\d+\.\d+) queries: info: client @0x[0-9a-f]+ ([0-9.]+)#\d+ \(([^)]+)\): query: [^ ]+ IN (\w+)"
)


def extract_dns_query_info(line: str) -> Optional[Dict[str, str]]:
    match = pattern.search(line)
    if match:
        timestamp_str = match.group(1)
        timestamp = datetime.strptime(
            timestamp_str, "%d-%b-%Y %H:%M:%S.%f").isoformat() + "Z"
        client_ip = match.group(2).strip()
        queried_domain = match.group(3).strip()
        query_type = match.group(4).strip()
        return {
            "timestamp": timestamp,
            "name": queried_domain,
            "client_ip": client_ip,
            "type": query_type
        }
    return None


def parse_dns_log(file_path: str) -> List[Dict[str, str]]:
    extracted_data: List[Dict[str, str]] = []
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with ThreadPoolExecutor() as executor:
        results = executor.map(extract_dns_query_info, lines)
        extracted_data = [data for data in results if data]

    return extracted_data


async def send_data_to_lumu(data: List[Dict[str, str]]) -> None:
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(data), 500):
            chunk = data[i:i+500]
            api_url = f"{
                LUMU_API_ENDPOINT}/collectors/{COLLECTOR_ID}/dns/queries?key={LUMU_CLIENT_KEY}"
            async with session.post(api_url, json=chunk, headers={'Content-Type': 'application/json'}) as response:
                if response.status != 200:
                    response_text = await response.text()
                    print(
                        f"Failed to send data chunk {i//500 + 1}: {response.status} {response_text}")


def print_statistics(data: List[Dict[str, str]], title: str) -> None:
    total_records = len(data)
    if not data:
        print(f"No data available for {title}")
        return

    item_key: str = "client_ip" if title == "Client IPs" else "name"

    counts: Counter = Counter([item[item_key] for item in data])

    largest_item = max(counts.keys(), key=len)
    title_spacing = len(largest_item) + 2
    print(f"{title} Rank".ljust(title_spacing), "Count Percent")
    print("-" * title_spacing, "----- ------")
    for item, count in counts.most_common():
        percentage = (count / total_records) * 100
        print(
            f"{item.ljust(title_spacing)} {str(count).rjust(5)} {str(f'{percentage:.2f}%').rjust(6)}")
    print("-" * title_spacing, "----- ------")


@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--send', is_flag=True, help="Send data to Lumu")
@click.option('--host', is_flag=True, help="Print host statistics")
@click.option('--client', is_flag=True, help="Print client statistics")
def main(file_path: str, send: bool, host: bool, client: bool) -> None:
    extracted_data = parse_dns_log(file_path)
    print(f"Total records {len(extracted_data)}")

    if send and extracted_data:
        asyncio.run(send_data_to_lumu(extracted_data))

    if client:
        print_statistics(extracted_data, "Client IPs")

    if host:
        print_statistics(extracted_data, "Hosts")


if __name__ == "__main__":
    main()
