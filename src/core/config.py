import os
import yaml
from typing import Dict, Any

class Config:
    """Configuration class for the application."""
    
    def __init__(self):
        self.production_mode = self._get_production_mode()
        self.mock_files_dir = self._get_mock_files_dir()
        self.categories = self._load_categories()

    def _load_categories(self) -> Dict[str, Any]:
        """Load categories from the YAML file."""
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        categories_path = os.path.join(project_root, 'config', 'categories.yaml')
        with open(categories_path, 'r') as f:
            return yaml.safe_load(f)['categories']

    def get_categories(self) -> Dict[str, Any]:
        """Get the loaded categories."""
        return self.categories

    def _get_production_mode(self) -> bool:
        """Get production mode from environment variable."""
        return os.getenv('PRODUCTION_MODE', 'false').lower() == 'true'
    
    def _get_mock_files_dir(self) -> str:
        """Get the directory containing mock HTML files."""
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(project_root, 'tests', 'mocks')
    
    def is_production(self) -> bool:
        """Check if the application is running in production mode."""
        return self.production_mode
    
    def get_mock_files_dir(self) -> str:
        """Get the directory path for mock files."""
        return self.mock_files_dir
    
    def get_mock_file_path(self, site_name: str, category: str) -> str:
        """Get the expected mock file path for a given site and category."""
        filename = f"{site_name}_{category}.html"
        return os.path.join(self.mock_files_dir, filename)

# Global config instance
config = Config() 