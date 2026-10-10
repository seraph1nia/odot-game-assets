"""Ledger catalog adapter: landed inventory/payload owners, not GLB discovery.

Pre-rendered native views fail closed when their source or image bindings change.
The normal index/build needs no Godot, Blender, game checkout or downloads.
"""
import hashlib
import io
import json
import struct
import zipfile
from pathlib import Path

PROJECT = 'ui/preview/'
PREVIEWS = 'docs/ui/catalog/previews.json'
PACKAGE = 'exports/ui/ledger-ui.zip'
DOCUMENTS = ('docs/ui/api.md', 'docs/ui/payload.json', 'docs/ui/inventory.json',
             'docs/ui/migration.json', 'docs/ui/coverage.md', PREVIEWS,
             'docs/ui/exploration-assets.json')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(root, name):
    if not isinstance(name, str) or Path(name).is_absolute() or '..' in Path(name).parts:
        raise ValueError(f'UI path must be portable and repository-relative: {name}')
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f'UI file missing or outside repository: {name}')
    return path


def record(root, name):
    return {'path': name, 'version': digest(local(root, name))}


def preview_sources(root):
    """Complete native runtime/example/host inputs; no test or import history."""
    result = {PROJECT + 'project.godot': digest(local(root, PROJECT + 'project.godot'))}
    for folder in ('UI', 'prototypes', 'catalog'):
        for path in sorted((root / PROJECT / folder).rglob('*')):
            if path.is_file() and path.suffix != '.uid':
                name = path.relative_to(root).as_posix()
                result[name] = digest(local(root, name))
    return result


def published_items(inventory):
    """Deduplicate resource aliases, advertise only shipped UI and two examples."""
    seen = set()
    for item in inventory['items']:
        implementation = inventory['implementation'][item['id']]
        resource = implementation.get('resource', '')
        if not (resource.startswith('UI/') or item['id'] in ('hud', 'start-menu')):
            continue
        if resource.endswith('.tscn') and item['kind'] not in ('component', 'composition'):
            continue  # A health-style sample is an alias, not another component.
        if resource in seen:
            continue
        seen.add(resource)
        yield item, resource


def payload_files(root):
    payload = json.loads(local(root, 'docs/ui/payload.json').read_text())['files']
    actual = {p.relative_to(root / PROJECT / 'UI').as_posix()
              for p in (root / PROJECT / 'UI').rglob('*') if p.is_file()}
    if actual != set(payload):
        raise ValueError('UI payload file set changed; refresh the payload audit')
    for name, expected in payload.items():
        if digest(local(root, PROJECT + 'UI/' + name)) != expected:
            raise ValueError(f'UI payload binding changed: {name}; refresh the payload audit')
    # Preserve the portable import recipe/UID/texture settings, not .godot caches.
    # An independent project regenerates the recipe's res://.godot target itself.
    return {PROJECT + 'UI/' + name: expected for name, expected in payload.items()}


