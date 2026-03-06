"""
Parser for Java interface files to extract API documentation.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ParsedParameter:
    """Represents a method parameter."""

    name: str
    type: str
    description: Optional[str] = None


@dataclass
class ParsedMethod:
    """Represents a parsed method from Java interface."""

    name: str
    return_type: str
    signature: str
    parameters: List[ParsedParameter] = field(default_factory=list)
    description: Optional[str] = None
    javadoc: Optional[str] = None
    exceptions: List[str] = field(default_factory=list)
    is_static: bool = False
    is_default: bool = False
    annotations: List[str] = field(default_factory=list)


@dataclass
class ParsedInterface:
    """Represents a parsed Java interface."""

    name: str
    package: str
    fully_qualified_name: str
    description: Optional[str] = None
    javadoc: Optional[str] = None
    methods: List[ParsedMethod] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    extends: List[str] = field(default_factory=list)
    file_path: Optional[str] = None
    is_public: bool = True


class JavaInterfaceParser:
    """Parser for Java interface files."""

    def __init__(self, base_path: Path):
        self.base_path = base_path

    def parse_file(self, file_path: Path) -> Optional[ParsedInterface]:
        """Parse a single Java interface file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            return self._parse_content(content, str(file_path))
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def _parse_content(self, content: str, file_path: str) -> Optional[ParsedInterface]:
        """Parse Java file content."""
        # Skip if not an interface or contains no interface definition
        if "interface " not in content:
            return None

        # Extract package
        package_match = re.search(r"package\s+([\w.]+);", content)
        package = package_match.group(1) if package_match else "default"

        # Extract imports
        imports = re.findall(r"import\s+(?:static\s+)?([\w.*]+);", content)

        # Find interface definition
        interface_pattern = (
            r"((?:public\s+)?interface\s+(\w+)(?:\s+extends\s+([\w,\s]+))?)\s*\{"
        )
        interface_match = re.search(interface_pattern, content, re.DOTALL)

        if not interface_match:
            return None

        interface_decl = interface_match.group(1)
        interface_name = interface_match.group(2)
        extends_str = interface_match.group(3)

        extends = []
        if extends_str:
            extends = [e.strip() for e in extends_str.split(",")]

        is_public = "public" in interface_decl

        # Find the interface body (content between first { and last })
        start_idx = content.find("{", interface_match.end() - 1)
        end_idx = content.rfind("}")

        if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
            return None

        interface_body = content[start_idx + 1 : end_idx]

        # Extract class-level Javadoc
        javadoc = self._extract_javadoc(content, start_idx)
        description = self._extract_description_from_javadoc(javadoc)

        # Parse methods
        methods = self._parse_methods(interface_body)

        return ParsedInterface(
            name=interface_name,
            package=package,
            fully_qualified_name=f"{package}.{interface_name}",
            description=description,
            javadoc=javadoc,
            methods=methods,
            imports=imports,
            extends=extends,
            file_path=file_path,
            is_public=is_public,
        )

    def _extract_javadoc(self, content: str, position: int) -> Optional[str]:
        """Extract Javadoc comment before a given position."""
        # Look backwards for Javadoc
        before_content = content[:position]

        # Find the last Javadoc comment
        javadoc_pattern = r"/\*\*\s*(.*?)\s*\*/"
        matches = list(re.finditer(javadoc_pattern, before_content, re.DOTALL))

        if not matches:
            return None

        # Get the last match
        last_match = matches[-1]
        javadoc_text = last_match.group(1)

        # Clean up the Javadoc (remove leading * and spaces)
        lines = javadoc_text.split("\n")
        cleaned_lines = []
        for line in lines:
            # Remove leading whitespace and *
            cleaned = re.sub(r"^\s*\*?\s?", "", line)
            cleaned_lines.append(cleaned)

        return "\n".join(cleaned_lines).strip()

    def _extract_description_from_javadoc(
        self, javadoc: Optional[str]
    ) -> Optional[str]:
        """Extract the main description from Javadoc (before any @ tags)."""
        if not javadoc:
            return None

        # Split at first @ tag
        parts = re.split(r"\n?\s*@", javadoc, maxsplit=1)
        description = parts[0].strip()

        return description if description else None

    def _parse_methods(self, interface_body: str) -> List[ParsedMethod]:
        """Parse all methods from interface body."""
        methods = []

        # Method pattern (handles multiline signatures)
        # Matches: [annotations] [public] [static] [default] ReturnType methodName(params) [throws ...];
        method_pattern = r"""
            (?:^|\n)\s*                            # Start of line or newline
            ((?:\s*@\w+(?:\([^)]*\))?\s*)*)        # Annotations
            \s*(?:public\s+)?                      # Optional public
            \s*(static\s+)?                        # Optional static
            \s*(default\s+)?                       # Optional default
            \s*([\w\[\]<>?]+(?:\s+[\w\[\]<>?]+)*)  # Return type (handles complex types)
            \s+(\w+)                               # Method name
            \s*\(\s*([^)]*)\s*\)                  # Parameters
            \s*(?:throws\s+([\w,\s]+))?           # Optional throws
            \s*;                                   # End with semicolon
        """

        for match in re.finditer(
            method_pattern, interface_body, re.VERBOSE | re.MULTILINE
        ):
            annotations_str = match.group(1) or ""
            is_static = match.group(2) is not None
            is_default = match.group(3) is not None
            return_type = match.group(4).strip()
            method_name = match.group(5)
            params_str = match.group(6)
            exceptions_str = match.group(7)

            # Parse annotations
            annotations = re.findall(r"@(\w+)", annotations_str)

            # Parse parameters
            parameters = self._parse_parameters(params_str)

            # Parse exceptions
            exceptions = []
            if exceptions_str:
                exceptions = [e.strip() for e in exceptions_str.split(",")]

            # Build full signature
            signature = f"{return_type} {method_name}({params_str})"
            if exceptions:
                signature += f" throws {', '.join(exceptions)}"

            # Extract Javadoc for this method (look backwards from match position)
            method_start = match.start()
            before_method = interface_body[:method_start]
            javadoc = self._extract_javadoc(
                before_method + "/** */", len(before_method) + 5
            )
            description = self._extract_description_from_javadoc(javadoc)

            # Extract param docs from javadoc
            if javadoc:
                param_docs = self._extract_param_docs(javadoc)
                for param in parameters:
                    if param.name in param_docs:
                        param.description = param_docs[param.name]

            methods.append(
                ParsedMethod(
                    name=method_name,
                    return_type=return_type,
                    signature=signature,
                    parameters=parameters,
                    description=description,
                    javadoc=javadoc,
                    exceptions=exceptions,
                    is_static=is_static,
                    is_default=is_default,
                    annotations=annotations,
                )
            )

        return methods

    def _parse_parameters(self, params_str: str) -> List[ParsedParameter]:
        """Parse method parameters."""
        parameters = []

        if not params_str.strip():
            return parameters

        # Split by comma, but be careful of generic types like Map<String, String>
        # Simple approach: split on commas not inside <>
        params = []
        depth = 0
        current = ""
        for char in params_str:
            if char == "<":
                depth += 1
                current += char
            elif char == ">":
                depth -= 1
                current += char
            elif char == "," and depth == 0:
                params.append(current.strip())
                current = ""
            else:
                current += char
        if current.strip():
            params.append(current.strip())

        for param in params:
            # Handle final modifier and annotations
            param = re.sub(r"\s+final\s+", " ", param)
            param = re.sub(r"\s*@\w+\s*", " ", param)
            param = param.strip()

            if not param:
                continue

            # Match: Type name
            # Support generics and arrays
            parts = param.rsplit(" ", 1)
            if len(parts) == 2:
                param_type = parts[0].strip()
                param_name = parts[1].strip()
                parameters.append(ParsedParameter(name=param_name, type=param_type))

        return parameters

    def _extract_param_docs(self, javadoc: str) -> Dict[str, str]:
        """Extract @param documentation from Javadoc."""
        param_docs = {}
        for match in re.finditer(r"@param\s+(\w+)\s+([^@\n]*)", javadoc):
            param_name = match.group(1)
            description = match.group(2).strip()
            param_docs[param_name] = description
        return param_docs

    def parse_directory(self, directory: Path) -> List[ParsedInterface]:
        """Parse all Java files in a directory recursively."""
        interfaces = []

        for java_file in directory.rglob("*.java"):
            interface = self.parse_file(java_file)
            if interface:
                interfaces.append(interface)
                print(
                    f"Parsed: {interface.fully_qualified_name} ({len(interface.methods)} methods)"
                )

        return interfaces
