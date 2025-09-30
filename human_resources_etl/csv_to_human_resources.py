#!/usr/bin/env python3
"""
CSV轉換為human_resources API插入腳本

此腳本將CSV檔案中的受災情形資料轉換為符合human_resources schema的格式，
並透過POST API一筆一筆插入到資料庫。

功能特點:
- 智能資料轉換：根據泥沙淤積程度判斷所需人力數量和類型
- 資料對應邏輯：地址→工作地點，淤積程度→人力需求，清潔狀況→完成度
- API整合：使用requests庫發送POST請求，包含錯誤處理和進度報告

使用方法:
1. 基本使用：
   python csv_to_human_resources.py --csv "花蓮光復鄉家戶受災情形.csv" --api-url "http://localhost:8080"

2. 乾跑模式（只解析不發送API請求）：
   python csv_to_human_resources.py --csv "檔案路徑.csv" --api-url "http://localhost:8080" --dry-run

3. 指定批次大小：
   python csv_to_human_resources.py --csv "檔案路徑.csv" --api-url "http://localhost:8080" --batch-size 10

4. 查看幫助：
   python csv_to_human_resources.py --help

參數說明:
--csv: CSV檔案路徑（必填）
--api-url: API基礎URL，例如 http://localhost:8080（必填）
--batch-size: 批次處理大小，預設為1（選填）
--dry-run: 乾跑模式，只解析不發送請求（選填）

範例CSV格式:
地址,家戶內泥沙淤積程度現況（公分）,屋內大型廢棄家具是否已移除,是否進入一般清潔階段,需求參考的分級與顏色,最後更新日期,最後更新時間
光復鄉中正路一段100號,0,是,是,6級,2025/9/28,11:00
光復鄉中正路一段102號,0～10,否,是,5級,2025/9/28,11:00

注意事項:
- 請確保API服務正在運行
- 建議先使用 --dry-run 模式測試資料解析
- 腳本會自動跳過空行和無效資料
- 每次API請求間隔0.5秒以避免過於頻繁
"""

import csv
import json
import time
import uuid
import argparse
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional


