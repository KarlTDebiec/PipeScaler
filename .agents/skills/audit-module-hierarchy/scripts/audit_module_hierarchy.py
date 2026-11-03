#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit dependency-aware ordering for package-level `__init__.py` hierarchy docs.

This script analyzes sibling imports and prints "bubble up" levels:
dependencies first, dependents later. It also reports cycles as SCC groups.
"""

from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path

__all__ = [
    "PackageAuditResult",
    "audit_one_package",
    "format_group",
    "get_child_names",
    "get_imported_sibling_from_import",
    "get_levels",
    "get_sibling_import_edges",
    "get_top_owner_name",
    "iter_package_dirs",
    "main",
    "parse_args",
    "print_result",
    "tarjan_scc",
    "to_dotted_name",
]


@dataclass(frozen=True)
class PackageAuditResult:
    """Dependency ordering and cycle information for one package.

    Attributes:
        package_dir_path: package directory analyzed
        levels: map of hierarchy level to grouped sibling names
        cycles: strongly connected sibling groups with two or more members
    """

    package_dir_path: Path
    """Package directory analyzed."""
    levels: dict[int, list[list[str]]]
    """Inferred minimum levels, grouping strongly connected components."""
    cycles: list[list[str]]
    """Sibling cycles, reported separately from valid independent peers."""


def audit_one_package(
    package_dir_path: Path, package_dotted: str
) -> PackageAuditResult:
    """Audit one package directory.

    Arguments:
        package_dir_path: package directory path
        package_dotted: dotted package name
    Returns:
        package audit result
    Raises:
        ValueError: if source cannot be parsed
        OSError: if source cannot be read
    """
    _parse_source(package_dir_path / "__init__.py")
    child_names = get_child_names(package_dir_path)
    edges = get_sibling_import_edges(package_dir_path, package_dotted, child_names)
    components = tarjan_scc(child_names, edges)
    levels = get_levels(components, edges)
    cycles = [group for group in components if len(group) > 1]
    return PackageAuditResult(
        package_dir_path=package_dir_path,
        levels=levels,
        cycles=sorted(cycles, key=lambda names: names[0]),
    )


def format_group(group: list[str]) -> str:
    """Format one level-group for display.

    Arguments:
        group: sibling names in same SCC group
    Returns:
        formatted group
    """
    return " / ".join(group)


def get_child_names(package_dir_path: Path) -> list[str]:
    """Get direct child module/subpackage names for a package directory.

    Arguments:
        package_dir_path: package directory path
    Returns:
        sorted child names
    """
    child_names: list[str] = []
    for child_path in package_dir_path.iterdir():
        if child_path.name == "__init__.py":
            continue
        if child_path.is_file() and child_path.suffix == ".py":
            child_names.append(child_path.stem)
        elif child_path.is_dir() and (child_path / "__init__.py").exists():
            child_names.append(child_path.name)
    return sorted(child_names)


def get_imported_sibling_from_import(
    imported_module: str,
    owner_name: str,
    child_names: list[str],
    package_prefix_parts: list[str],
) -> str | None:
    """Resolve sibling target from ast.Import, if any.

    Arguments:
        imported_module: imported module path
        owner_name: importer sibling name
        child_names: known sibling names
        package_prefix_parts: package path split by dots
    Returns:
        imported sibling name, or None
    """
    module_parts = imported_module.split(".")
    if module_parts[: len(package_prefix_parts)] != package_prefix_parts:
        return None
    if len(module_parts) <= len(package_prefix_parts):
        return None

    sibling_name = module_parts[len(package_prefix_parts)]
    if sibling_name in child_names and sibling_name != owner_name:
        return sibling_name
    return None


def get_levels(
    components: list[list[str]], edges: dict[str, set[str]]
) -> dict[int, list[list[str]]]:
    """Compute bubbled dependency levels for SCC components.

    Arguments:
        components: SCC groups
        edges: sibling import graph
    Returns:
        mapping of level to component groups at that level
    """
    component_index: dict[str, int] = {
        name: idx for idx, group in enumerate(components) for name in group
    }
    component_edges: dict[int, set[int]] = defaultdict(set)
    for importer_name, imported_names in edges.items():
        for imported_name in imported_names:
            importer_component = component_index[importer_name]
            imported_component = component_index[imported_name]
            if importer_component != imported_component:
                component_edges[importer_component].add(imported_component)

    @cache
    def level_for_component(component_id: int) -> int:
        """Get the dependency level of one strongly connected component.

        Arguments:
            component_id: component id
        Returns:
            dependency level of the component
        """
        imported_components = component_edges.get(component_id, set())
        if not imported_components:
            return 1
        return 1 + max(level_for_component(cid) for cid in imported_components)

    levels: dict[int, list[list[str]]] = defaultdict(list)
    for component_id, group in enumerate(components):
        levels[level_for_component(component_id)].append(group)

    return {
        level: sorted(groups, key=lambda names: names[0])
        for level, groups in sorted(levels.items())
    }


def get_sibling_import_edges(
    package_dir_path: Path,
    package_dotted: str,
    child_names: list[str],
) -> dict[str, set[str]]:
    """Build sibling import graph for one package.

    Graph edge direction is importer -> importee.

    Arguments:
        package_dir_path: package directory path
        package_dotted: dotted package name
        child_names: direct child module/subpackage names
    Returns:
        sibling import graph
    Raises:
        ValueError: if a source file cannot be parsed
        OSError: if a source file cannot be read
    """
    edges: dict[str, set[str]] = {name: set() for name in child_names}
    package_prefix_parts = package_dotted.split(".")

    candidate_files: list[Path] = []
    for child_name in child_names:
        child_path = package_dir_path / child_name
        if child_path.is_dir():
            candidate_files.extend(child_path.rglob("*.py"))
        else:
            candidate_files.append(package_dir_path / f"{child_name}.py")

    for file_path in candidate_files:
        owner_name = get_top_owner_name(package_dir_path, file_path)
        if owner_name is None or owner_name not in edges:
            continue

        tree = _parse_source(file_path)
        relative_parts = file_path.relative_to(package_dir_path).parts
        current_package_parts = package_prefix_parts + list(relative_parts[:-1])
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imported_modules = _get_imported_modules(node, current_package_parts)
            elif isinstance(node, ast.Import):
                imported_modules = [alias.name for alias in node.names]
            else:
                continue
            for imported_module in imported_modules:
                imported_name = get_imported_sibling_from_import(
                    imported_module, owner_name, child_names, package_prefix_parts
                )
                if imported_name is not None:
                    edges[owner_name].add(imported_name)

    return edges


def get_top_owner_name(package_dir_path: Path, file_path: Path) -> str | None:
    """Get child module owner name for a file under a package directory.

    Arguments:
        package_dir_path: package directory path
        file_path: file path under that package
    Returns:
        owner child name, or None if unavailable
    """
    relative_parts = file_path.relative_to(package_dir_path).parts
    if not relative_parts:
        return None
    first = relative_parts[0]
    if first == "__init__.py":
        return None
    return first.removesuffix(".py")


def iter_package_dirs(target_dir_path: Path, min_children: int) -> list[Path]:
    """Find package directories to audit.

    Arguments:
        target_dir_path: root package directory path
        min_children: minimum number of direct child modules/subpackages
    Returns:
        package directories to audit
    """
    package_dir_paths: list[Path] = []
    for init_path in sorted(target_dir_path.rglob("__init__.py")):
        package_dir_path = init_path.parent
        child_names = get_child_names(package_dir_path)
        if len(child_names) >= min_children:
            package_dir_paths.append(package_dir_path)
    return package_dir_paths


def main(argv: Sequence[str] | None = None):
    """Run the hierarchy audit without modifying package declarations.

    Arguments:
        argv: optional argument sequence
    Raises:
        SystemExit: if the target is invalid or source cannot be read or parsed
    """
    args = parse_args(argv)
    target_dir_path = args.target.resolve()
    try:
        if not target_dir_path.is_dir():
            raise FileNotFoundError(
                f"Target package directory not found: {target_dir_path}"
            )
        if not (target_dir_path / "__init__.py").is_file():
            raise ValueError(f"Target is not a package directory: {target_dir_path}")
        package_dir_paths = iter_package_dirs(target_dir_path, args.min_children)
        results = [
            audit_one_package(path, to_dotted_name(target_dir_path, path))
            for path in package_dir_paths
        ]
    except (OSError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    for result in results:
        print_result(result, target_dir_path)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Arguments:
        argv: optional argument sequence
    Returns:
        parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description=(
            "Audit import-based hierarchy levels for package __init__.py docs. "
            "Outputs dependency-first levels and sibling cycles."
        )
    )
    parser.add_argument(
        "--target",
        default=Path("pipescaler"),
        type=Path,
        help=(
            "Target package directory path relative to current working directory. "
            "Default: pipescaler"
        ),
    )
    parser.add_argument(
        "--min-children",
        type=int,
        default=2,
        help="Only audit packages with at least this many direct child modules.",
    )
    args = parser.parse_args(argv)
    if args.min_children < 1:
        parser.error("--min-children must be at least 1")
    return args


def print_result(result: PackageAuditResult, target_dir_path: Path):
    """Print one package audit result.

    Arguments:
        result: audit result
        target_dir_path: root package directory path
    """
    package_relative = result.package_dir_path.relative_to(target_dir_path)
    if package_relative == Path("."):
        package_label = target_dir_path.name
    else:
        package_label = package_relative.as_posix()
    print(f"[{package_label}]")
    for level, groups in result.levels.items():
        level_text = " | ".join(format_group(group) for group in groups)
        print(f"  L{level}: {level_text}")
    if result.cycles:
        cycle_text = "; ".join(format_group(group) for group in result.cycles)
        print(f"  CYCLES: {cycle_text}")
    else:
        print("  CYCLES: none")
    print()


def tarjan_scc(nodes: list[str], edges: dict[str, set[str]]) -> list[list[str]]:
    """Compute strongly connected components with Tarjan's algorithm.

    Arguments:
        nodes: graph node names
        edges: graph edges
    Returns:
        list of SCC node groups
    """
    next_index = [0]
    stack: list[str] = []
    on_stack: set[str] = set()
    index_of: dict[str, int] = {}
    lowlink_of: dict[str, int] = {}
    components: list[list[str]] = []

    def strong_connect(node_name: str):
        """Visit a node while tracking Tarjan's active component stack.

        Arguments:
            node_name: node name
        """
        index_of[node_name] = next_index[0]
        lowlink_of[node_name] = next_index[0]
        next_index[0] += 1
        stack.append(node_name)
        on_stack.add(node_name)

        for imported_name in edges[node_name]:
            if imported_name not in index_of:
                strong_connect(imported_name)
                lowlink_of[node_name] = min(
                    lowlink_of[node_name], lowlink_of[imported_name]
                )
            elif imported_name in on_stack:
                lowlink_of[node_name] = min(
                    lowlink_of[node_name], index_of[imported_name]
                )

        if lowlink_of[node_name] == index_of[node_name]:
            component: list[str] = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node_name:
                    break
            components.append(sorted(component))

    for node_name in nodes:
        if node_name not in index_of:
            strong_connect(node_name)

    return components


def to_dotted_name(target_dir_path: Path, package_dir_path: Path) -> str:
    """Convert package directory path to dotted name.

    Arguments:
        target_dir_path: root package directory path
        package_dir_path: package directory path
    Returns:
        dotted package name
    """
    relative = package_dir_path.relative_to(target_dir_path)
    target_parts = [target_dir_path.name]
    parent = target_dir_path.parent
    while (parent / "__init__.py").is_file():
        target_parts.insert(0, parent.name)
        parent = parent.parent
    return ".".join([*target_parts, *relative.parts])


def _get_imported_modules(
    node: ast.ImportFrom, current_package_parts: list[str]
) -> list[str]:
    """Resolve import-from module names in the importing file's package context.

    Arguments:
        node: import-from statement
        current_package_parts: fully qualified containing package of the source file
    Returns:
        base module and possible imported child modules
    """
    if node.level:
        keep = len(current_package_parts) - node.level + 1
        if keep < 1:
            return []
        parts = current_package_parts[:keep]
    else:
        parts = []
    if node.module:
        parts = [*parts, *node.module.split(".")]
    if not parts:
        return []
    base_module = ".".join(parts)
    return [
        base_module,
        *[f"{base_module}.{alias.name}" for alias in node.names if alias.name != "*"],
    ]


def _parse_source(file_path: Path) -> ast.Module:
    """Read UTF-8 Python source and reject incomplete audit inputs.

    Arguments:
        file_path: Python source to parse without executing it
    Returns:
        parsed syntax tree
    Raises:
        ValueError: if source is not valid UTF-8 Python
        OSError: if source cannot be read
    """
    try:
        return ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
    except (SyntaxError, UnicodeError) as exc:
        raise ValueError(f"Cannot parse Python source '{file_path}': {exc}") from exc


if __name__ == "__main__":
    main()
