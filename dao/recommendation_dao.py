"""
Data Access Object (DAO) for stock recommendations.
Handles storage and retrieval of stock recommendation data with enriched schema.
"""

import os
import json
from typing import List, Dict, Optional


class Stock:
    """Represents a single stock recommendation"""
    
    def __init__(self, id: str, sentiment: str, TP: Optional[float] = None, 
                 SL: Optional[float] = None, name: Optional[str] = None):
        self.id = str(id)
        self.sentiment = sentiment  # STRONG_BUY, BUY, NEUTRAL, SELL
        self.TP = TP  # Target Price
        self.SL = SL  # Stop Loss
        self.name = name
    
    def to_dict(self) -> Dict:
        """Convert to dictionary, excluding None values"""
        result = {
            "id": self.id,
            "sentiment": self.sentiment
        }
        if self.TP is not None:
            result["TP"] = self.TP
        if self.SL is not None:
            result["SL"] = self.SL
        if self.name is not None:
            result["name"] = self.name
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Stock':
        """Create Stock instance from dictionary"""
        return cls(
            id=str(data.get('id')),
            sentiment=data.get('sentiment', 'NEUTRAL'),
            TP=data.get('TP'),
            SL=data.get('SL'),
            name=data.get('name')
        )


class RecommendationRecord:
    """Represents a recommendation record for a specific date"""
    
    def __init__(self, date: str, stocks: List[Stock] = None):
        self.date = date  # YYYY-MM-DD format
        self.stocks = stocks or []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "date": self.date,
            "stocks": [stock.to_dict() for stock in self.stocks]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RecommendationRecord':
        """Create RecommendationRecord instance from dictionary"""
        stocks = [
            Stock.from_dict(stock_data) 
            for stock_data in data.get('stocks', [])
        ]
        return cls(
            date=data.get('date'),
            stocks=stocks
        )


class RecommendationDAO:
    """Data Access Object for managing stock recommendations"""
    
    def __init__(self, file_path: str):
        """
        Initialize DAO with file path
        
        Args:
            file_path: Path to the JSON file storing recommendations
        """
        self.file_path = file_path
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Ensure the directory for the file exists"""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    def load(self) -> List[RecommendationRecord]:
        """
        Load all recommendation records from file
        
        Returns:
            List of RecommendationRecord objects sorted by date
        """
        if not os.path.exists(self.file_path):
            return []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            records = [RecommendationRecord.from_dict(item) for item in data]
            records.sort(key=lambda r: r.date)
            return records
        except Exception as e:
            raise IOError(f"Failed to load recommendations from {self.file_path}: {e}")
    
    def save(self, records: List[RecommendationRecord]) -> None:
        """
        Save recommendation records to file
        
        Args:
            records: List of RecommendationRecord objects to save
        """
        self._ensure_directory()
        
        try:
            # Sort by date before saving
            sorted_records = sorted(records, key=lambda r: r.date)
            data = [record.to_dict() for record in sorted_records]
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            raise IOError(f"Failed to save recommendations to {self.file_path}: {e}")
    
    def add_record(self, record: RecommendationRecord) -> None:
        """
        Add a single recommendation record
        
        Args:
            record: RecommendationRecord to add
        """
        records = self.load()
        
        # Remove existing record for the same date if present
        records = [r for r in records if r.date != record.date]
        
        # Add new record
        records.append(record)
        
        self.save(records)
    
    def get_by_date(self, date: str) -> Optional[RecommendationRecord]:
        """
        Get recommendation record by date
        
        Args:
            date: Date string in YYYY-MM-DD format
        
        Returns:
            RecommendationRecord or None if not found
        """
        records = self.load()
        for record in records:
            if record.date == date:
                return record
        return None
    
    def get_latest(self) -> Optional[RecommendationRecord]:
        """
        Get the latest recommendation record
        
        Returns:
            Latest RecommendationRecord or None if empty
        """
        records = self.load()
        return records[-1] if records else None
    
    def get_stock_ids(self, date: str) -> List[str]:
        """
        Get list of stock IDs for a specific date
        
        Args:
            date: Date string in YYYY-MM-DD format
        
        Returns:
            List of stock ID strings
        """
        record = self.get_by_date(date)
        return [stock.id for stock in record.stocks] if record else []
    
    def delete_by_date(self, date: str) -> None:
        """
        Delete recommendation record by date
        
        Args:
            date: Date string in YYYY-MM-DD format
        """
        records = self.load()
        records = [r for r in records if r.date != date]
        self.save(records)
