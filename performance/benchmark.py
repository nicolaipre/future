#!/usr/bin/env python3
"""
Benchmark script for comparing Future framework with Flask
"""

import time
import statistics
import requests
import subprocess
import sys
from typing import List, Dict, Any

def benchmark_with_requests(url: str, num_requests: int = 1000) -> Dict[str, Any]:
    """Benchmark using requests library"""
    print(f"Benchmarking {url} with {num_requests} requests...")
    
    times = []
    errors = 0
    
    for i in range(num_requests):
        start_time = time.time()
        try:
            response = requests.get(url)
            if response.status_code == 200:
                times.append(time.time() - start_time)
            else:
                errors += 1
        except Exception as e:
            errors += 1
            print(f"Error on request {i}: {e}")
    
    if times:
        return {
            "total_requests": num_requests,
            "successful_requests": len(times),
            "failed_requests": errors,
            "avg_response_time": statistics.mean(times),
            "median_response_time": statistics.median(times),
            "min_response_time": min(times),
            "max_response_time": max(times),
            "requests_per_second": len(times) / sum(times),
            "times": times
        }
    else:
        return {"error": "No successful requests"}

def benchmark_with_ab(url: str, num_requests: int = 1000, concurrency: int = 10) -> Dict[str, Any]:
    """Benchmark using Apache Bench (ab)"""
    print(f"Benchmarking {url} with ab: {num_requests} requests, {concurrency} concurrent...")
    
    try:
        cmd = [
            "ab", 
            "-n", str(num_requests),
            "-c", str(concurrency),
            "-q",  # quiet mode
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Parse ab output
            output = result.stdout
            lines = output.split('\n')
            
            # Extract key metrics
            metrics = {}
            for line in lines:
                if "Requests per second:" in line:
                    metrics["requests_per_second"] = float(line.split()[0])
                elif "Time per request:" in line and "mean" in line:
                    metrics["avg_response_time"] = float(line.split()[3])
                elif "Transfer rate:" in line:
                    metrics["transfer_rate"] = float(line.split()[2])
                elif "Failed requests:" in line:
                    metrics["failed_requests"] = int(line.split()[2])
                elif "Complete requests:" in line:
                    metrics["total_requests"] = int(line.split()[2])
            
            return metrics
        else:
            return {"error": f"ab failed: {result.stderr}"}
            
    except Exception as e:
        return {"error": f"ab error: {e}"}

def benchmark_with_wrk(url: str, duration: int = 10, threads: int = 4) -> Dict[str, Any]:
    """Benchmark using wrk"""
    print(f"Benchmarking {url} with wrk: {duration}s duration, {threads} threads...")
    
    try:
        cmd = [
            "wrk",
            "-t", str(threads),
            "-c", str(threads * 10),  # connections
            "-d", f"{duration}s",
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Parse wrk output
            output = result.stdout
            lines = output.split('\n')
            
            metrics = {}
            for line in lines:
                if "Requests/sec:" in line:
                    metrics["requests_per_second"] = float(line.split()[1])
                elif "Transfer/sec:" in line:
                    metrics["transfer_rate"] = line.split()[1]
                elif "requests in" in line and "read" in line:
                    parts = line.split()
                    metrics["total_requests"] = int(parts[0])
                    metrics["duration"] = float(parts[3])
            
            return metrics
        else:
            return {"error": f"wrk failed: {result.stderr}"}
            
    except Exception as e:
        return {"error": f"wrk error: {e}"}

def print_results(framework: str, results: Dict[str, Any]):
    """Print benchmark results in a formatted way"""
    print(f"\n{'='*50}")
    print(f"Results for {framework}")
    print(f"{'='*50}")
    
    if "error" in results:
        print(f"Error: {results['error']}")
        return
    
    if "requests_per_second" in results:
        print(f"Requests/sec: {results['requests_per_second']:.2f}")
    
    if "avg_response_time" in results:
        print(f"Avg Response Time: {results['avg_response_time']:.4f}s")
    
    if "median_response_time" in results:
        print(f"Median Response Time: {results['median_response_time']:.4f}s")
    
    if "min_response_time" in results:
        print(f"Min Response Time: {results['min_response_time']:.4f}s")
    
    if "max_response_time" in results:
        print(f"Max Response Time: {results['max_response_time']:.4f}s")
    
    if "total_requests" in results:
        print(f"Total Requests: {results['total_requests']}")
    
    if "failed_requests" in results:
        print(f"Failed Requests: {results['failed_requests']}")
    
    if "transfer_rate" in results:
        print(f"Transfer Rate: {results['transfer_rate']}")

def main():
    """Main benchmarking function"""
    print("Future vs Flask Benchmark")
    print("="*50)
    
    # Test URLs
    future_url = "http://localhost:5000/"
    flask_url = "http://localhost:5001/"
    
    # Test parameters
    num_requests = 1000
    concurrency = 10
    duration = 10
    
    print(f"Testing with {num_requests} requests, {concurrency} concurrent connections")
    print(f"Future URL: {future_url}")
    print(f"Flask URL: {flask_url}")
    
    # Test with requests library
    print("\n" + "="*50)
    print("Testing with requests library")
    print("="*50)
    
    future_results = benchmark_with_requests(future_url, num_requests)
    print_results("Future", future_results)
    
    flask_results = benchmark_with_requests(flask_url, num_requests)
    print_results("Flask", flask_results)
    
    # Test with ab
    print("\n" + "="*50)
    print("Testing with Apache Bench (ab)")
    print("="*50)
    
    future_ab = benchmark_with_ab(future_url, num_requests, concurrency)
    print_results("Future (ab)", future_ab)
    
    flask_ab = benchmark_with_ab(flask_url, num_requests, concurrency)
    print_results("Flask (ab)", flask_ab)
    
    # Test with wrk
    print("\n" + "="*50)
    print("Testing with wrk")
    print("="*50)
    
    future_wrk = benchmark_with_wrk(future_url, duration)
    print_results("Future (wrk)", future_wrk)
    
    flask_wrk = benchmark_with_wrk(flask_url, duration)
    print_results("Flask (wrk)", flask_wrk)

if __name__ == "__main__":
    main() 