class CSVToHumanResourcesConverter:
    def __init__(self, api_base_url: str, batch_size: int = 1):
        self.api_base_url = api_base_url.rstrip('/')
        self.batch_size = batch_size
        self.success_count = 0
        self.error_count = 0
        self.errors = []

    def parse_csv_row(self, row: Dict[str, str], row_number: int) -> Optional[Dict[str, Any]]:
        """
        將CSV行資料轉換為human_resources schema格式

        CSV欄位對應:
        - 地址 -> address (工作地點地址)
        - 家戶內泥沙淤積程度現況（公分） -> 根據淤積程度推斷所需人力類型和數量
        - 屋內大型廢棄家具是否已移除 -> 影響是否需要搬運志工
        - 是否進入一般清潔階段 -> 影響所需清潔人力
        - 需求參考的分級與顏色 -> 優先級和緊急程度
        - 最後更新日期/時間 -> updated_at
        """
        try:
            # 跳過空行或無效資料
            address = row.get('地址', '').strip()
            if not address:
                return None

            # 解析淤積程度
            mud_level = row.get('家戶內泥沙淤積程度現況（公分）', '').strip()
            furniture_removed = row.get('屋內大型廢棄家具是否已移除', '').strip()
            cleaning_stage = row.get('是否進入一般清潔階段', '').strip()
            priority_level = row.get('需求參考的分級與顏色', '').strip()
            last_update_date = row.get('最後更新日期', '').strip()
            last_update_time = row.get('最後更新時間', '').strip()

            # 根據淤積程度判斷所需人力
            headcount_need = self._calculate_headcount_by_mud_level(mud_level)
            role_type = self._determine_role_type(mud_level, furniture_removed, cleaning_stage)
            role_name = self._determine_role_name(mud_level, furniture_removed, cleaning_stage)

            # 判斷完成狀態
            is_completed = cleaning_stage == "是" and furniture_removed == "是"
            status = "completed" if is_completed else "active"
            role_status = "completed" if is_completed else "pending"
            headcount_got = headcount_need if is_completed else 0

            # 解析更新時間
            updated_at = self._parse_datetime(last_update_date, last_update_time)

            # 根據等級判斷緊急程度
            is_urgent = priority_level in ["1級", "2級", "3級"]

            # 生成唯一ID
            record_id = f"hr-{uuid.uuid4()}"

            human_resource_record = {
                "id": record_id,
                "org": "光復鄉災後重建志工隊",  # 預設組織名稱
                "address": address,
                "phone": "03-8701129",  # 預設聯絡電話（光復鄉公所）
                "status": status,
                "is_completed": is_completed,
                "has_medical": False,  # 預設非醫療需求
                "created_at": int(time.time()),
                "updated_at": updated_at,
                "role_name": role_name,
                "role_type": role_type,
                "skills": self._get_required_skills(mud_level, furniture_removed),
                "certifications": [],
                "experience_level": self._get_experience_level(mud_level),
                "language_requirements": ["中文"],
                "headcount_need": headcount_need,
                "headcount_got": headcount_got,
                "headcount_unit": "人",
                "role_status": role_status,
                # 統計欄位，實際使用時可能需要從其他來源計算
                "total_roles_in_request": 1,
                "completed_roles_in_request": 1 if is_completed else 0,
                "pending_roles_in_request": 0 if is_completed else 1,
                "total_requests": 0,  # 需要實際統計
                "active_requests": 0,  # 需要實際統計
                "completed_requests": 0,  # 需要實際統計
                "cancelled_requests": 0,  # 需要實際統計
                "total_roles": 0,  # 需要實際統計
                "completed_roles": 0,  # 需要實際統計
                "pending_roles": 0,  # 需要實際統計
                "urgent_requests": 1 if is_urgent else 0,
                "medical_requests": 0
            }

            return human_resource_record

        except Exception as e:
            print(f"第 {row_number} 行資料解析錯誤: {e}")
            return None

    def _calculate_headcount_by_mud_level(self, mud_level: str) -> int:
        """根據淤積程度計算所需人力數量"""
        if "50以上" in mud_level:
            return 8  # 嚴重淤積需要較多人力
        elif "30～50" in mud_level:
            return 6
        elif "10～30" in mud_level:
            return 4
        elif "0～10" in mud_level:
            return 2
        elif mud_level == "0":
            return 1  # 輕微清潔
        else:
            return 2  # 預設值

    def _determine_role_type(self, mud_level: str, furniture_removed: str, cleaning_stage: str) -> str:
        """根據災情判斷人力類型"""
        if "50以上" in mud_level or "30～50" in mud_level:
            return "一般志工"  # 需要大量清理工作
        elif furniture_removed == "否":
            return "一般志工"  # 需要搬運大型家具
        elif cleaning_stage == "否":
            return "一般志工"  # 需要清潔工作
        else:
            return "一般志工"  # 預設為一般志工

    def _determine_role_name(self, mud_level: str, furniture_removed: str, cleaning_stage: str) -> str:
        """根據災情判斷具體角色名稱"""
        if "50以上" in mud_level or "30～50" in mud_level:
            return "重度清理志工"
        elif furniture_removed == "否":
            return "搬運志工"
        elif cleaning_stage == "否":
            return "清潔志工"
        else:
            return "一般協助志工"

    def _get_required_skills(self, mud_level: str, furniture_removed: str) -> List[str]:
        """根據工作內容決定所需技能"""
        skills = []

        if furniture_removed == "否":
            skills.extend(["搬運", "體力勞動"])

        if "50以上" in mud_level or "30～50" in mud_level:
            skills.extend(["清理", "泥沙清除", "體力勞動"])
        elif "10～30" in mud_level or "0～10" in mud_level:
            skills.extend(["清潔", "整理"])

        return skills if skills else ["一般協助"]

    def _get_experience_level(self, mud_level: str) -> str:
        """根據工作難度決定經驗需求"""
        if "50以上" in mud_level:
            return "level_2"  # 需要有經驗
        elif "30～50" in mud_level or "10～30" in mud_level:
            return "level_1"  # 基礎經驗即可
        else:
            return "level_1"  # 預設基礎經驗

    def _parse_datetime(self, date_str: str, time_str: str) -> int:
        """解析日期時間字串，返回Unix timestamp"""
        try:
            if not date_str or not time_str:
                return int(time.time())

            # 處理日期格式 "2025/9/28" -> "2025-09-28"
            if '/' in date_str:
                date_parts = date_str.split('/')
                if len(date_parts) == 3:
                    year, month, day = date_parts
                    date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            # 處理時間格式 "11:00" -> "11:00:00"
            if ':' in time_str and len(time_str.split(':')) == 2:
                time_str += ":00"

            datetime_str = f"{date_str} {time_str}"
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            return int(dt.timestamp())

        except Exception as e:
            print(f"日期時間解析錯誤: {e}, 使用當前時間")
            return int(time.time())

    def read_csv(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """讀取CSV檔案並轉換為human_resources格式"""
        records = []

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                # 檢測CSV dialect
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter

                reader = csv.DictReader(file, delimiter=delimiter)

                for row_number, row in enumerate(reader, start=2):  # 從第2行開始（第1行是header）
                    record = self.parse_csv_row(row, row_number)
                    if record:
                        records.append(record)

        except FileNotFoundError:
            print(f"錯誤: 找不到檔案 {csv_file_path}")
            return []
        except Exception as e:
            print(f"讀取CSV檔案時發生錯誤: {e}")
            return []

        print(f"成功解析 {len(records)} 筆記錄")
        return records

    def post_record(self, record: Dict[str, Any]) -> bool:
        """發送單筆記錄到API"""
        try:
            url = f"{self.api_base_url}/resources/human_resources"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            response = requests.post(url, json=record, headers=headers, timeout=30)

            if response.status_code == 201:
                self.success_count += 1
                print(f"✓ 成功插入記錄 ID: {record['id']}")
                return True
            else:
                self.error_count += 1
                error_msg = f"API回應錯誤 {response.status_code}: {response.text}"
                self.errors.append({
                    'record_id': record['id'],
                    'error': error_msg
                })
                print(f"✗ 插入失敗 ID: {record['id']}, 錯誤: {error_msg}")
                return False

        except requests.RequestException as e:
            self.error_count += 1
            error_msg = f"網路請求錯誤: {e}"
            self.errors.append({
                'record_id': record['id'],
                'error': error_msg
            })
            print(f"✗ 插入失敗 ID: {record['id']}, 錯誤: {error_msg}")
            return False

    def process_records(self, records: List[Dict[str, Any]]) -> None:
        """處理所有記錄，逐一發送到API"""
        total_records = len(records)
        print(f"\n開始處理 {total_records} 筆記錄...")
        print("=" * 60)

        for i, record in enumerate(records, 1):
            print(f"[{i}/{total_records}] 處理地址: {record['address']}")

            success = self.post_record(record)

            # 避免API請求過於頻繁
            if i < total_records:
                time.sleep(0.5)  # 每次請求間隔0.5秒

        self.print_summary()

    def print_summary(self) -> None:
        """印出處理結果摘要"""
        print("\n" + "=" * 60)
        print("處理結果摘要:")
        print(f"成功插入: {self.success_count} 筆")
        print(f"失敗: {self.error_count} 筆")
        print(f"總計: {self.success_count + self.error_count} 筆")

        if self.errors:
            print(f"\n錯誤詳情:")
            for error in self.errors[:10]:  # 只顯示前10個錯誤
                print(f"  - ID: {error['record_id']}, 錯誤: {error['error']}")

            if len(self.errors) > 10:
                print(f"  ... 還有 {len(self.errors) - 10} 個錯誤")


def main():
    parser = argparse.ArgumentParser(description='將CSV檔案轉換並插入到human_resources API')
    parser.add_argument('--csv', required=True, help='CSV檔案路徑')
    parser.add_argument('--api-url', required=True, help='API基礎URL（例如: http://localhost:8080）')
    parser.add_argument('--batch-size', type=int, default=1, help='批次處理大小（預設: 1）')
    parser.add_argument('--dry-run', action='store_true', help='乾跑模式，只解析不發送API請求')

    args = parser.parse_args()

    # 建立轉換器
    converter = CSVToHumanResourcesConverter(args.api_url, args.batch_size)

    # 讀取並解析CSV
    records = converter.read_csv(args.csv)

    if not records:
        print("沒有有效的記錄需要處理")
        return

    if args.dry_run:
        print(f"\n乾跑模式: 已解析 {len(records)} 筆記錄，不會發送API請求")
        print("範例記錄:")
        if records:
            print(json.dumps(records[0], indent=2, ensure_ascii=False))
    else:
        # 確認是否繼續
        print(f"\n準備將 {len(records)} 筆記錄插入到 {args.api_url}/resources/human_resources")
        confirm = input("確定要繼續嗎？(y/N): ")

        if confirm.lower() == 'y':
            converter.process_records(records)
        else:
            print("操作已取消")


if __name__ == "__main__":
    main()