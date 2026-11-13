"""Enforce presentation -> service -> DAL, including relative imports."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'app'


def imported_modules(path: Path) -> set[str]:
    modules = set()
    package = path.relative_to(ROOT).with_suffix('').parts[:-1]
    for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package[:len(package) - node.level + 1]
                module = '.'.join((*base, *((node.module or '').split('.') if node.module else ())))
            else:
                module = node.module or ''
            if module:
                modules.add(module)
                modules.update(f'{module}.{alias.name}' for alias in node.names)
    return modules


def violations(paths, forbidden):
    return [f'{path.relative_to(ROOT)} imports {module}' for path in paths
            for module in imported_modules(path)
            if any(module == name or module.startswith(name + '.') for name in forbidden)]


def test_lower_layers_never_import_presentation_or_wiring():
    files = [APP / 'domain.py', *(APP / 'repositories').rglob('*.py'), *(APP / 'services').rglob('*.py')]
    errors = violations(files, ('fastapi', 'app.controllers', 'app.dependencies'))
    assert not errors, '\n'.join(errors)


def test_presentation_and_services_do_not_query_or_open_database():
    presentation = [*(APP / 'controllers').rglob('*.py'), APP / 'views.py']
    errors = violations(presentation, ('sqlalchemy', 'app.database', 'app.repositories', 'app.models', 'etl'))
    errors += violations((APP / 'services').rglob('*.py'), ('sqlalchemy', 'app.database'))
    assert not errors, '\n'.join(errors)


def test_repositories_do_not_commit_or_rollback():
    errors = []
    for path in (APP / 'repositories').rglob('*.py'):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {'commit', 'rollback'}:
                errors.append(f'{path.relative_to(ROOT)}:{node.lineno} owns a transaction')
    assert not errors, '\n'.join(errors)
