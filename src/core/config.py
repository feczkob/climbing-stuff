import os
from typing import Dict, Any

class Config:
    """Configuration class for the application."""
    
    def __init__(self):
        self.production_mode = self._get_production_mode()
        self.mock_files_dir = self._get_mock_files_dir()
    
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
        # Map category names to URL path segments
        category_paths = {
            'ropes': 'climbing_ropes',
            'friends-nuts': 'camming_devices_friends',  # This would need separate files for each
            'slings': 'slings_cord',
            'carabiners-quickdraws': 'carabiners_quickdraws'
        }
        
        path_segment = category_paths.get(category, category.replace('-', '_'))
        
        # Map site names to domain patterns
        site_patterns = {
            'bergfreunde': f'bergfreunde_bergfreunde_eu_{path_segment}',
            'mountex': f'mountex_mountex_hu_sziklamaszas_hegymaszas',
            '4camping': f'4camping_4camping_hu_c_maszokoetelek'  # Fixed for ropes category
        }
        
        pattern = site_patterns.get(site_name, f'{site_name}_{path_segment}')
        return os.path.join(self.mock_files_dir, f'{pattern}.html')

# Global config instance
config = Config() 