"""Configuration model for managing setting.json file.

This module provides functionality to load, save, and validate
the application configuration stored in setting.json.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List


class Configuration:
    """Manages application configuration from setting.json file.
    
    This class handles loading, saving, and validation of the configuration
    file. All cell mappings and file paths are managed through this class
    to avoid hardcoding (Constitution principle I).
    
    Attributes:
        config_path: Path to the setting.json file
        data: Dictionary containing the configuration data
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Configuration with optional config file path.
        
        Args:
            config_path: Path to setting.json file. If None, uses
                        'setting.json' in the repository root.
        """
        if config_path is None:
            # Get repository root (parent of src/)
            repo_root = Path(__file__).parent.parent.parent
            config_path = repo_root / "setting.json"
        
        self.config_path = Path(config_path)
        self.data: Dict[str, Any] = {}
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from setting.json file.
        
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If setting.json file doesn't exist
            json.JSONDecodeError: If JSON file is invalid
        """
        if not self.config_path.exists():
            # Create default configuration if file doesn't exist
            self._create_default()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # Ensure company_mappings field exists
        if "company_mappings" not in self.data:
            self.data["company_mappings"] = {}
        
        # Ensure current_company field exists
        if "current_company" not in self.data:
            self.data["current_company"] = ""
        
        self._validate()
        return self.data
    
    def save(self) -> None:
        """Save current configuration to setting.json file.
        
        Raises:
            IOError: If file cannot be written
        """
        self._validate()
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def get_statement_template_path(self) -> str:
        """Get the statement template file path from configuration.
        
        Returns:
            Path to statement template file (empty string if not set)
        """
        return self.data.get("statement_template_path", "")
    
    def set_statement_template_path(self, path: str) -> None:
        """Set the statement template file path in configuration.
        
        Args:
            path: Path to statement template file
        """
        if "statement_template_path" not in self.data:
            self.data["statement_template_path"] = ""
        self.data["statement_template_path"] = path
    
    def get_cell_mappings(self, company_name: Optional[str] = None) -> Dict[str, Any]:
        """Get cell mapping configuration for a specific company or default.
        
        Args:
            company_name: Company name to get mappings for. If None, returns default mappings.
            
        Returns:
            Dictionary containing cell mapping settings
        """
        if company_name:
            company_mappings = self.data.get("company_mappings", {})
            if company_name in company_mappings:
                return company_mappings[company_name]
        
        return self.data.get("cell_mappings", {})
    
    def set_cell_mappings(self, mappings: Dict[str, Any], company_name: Optional[str] = None) -> None:
        """Set cell mapping configuration for a specific company or default.
        
        Args:
            mappings: Dictionary containing cell mapping settings
            company_name: Company name to save mappings for. If None, saves as default.
        """
        if company_name:
            if "company_mappings" not in self.data:
                self.data["company_mappings"] = {}
            self.data["company_mappings"][company_name] = mappings
        else:
            self.data["cell_mappings"] = mappings
    
    def get_company_list(self) -> List[str]:
        """Get list of all company names with saved mappings.
        
        Returns:
            List of company names
        """
        company_mappings = self.data.get("company_mappings", {})
        return list(company_mappings.keys())
    
    def has_company_mapping(self, company_name: str) -> bool:
        """Check if mapping exists for a company.
        
        Args:
            company_name: Company name to check
            
        Returns:
            True if mapping exists, False otherwise
        """
        company_mappings = self.data.get("company_mappings", {})
        return company_name in company_mappings
    
    def get_current_company(self) -> str:
        """Get currently selected company name.
        
        Returns:
            Company name (empty string if none selected)
        """
        return self.data.get("current_company", "")
    
    def set_current_company(self, company_name: str) -> None:
        """Set currently selected company name.
        
        Args:
            company_name: Company name to set as current
        """
        self.data["current_company"] = company_name
    
    def _validate(self) -> None:
        """Validate configuration structure.
        
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Ensure company_mappings exists
        if "company_mappings" not in self.data:
            self.data["company_mappings"] = {}
        
        # Ensure current_company exists
        if "current_company" not in self.data:
            self.data["current_company"] = ""
        
        if "cell_mappings" not in self.data:
            raise ValueError("cell_mappings is required in configuration")
        
        cell_mappings = self.data["cell_mappings"]
        required_fields = [
            "settlement_input_range",
            "settlement_data_columns",
            "statement_output_columns",
            "statement_start_row",
            "statement_fixed_values"
        ]
        
        for field in required_fields:
            if field not in cell_mappings:
                raise ValueError(f"Required field '{field}' missing in cell_mappings")
        
        # Validate company_mappings structure if any exist
        for company_name, mappings in self.data.get("company_mappings", {}).items():
            for field in required_fields:
                if field not in mappings:
                    raise ValueError(f"Required field '{field}' missing in company_mappings['{company_name}']")
    
    def _create_default(self) -> None:
        """Create default configuration structure."""
        self.data = {
            "statement_template_path": "",
            "current_company": "",
            "cell_mappings": {
                "settlement_input_range": "B1:B100",
                "settlement_data_columns": ["C", "I", "J", "K"],
                "statement_output_columns": ["E", "H", "J", "K"],
                "statement_start_row": 2,
                "statement_fixed_values": {
                    "column_d": 940918,
                    "column_g": 1,
                    "column_i": 3
                }
            },
            "company_mappings": {}
        }
        self.save()

