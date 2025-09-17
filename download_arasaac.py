#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Korean ARASAAC Pictogram Downloader"""

import requests
import json
import os
import time
import argparse
from pathlib import Path
from tqdm import tqdm
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from typing import Dict, List, Optional, Any
import multiprocessing


class KoreanArasaacDownloader:
    """Korean ARASAAC pictogram downloader with automatic thread optimization"""
    
    def __init__(self, base_dir: str = './arasaac_korean', max_workers: Optional[int] = None):
        self.base_url = 'https://api.arasaac.org/v1'
        self.static_url = 'https://static.arasaac.org/pictograms'
        self.language = 'ko'
        self.base_dir = Path(base_dir)
        
        # Auto-determine optimal thread count
        if max_workers is None:
            cpu_count = multiprocessing.cpu_count()
            self.max_workers = min(max(cpu_count * 2, 8), 32)
        else:
            self.max_workers = max_workers
        
        self.counter_lock = threading.Lock()
        self.success_count = 0
        self.failed_count = 0
        
        # Directory structure
        self.images_dir = self.base_dir / 'images'
        self.metadata_dir = self.base_dir / 'metadata'
        self.logs_dir = self.base_dir / 'logs'
        
        for dir_path in [self.images_dir, self.metadata_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.logs_dir / f'download_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        
        print(f"Downloader initialized")
        print(f"Download directory: {self.base_dir.absolute()}")
        print(f"Concurrent threads: {self.max_workers}")
        
    def create_session(self) -> requests.Session:
        """Create optimized session for each thread"""
        session = requests.Session()
        
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=50,
            pool_maxsize=50,
            max_retries=2
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.timeout = 10
        
        return session
        
    def log_message(self, message: str) -> None:
        """Thread-safe logging"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        with self.counter_lock:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
    
    def get_all_pictograms(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch all Korean pictogram metadata"""
        url = f"{self.base_url}/pictograms/all/{self.language}"
        
        session = self.create_session()
        try:
            print("Fetching Korean pictogram metadata...")
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            print(f"Found {len(data)} Korean pictograms")
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            return None
        finally:
            session.close()
    
    def download_single_pictogram(self, pictogram_data: Dict[str, Any]) -> Dict[str, Any]:
        """Download single pictogram"""
        pictogram_id = pictogram_data.get('_id')
        if not pictogram_id:
            return {'success': False, 'id': None, 'error': 'No ID'}
        
        session = self.create_session()
        
        try:
            image_url = f"{self.static_url}/{pictogram_id}/{pictogram_id}.png"
            response = session.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Generate filename with Korean keyword
            filename = f"{pictogram_id}.png"
            
            if 'keywords' in pictogram_data:
                korean_keywords = [kw.get('keyword', '') for kw in pictogram_data['keywords'] 
                                 if kw.get('keyword')]
                if korean_keywords:
                    safe_keyword = korean_keywords[0].replace('/', '_').replace('\\', '_')[:15]
                    if safe_keyword:
                        filename = f"{pictogram_id}_{safe_keyword}.png"
            
            filepath = self.images_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            with self.counter_lock:
                self.success_count += 1
            
            return {
                'success': True,
                'id': pictogram_id,
                'filename': filename,
                'size': len(response.content)
            }
            
        except requests.exceptions.RequestException as e:
            with self.counter_lock:
                self.failed_count += 1
            return {'success': False, 'id': pictogram_id, 'error': str(e)}
        finally:
            session.close()
    
    def download_all_pictograms(self, max_count: Optional[int] = None, 
                               chunk_size: int = 1000) -> Dict[str, Any]:
        """Download all pictograms with parallel processing"""
        pictograms_data = self.get_all_pictograms()
        if not pictograms_data:
            print("Failed to fetch pictogram data")
            return {'successful': [], 'failed': [], 'total_time': 0}
        
        if max_count:
            pictograms_data = pictograms_data[:max_count]
        
        total_count = len(pictograms_data)
        print(f"Download target: {total_count:,} items")
        print(f"Concurrent processing: {self.max_workers} threads")
        
        successful_downloads = []
        failed_downloads = []
        start_time = time.time()
        
        # Process in chunks for memory efficiency
        for chunk_start in range(0, total_count, chunk_size):
            chunk_end = min(chunk_start + chunk_size, total_count)
            chunk_data = pictograms_data[chunk_start:chunk_end]
            
            print(f"Processing chunk {chunk_start//chunk_size + 1}/{(total_count-1)//chunk_size + 1}")
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                with tqdm(total=len(chunk_data), 
                         desc=f"Downloading ({chunk_start+1}-{chunk_end})",
                         unit="items") as pbar:
                    
                    future_to_pictogram = {
                        executor.submit(self.download_single_pictogram, pictogram): pictogram
                        for pictogram in chunk_data
                    }
                    
                    for future in as_completed(future_to_pictogram):
                        result = future.result()
                        
                        if result['success']:
                            successful_downloads.append(result)
                        else:
                            failed_downloads.append(result)
                        
                        pbar.set_postfix({
                            'Success': len(successful_downloads),
                            'Failed': len(failed_downloads),
                            'Rate': f"{len(successful_downloads)/(len(successful_downloads)+len(failed_downloads))*100:.1f}%"
                        })
                        pbar.update(1)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.save_metadata(pictograms_data, [f['id'] for f in failed_downloads if f['id']])
        self.print_final_results(successful_downloads, failed_downloads, total_time)
        
        return {
            'successful': successful_downloads,
            'failed': failed_downloads,
            'total_time': total_time
        }
    
    def print_final_results(self, successful: List[Dict], failed: List[Dict], total_time: float) -> None:
        """Print final download results"""
        total_count = len(successful) + len(failed)
        success_rate = len(successful) / total_count * 100 if total_count > 0 else 0
        
        print(f"\nDownload completed")
        print(f"Success: {len(successful):,}")
        print(f"Failed: {len(failed):,}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Total time: {total_time:.1f}s")
        print(f"Average speed: {len(successful)/total_time:.1f} items/sec")
        
        if successful:
            total_size = sum(d['size'] for d in successful)
            print(f"Total size: {total_size/(1024*1024):.1f} MB")
            print(f"Download speed: {total_size/(1024*1024)/total_time:.1f} MB/sec")
        
        print(f"Files saved to: {self.base_dir.absolute()}")
    
    def save_metadata(self, pictograms_data: List[Dict], failed_ids: List[str]) -> None:
        """Save metadata to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save complete JSON metadata
        json_file = self.metadata_dir / f'pictograms_metadata_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(pictograms_data, f, ensure_ascii=False, indent=2)
        
        # Save research CSV
        csv_file = self.metadata_dir / f'pictograms_research_{timestamp}.csv'
        csv_data = []
        
        for pictogram in pictograms_data:
            korean_keywords = []
            if 'keywords' in pictogram:
                korean_keywords = [kw.get('keyword', '') for kw in pictogram['keywords'] 
                                 if kw.get('keyword')]
            
            csv_row = {
                'id': pictogram.get('_id'),
                'korean_keywords': '; '.join(korean_keywords),
                'categories': '; '.join(map(str, pictogram.get('categories', []))),
                'aac_suitable': pictogram.get('aac', False),
                'color_available': pictogram.get('aacColor', False),
                'has_skin_option': pictogram.get('skin', False),
                'has_hair_option': pictogram.get('hair', False),
                'created_date': pictogram.get('created', ''),
                'last_updated': pictogram.get('lastUpdated', ''),
                'image_filename': f"{pictogram.get('_id')}.png",
                'download_success': pictogram.get('_id') not in failed_ids
            }
            csv_data.append(csv_row)
        
        if csv_data:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)
        
        # Save failed downloads list
        if failed_ids:
            failed_file = self.logs_dir / f'failed_downloads_{timestamp}.txt'
            with open(failed_file, 'w', encoding='utf-8') as f:
                for failed_id in failed_ids:
                    f.write(f"{failed_id}\n")
        
        print(f"Metadata saved: {json_file.name}, {csv_file.name}")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Korean ARASAAC Pictogram Downloader')
    parser.add_argument('--dir', '-d', type=str, default='./arasaac_korean',
                       help='Download directory path')
    parser.add_argument('--max', '-m', type=int, default=None,
                       help='Maximum download count')
    parser.add_argument('--workers', '-w', type=int, default=None,
                       help='Number of concurrent threads (auto-determined if not specified)')
    parser.add_argument('--chunk', type=int, default=1000,
                       help='Chunk size for processing')
    parser.add_argument('--test', action='store_true',
                       help='Test mode (download 100 items only)')
    
    args = parser.parse_args()
    
    if args.test:
        args.max = 100
        print("Test mode: downloading 100 pictograms only")
    
    if args.workers and args.workers > 50:
        print("Warning: thread count limited to 50 for server protection")
        args.workers = 50
    
    print(f"Configuration: dir={args.dir}, threads={args.workers or 'auto'}, max={args.max or 'all'}")
    
    downloader = KoreanArasaacDownloader(
        base_dir=args.dir,
        max_workers=args.workers
    )
    
    try:
        result = downloader.download_all_pictograms(
            max_count=args.max,
            chunk_size=args.chunk
        )
        
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
        print(f"Files downloaded so far are saved in {args.dir}")
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()