def package_bytes(root, files):
    output = io.BytesIO()
    # Stored members avoid zlib-version-dependent package bytes across CI/OSes.
    with zipfile.ZipFile(output, 'w') as archive:
        contents = {'UI/' + name.removeprefix(PROJECT + 'UI/'): local(root, name).read_bytes()
                    for name in files}
        contents['api.md'] = local(root, 'docs/ui/api.md').read_bytes()
        contents['manifest.json'] = (json.dumps({'schema_version': 1,
            'namespace': 'res://UI/', 'files': {name.removeprefix(PROJECT): value
                                              for name, value in files.items()}},
            sort_keys=True, indent=2) + '\n').encode()
        contents['README.txt'] = b'Ledger native UI runtime payload\n\nExtract UI/ into your Godot project at res://UI/. Import with Godot before loading.\nRead api.md for data/signals, modal hosting, engine coverage and integration limits.\nNo prototypes, game services, caches or authoring tools are included.\nGame migration remains separately authorized.\n'
        for name, content in sorted(contents.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3  # Fixed Unix metadata, also on non-Unix builders.
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    return output.getvalue()


def build_ui_assets(root):
    root = Path(root).resolve()
    if not (root / 'docs/ui/inventory.json').exists():
        if (root / PROJECT / 'UI').exists():
            raise ValueError('UI runtime exists without its inventory owner')
        return []  # Older/model-only catalog consumers and fixtures remain valid.
    inventory = json.loads(local(root, 'docs/ui/inventory.json').read_text())
    files = payload_files(root)
    art = json.loads(local(root, 'docs/ui/exploration-assets.json').read_text())
    seal = next(entry for entry in art['assets'] if entry['output'] == PROJECT + 'UI/art/menu_seal.png')
    for key in ('source', 'output'):
        if digest(local(root, seal[key])) != seal[key + '_sha256']:
            raise ValueError(f'Original menu seal {key} binding changed')
    previews = json.loads(local(root, PREVIEWS).read_text())
    if digest(local(root, previews['generator'])) != previews['generator_sha256']:
        raise ValueError('UI native preview generator binding changed; run tools/ui/capture_catalog.py')
    if previews['source_sha256'] != preview_sources(root):
        raise ValueError('UI native preview source binding changed; run tools/ui/capture_catalog.py')
    selected = list(published_items(inventory))
    if set(previews['entries']) != {item['id'] for item, _ in selected if item['id'] != 'watch-seal'}:
        raise ValueError('UI native preview identities do not match the published inventory')
    package = package_bytes(root, files)
    path = root / PACKAGE
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_bytes() != package:
        path.write_bytes(package)
    assets = []
    for item, resource in selected:
        name = PROJECT + resource
        suffix = Path(resource).suffix
        role = 'showcase' if item['kind'] == 'composition' else 'theme' if suffix == '.tres' else 'art' if suffix == '.png' else 'component'
        kind = {'.tscn': 'godot-scene', '.tres': 'godot-theme', '.png': 'image'}[suffix]
        aliases = [key for key, value in inventory['implementation'].items()
                   if value.get('resource') == resource and key != item['id']]
        if role == 'art':
            preview = record(root, name)
            label = 'Original transparent menu seal · 192×192 PNG · used at 48px'
        else:
            view = previews['entries'][item['id']]
            if view['resource'] != name or (role != 'showcase' and view['native_loaded_resource'] != 'res://' + resource):
                raise ValueError(f'UI preview identity mismatch: {item["id"]}')
            preview = record(root, view['path'])
            if preview['version'] != view['sha256']:
                raise ValueError(f'UI preview image binding changed: {item["id"]}')
            header = local(root, view['path']).read_bytes()[:24]
            if len(header) != 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or struct.unpack('>II', header[16:24]) != (view['width'], view['height']):
                raise ValueError(f'UI preview dimensions invalid: {item["id"]}')
            label = view['label']
        assets.append({'id': 'ui/' + ('menu-seal' if role == 'art' else item['id']),
            'inventory_id': item['id'],
            'title': 'Original menu seal' if role == 'art' else 'Ledger control Theme' if role == 'theme' else item['name'],
            'category': 'ui/' + {'component': 'components', 'theme': 'theme', 'art': 'art', 'showcase': 'showcases'}[role],
            'kind': kind, 'role': role, 'description': item['purpose'], 'aliases': aliases,
            'authored_resource': name,
            'bytes': local(root, name).stat().st_size, 'triangles': None, 'materials': None,
            'animations': [], 'model': None,
            'source': None if role == 'showcase' else record(root, name),
            'resource': None if role == 'showcase' else record(root, name),
            'resource_excluded': role == 'showcase',
            'reference': None, 'preview': preview, 'thumbnail': preview, 'preview_label': label,
            'package': record(root, PACKAGE), 'api': record(root, 'docs/ui/api.md'),
            'provenance': record(root, PREVIEWS if role != 'art' else 'docs/ui/exploration-assets.json'),
            'dependency_scope': 'shared runtime UI package (not per-scene minimal closure)' +
                ('; additional authoring prototype/fixture inputs are bound in preview provenance, not published runtime dependencies' if role == 'showcase' else ''),
            'dependencies': [record(root, key) for key in files],
            'inventory': record(root, 'docs/ui/inventory.json'), 'error': None})
    return assets


def publish_ui(root, stage, assets):
    """Copy one runtime dependency set/package and bound views, never history."""
    names = set(DOCUMENTS) | set(payload_files(root)) | {PACKAGE}
    for asset in assets:
        names.add(asset['preview']['path'])
    for name in sorted(names):
        source = local(root, name)
        target = stage / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
