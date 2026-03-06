"""
Script to parse all Java API files and store in SQLite database.
"""

import sys
import json
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from burp_api_mcp.models import (
    init_db,
    get_session,
    Base,
    Package,
    Interface,
    Method,
    Import,
    interface_extends,
)
from burp_api_mcp.parser import JavaInterfaceParser


def import_to_database(interfaces: List, db_path: str = "burp_api.db"):
    """Import parsed interfaces to SQLite database."""
    engine = init_db(db_path)
    session = get_session(engine)

    try:
        # Track packages to avoid duplicates
        packages_cache = {}
        interfaces_cache = {}

        print(f"Importing {len(interfaces)} interfaces...")

        for parsed_iface in interfaces:
            # Create or get package
            package_parts = parsed_iface.package.split(".")
            current_package = None
            current_path = []

            for part in package_parts:
                current_path.append(part)
                package_name = ".".join(current_path)

                if package_name in packages_cache:
                    current_package = packages_cache[package_name]
                else:
                    package = Package(
                        name=package_name,
                        parent_id=current_package.id if current_package else None,
                    )
                    session.add(package)
                    session.flush()
                    packages_cache[package_name] = package
                    current_package = package

            # Create interface
            interface = Interface(
                name=parsed_iface.name,
                fully_qualified_name=parsed_iface.fully_qualified_name,
                package_id=current_package.id,
                description=parsed_iface.description,
                javadoc=parsed_iface.javadoc,
                file_path=parsed_iface.file_path,
                is_public=1 if parsed_iface.is_public else 0,
            )
            session.add(interface)
            session.flush()
            interfaces_cache[parsed_iface.fully_qualified_name] = interface

            # Add imports
            for import_stmt in parsed_iface.imports:
                import_obj = Import(
                    interface_id=interface.id, import_statement=import_stmt, is_static=0
                )
                session.add(import_obj)

            # Create methods
            for parsed_method in parsed_iface.methods:
                # Check if method already exists
                existing_method = (
                    session.query(Method)
                    .filter_by(
                        name=parsed_method.name, signature=parsed_method.signature
                    )
                    .first()
                )

                if existing_method:
                    method = existing_method
                else:
                    method = Method(
                        name=parsed_method.name,
                        signature=parsed_method.signature,
                        return_type=parsed_method.return_type,
                        description=parsed_method.description,
                        javadoc=parsed_method.javadoc,
                        parameters=json.dumps(
                            [
                                {
                                    "name": p.name,
                                    "type": p.type,
                                    "description": p.description,
                                }
                                for p in parsed_method.parameters
                            ]
                        ),
                        exceptions=json.dumps(parsed_method.exceptions),
                        is_static=1 if parsed_method.is_static else 0,
                        is_default=1 if parsed_method.is_default else 0,
                    )
                    session.add(method)
                    session.flush()

                # Associate method with interface
                interface.methods.append(method)

        # Second pass: handle extends relationships
        print("Processing inheritance relationships...")
        for parsed_iface in interfaces:
            if parsed_iface.extends:
                interface = interfaces_cache.get(parsed_iface.fully_qualified_name)
                if interface:
                    for extended_name in parsed_iface.extends:
                        # Try to find fully qualified name
                        extended_iface = None

                        # First, check if it's a fully qualified name
                        if extended_name in interfaces_cache:
                            extended_iface = interfaces_cache[extended_name]
                        else:
                            # Try to resolve from imports
                            for import_stmt in parsed_iface.imports:
                                if import_stmt.endswith(f".{extended_name}"):
                                    full_name = import_stmt
                                    if full_name in interfaces_cache:
                                        extended_iface = interfaces_cache[full_name]
                                        break

                            # Try same package
                            if not extended_iface:
                                same_package_name = (
                                    f"{parsed_iface.package}.{extended_name}"
                                )
                                if same_package_name in interfaces_cache:
                                    extended_iface = interfaces_cache[same_package_name]

                        if extended_iface:
                            interface.extends.append(extended_iface)

        session.commit()
        print(f"Successfully imported {len(interfaces)} interfaces to {db_path}")

        # Print statistics
        pkg_count = session.query(Package).count()
        iface_count = session.query(Interface).count()
        method_count = session.query(Method).count()

        print(f"\nDatabase statistics:")
        print(f"  - Packages: {pkg_count}")
        print(f"  - Interfaces: {iface_count}")
        print(f"  - Methods: {method_count}")

    except Exception as e:
        session.rollback()
        print(f"Error importing data: {e}")
        raise
    finally:
        session.close()


def main():
    """Main function to parse and import API documentation."""
    # Get the API directory
    api_dir = Path(__file__).parent.parent.parent / "api"

    if not api_dir.exists():
        print(f"Error: API directory not found at {api_dir}")
        print("Please run this script from the project root directory")
        sys.exit(1)

    print(f"Parsing Java files from: {api_dir}")

    # Parse all Java files
    parser = JavaInterfaceParser(api_dir)
    interfaces = parser.parse_directory(api_dir)

    if not interfaces:
        print("No interfaces found!")
        sys.exit(1)

    print(f"\nFound {len(interfaces)} interfaces")

    # Import to database
    db_path = Path(__file__).parent.parent / "burp_api.db"
    import_to_database(interfaces, str(db_path))


if __name__ == "__main__":
    main()
