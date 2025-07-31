# log_analyzer.py
# 로그 분석 및 관리 유틸리티

import json
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path
import pandas as pd


class LogAnalyzer:
    """로그 분석 도구"""
    
    def __init__(self, log_dir="/var/log/streamlit-app"):
        self.log_dir = Path(log_dir)
    
    def analyze_errors(self, hours=24):
        """에러 로그 분석"""
        error_file = self.log_dir / "error.log"
        
        if not error_file.exists():
            return {"message": "Error log file not found"}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        errors = []
        
        with open(error_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    # 타임스탬프 추출
                    timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    if timestamp_match:
                        timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                        if timestamp >= cutoff_time:
                            errors.append({
                                'timestamp': timestamp,
                                'line': line.strip()
                            })
                except Exception:
                    continue
        
        # 에러 유형별 분류
        error_types = Counter()
        for error in errors:
            if 'Exception:' in error['line']:
                exception_type = re.search(r'Exception: (\w+)', error['line'])
                if exception_type:
                    error_types[exception_type.group(1)] += 1
        
        return {
            'total_errors': len(errors),
            'error_types': dict(error_types),
            'recent_errors': errors[-10:] if errors else []
        }
    
    def analyze_performance(self, hours=24):
        """성능 로그 분석"""
        perf_file = self.log_dir / "performance.log"
        
        if not perf_file.exists():
            return {"message": "Performance log file not found"}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        operations = defaultdict(list)
        
        with open(perf_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    # 타임스탬프 추출
                    timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    if timestamp_match:
                        timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                        if timestamp >= cutoff_time:
                            # JSON 데이터 추출
                            json_match = re.search(r'\{.*\}', line)
                            if json_match:
                                data = json.loads(json_match.group())
                                operation = data.get('operation', 'unknown')
                                duration = data.get('duration_ms', 0)
                                operations[operation].append(duration)
                except Exception:
                    continue
        
        # 통계 계산
        stats = {}
        for op, durations in operations.items():
            stats[op] = {
                'count': len(durations),
                'avg_ms': round(sum(durations) / len(durations), 2),
                'max_ms': max(durations),
                'min_ms': min(durations)
            }
        
        return stats
    
    def analyze_user_activity(self, hours=24):
        """사용자 활동 분석"""
        access_file = self.log_dir / "access.log"
        
        if not access_file.exists():
            return {"message": "Access log file not found"}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        activities = []
        
        with open(access_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    if timestamp_match:
                        timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                        if timestamp >= cutoff_time:
                            json_match = re.search(r'\{.*\}', line)
                            if json_match:
                                data = json.loads(json_match.group())
                                activities.append({
                                    'timestamp': timestamp,
                                    'user_id': data.get('user_id'),
                                    'action': data.get('action'),
                                    'session_id': data.get('session_id')
                                })
                except Exception:
                    continue
        
        # 분석
        unique_users = len(set(a['user_id'] for a in activities))
        unique_sessions = len(set(a['session_id'] for a in activities))
        action_counts = Counter(a['action'] for a in activities)
        
        return {
            'total_activities': len(activities),
            'unique_users': unique_users,
            'unique_sessions': unique_sessions,
            'top_actions': dict(action_counts.most_common(10))
        }
    
    def generate_report(self, hours=24):
        """종합 보고서 생성"""
        return {
            'analysis_period': f"Last {hours} hours",
            'timestamp': datetime.now().isoformat(),
            'errors': self.analyze_errors(hours),
            'performance': self.analyze_performance(hours),
            'user_activity': self.analyze_user_activity(hours)
        }


class LogManager:
    """로그 관리 도구"""
    
    def __init__(self, log_dir="/var/log/streamlit-app"):
        self.log_dir = Path(log_dir)
    
    def cleanup_old_logs(self, days=30):
        """오래된 로그 파일 정리"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_files = []
        
        for log_file in self.log_dir.glob("*.log.*"):  # 로테이션된 파일들
            try:
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_mtime < cutoff_date:
                    log_file.unlink()
                    cleaned_files.append(str(log_file))
            except Exception as e:
                print(f"Error cleaning {log_file}: {e}")
        
        return cleaned_files
    
    def get_log_sizes(self):
        """로그 파일 크기 정보"""
        sizes = {}
        for log_file in self.log_dir.glob("*.log"):
            try:
                size_mb = log_file.stat().st_size / (1024 * 1024)
                sizes[log_file.name] = round(size_mb, 2)
            except Exception:
                sizes[log_file.name] = 0
        
        return sizes
    
    def backup_logs(self, backup_dir="/backup/streamlit-logs"):
        """로그 백업"""
        import shutil
        
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = backup_path / f"backup_{timestamp}"
        backup_subdir.mkdir()
        
        backed_up_files = []
        for log_file in self.log_dir.glob("*.log"):
            try:
                shutil.copy2(log_file, backup_subdir)
                backed_up_files.append(str(log_file))
            except Exception as e:
                print(f"Error backing up {log_file}: {e}")
        
        return str(backup_subdir), backed_up_files


# === 실행 스크립트 ===

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Streamlit Log Analysis Tool')
    parser.add_argument('--analyze', action='store_true', help='Analyze logs')
    parser.add_argument('--cleanup', type=int, default=30, help='Cleanup logs older than N days')
    parser.add_argument('--backup', action='store_true', help='Backup current logs')
    parser.add_argument('--hours', type=int, default=24, help='Analysis period in hours')
    parser.add_argument('--log-dir', default='/var/log/streamlit-app', help='Log directory path')
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer(args.log_dir)
    manager = LogManager(args.log_dir)
    
    if args.analyze:
        print("=== Log Analysis Report ===")
        report = analyzer.generate_report(args.hours)
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    if args.cleanup:
        print(f"=== Cleaning up logs older than {args.cleanup} days ===")
        cleaned = manager.cleanup_old_logs(args.cleanup)
        print(f"Cleaned {len(cleaned)} files")
        for file in cleaned:
            print(f"  - {file}")
    
    if args.backup:
        print("=== Backing up logs ===")
        backup_dir, backed_up = manager.backup_logs()
        print(f"Backup created: {backup_dir}")
        print(f"Backed up {len(backed_up)} files")
    
    # 로그 파일 크기 정보
    print("=== Log File Sizes ===")
    sizes = manager.get_log_sizes()
    for filename, size_mb in sizes.items():
        print(f"{filename}: {size_mb} MB")


if __name__ == "__main__":
    main()
