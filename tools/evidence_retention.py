"""Bound persistent diagnostic PNGs; never delete files or refresh image receipts."""
import argparse
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
POLICY = 'docs/evidence-retention.json'
FIXED_ROOTS = ('docs/ai-textures/renders', 'docs/ai-textures/comparisons',
               'docs/ai-textures/seams', 'docs/ui/previews',
               'docs/ui/production', 'docs/ui/catalog')
GUIDANCE = 'Use ignored scratch/cache, or explicitly review a purpose/provenance/budget edit in ' + POLICY


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON entry: {key}')
        result[key] = value
    return result


def portable(value):
    return (isinstance(value, str) and bool(value) and '\\' not in value
            and not PurePosixPath(value).is_absolute()
            and '..' not in value.split('/') and '.' not in value.split('/')
            and str(PurePosixPath(value)) == value)


def bound(value):
    return type(value) is int and value > 0


def evidence_roots(root):
    """Discover new evidence trees too, so a new campaign needs explicit promotion."""
    roots = {name for name in FIXED_ROOTS if (root / name).is_dir()}
    roots.update(p.relative_to(root).as_posix()
                 for p in (root / 'docs').rglob('evidence')
                 if p.is_dir() and not p.is_relative_to(root / 'docs/ui/references'))
    return roots


def validate(root=ROOT, policy=None):
    root = Path(root).resolve()
    if policy is None:
        try:
            policy = json.loads((root / POLICY).read_text(), object_pairs_hook=unique_object)
        except (OSError, ValueError) as exc:
            return [f'{POLICY}: {exc}']
    if (not isinstance(policy, dict) or type(policy.get('version')) is not int or policy['version'] != 1
            or not isinstance(policy.get('groups'), list)
            or not bound(policy.get('aggregate_cap_bytes'))):
        return [f'{POLICY}: expected version 1, groups list and positive integer aggregate_cap_bytes']
    errors = []
    roots = set()
    entries = {}
    for group in policy['groups']:
        if not isinstance(group, dict):
            errors.append('invalid retention group: expected object')
            continue
        name = group.get('root')
        if (not portable(name) or not name.startswith('docs/')
                or name.startswith('docs/ui/references/')
                or not (name in FIXED_ROOTS or name.endswith('/evidence'))):
            errors.append(f'invalid monitored root: {name!r}')
            continue
        if name in roots:
            errors.append(f'duplicate monitored root: {name}')
        roots.add(name)
        for field in ('purpose', 'provenance'):
            if not isinstance(group.get(field), str) or not group[field].strip():
                errors.append(f'{name}: nonblank {field} required for reviewed retention')
        files = group.get('files')
        if not isinstance(files, dict):
            errors.append(f'{name}: files must map exact relative PNG paths to byte caps')
            continue
        for relative, cap in files.items():
            if not portable(relative) or PurePosixPath(relative).suffix.lower() != '.png':
                errors.append(f'{name}: invalid PNG path {relative!r}')
                continue
            path = name + '/' + relative
            if path in entries:
                errors.append(f'duplicate retained path: {path}')
            if not bound(cap):
                errors.append(f'{path}: byte cap must be a positive integer')
                continue
            entries[path] = cap
    discovered = evidence_roots(root)
    for name in sorted(discovered - roots):
        errors.append(f'{name}: unlisted evidence root. {GUIDANCE}')
    actual = set()
    for name in sorted(roots | discovered):
        directory = root / name
        if not directory.is_dir():
            errors.append(f'{name}: monitored root missing')
            continue
        if not directory.resolve().is_relative_to(root) or directory.is_symlink():
            errors.append(f'{name}: monitored root escapes repository or is a symlink')
            continue
        for path in directory.rglob('*'):
            if path.suffix.lower() != '.png':
                continue
            relative = path.relative_to(root).as_posix()
            actual.add(relative)
            if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root):
                errors.append(f'{relative}: expected regular PNG inside repository')
    for name in sorted(actual - entries.keys()):
        errors.append(f'{name}: unlisted capture. {GUIDANCE}')
    for name in sorted(entries.keys() - actual):
        errors.append(f'{name}: retained PNG missing; restore it or explicitly review retirement')
    total = 0
    for name in sorted(actual & entries.keys()):
        path = root / name
        if not path.is_file() or not path.resolve().is_relative_to(root):
            continue
        size = path.stat().st_size
        total += size
        if size > entries[name]:
            errors.append(f'{name}: {size} bytes exceeds cap {entries[name]}. {GUIDANCE}')
    if total > policy['aggregate_cap_bytes']:
        errors.append(f'aggregate PNG bytes {total} exceeds cap {policy["aggregate_cap_bytes"]}. {GUIDANCE}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        parser.exit(1, '\n'.join(errors) + '\n')
    print('Evidence retention paths and byte budgets passed')


if __name__ == '__main__':
    main()
