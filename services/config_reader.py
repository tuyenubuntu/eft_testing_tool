import os
import sys
import xml.etree.ElementTree as ET


class ConfigReader:
    def __init__(self, config_dir="configs"):
        """
        Automatically determine the base directory based on whether the application is frozen (packaged) or running as a script.
        :param config_dir: str, the subdirectory where configuration files are stored.
        """
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.config_dir = os.path.join(base_dir, config_dir)
        
        

    def _parse_xml(self, filename):
        """
        Internal function to parse XML file and check its existence.
        :param filename: str, the name of the XML file to parse.
        :return: ElementTree root element.
        """
        file_path = os.path.join(self.config_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        tree = ET.parse(file_path)
        return tree.getroot()

    def get_general_configs(self, filename="configuration.xml"):
        """
        Documents the general configuration settings from configuration.xml.
        :param filename: str, the name of the XML file to read.
        """
        root = self._parse_xml(filename)

        def extract_items(tag_name):
            return [
                item.text.strip()
                for item in root.findall(f"{tag_name}/Item")
                if item.text
            ]

        return {
            "eft_machines": extract_items("EFTMachines"),
            "task_names": extract_items("TaskNames"),
            "element_types": extract_items("ElementTypes"),
            "lines": extract_items("Lines"),
            "processes": extract_items("Processes"),
            "axes": extract_items("Axes"),
            "requested_by": extract_items("RequestedBy"),
        }

    def get_all_element_forces(self, filename="element_config.xml"):
        """
        Read the entire force lookup table from element_config.xml.
        Return a dictionary in the format: {'24-6': '300', '28-10': '400', ...}
        """
        root = self._parse_xml(filename)
        forces = {}
        for elem in root.findall("Element"):
            elem_type = elem.get("type")
            force_node = elem.find("force")
            if elem_type and force_node is not None and force_node.text:
                forces[elem_type] = force_node.text.strip()
        return forces

    def get_force_by_element(self, element_type, filename="element_config.xml"):
        """
        Get the force value for a specific element type.
        :param element_type: str, the type of the element.
        :param filename: str, the name of the XML file to read.
        :return: str or None, the force value if found, otherwise None.
        """
        forces = self.get_all_element_forces(filename)
        return forces.get(element_type, None)

    def get_path_configs(self, filename="path_config.xml"):
        """
        Read all child nodes directly in path_config.xml into a dictionary.
        Example: <OutputDir>D:/Data</OutputDir> -> {'OutputDir': 'D:/Data'}
        """
        root = self._parse_xml(filename)
        return {
            child.tag: child.text.strip() if child.text else ""
            for child in root
        }

    def get_test_files_dir(self, filename="path_config.xml"):
        """Get the directory path for test files."""
        paths = self.get_path_configs(filename)
        return paths.get("TestFiles", "")
    
    def get_setting_judgment(self, filename="setting_judgment.xml"):
        """
        Read the judgment settings from setting_judgment.xml.
        Example: <default_cycle>2500000</default_cycle> -> {'default_cycle': '2500000'}
        """
        root = self._parse_xml(filename)
        return {
            child.tag: child.text.strip() if child.text else ""
            for child in root
        }
    
    def get_default_cycle(self, filename="setting_judgment.xml"):
        """Get the default cycle value from setting_judgment.xml."""
        settings = self.get_setting_judgment(filename)
        return settings.get("default_cycle", "")
    
    def get_adjust_force(self, filename="setting_judgment.xml"):
        """Get the adjust force value from setting_judgment.xml."""
        settings = self.get_setting_judgment(filename)
        return settings.get("adjust_force", "")