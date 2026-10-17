"""Bounded, fail-closed extraction for the two user-supplied texture archives."""
import argparse
import hashlib
import json
import stat
import zipfile
from pathlib import Path, PurePosixPath


def extract(archive, destination):
    archive, destination = Path(archive), Path(destination)
    if destination.exists():
        raise FileExistsError('Use a fresh private destination, not production sources')
    with zipfile.ZipFile(archive) as stream:
        entries = stream.infolist()
        total = sum(e.file_size for e in entries)
        if len(entries) > 250 or total > 300_000_000:
            raise ValueError('Archive exceeds POC entry/expanded-byte budget')
        seen = set()
        for entry in entries:
            name = PurePosixPath(entry.filename)
            mode = entry.external_attr >> 16
            if (name.is_absolute() or '..' in name.parts or '\\' in entry.filename
                    or ':' in entry.filename or stat.S_ISLNK(mode)
                    or (stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR))
                    or name.as_posix().casefold() in seen):
                raise ValueError('Unsafe/ambiguous archive entry: ' + entry.filename)
            if entry.file_size > 40_000_000 or entry.file_size / max(1, entry.compress_size) > 300:
                raise ValueError('Archive member exceeds POC expansion budget')
            if entry.flag_bits & 1:
                raise ValueError('Encrypted entries are not supported')
            seen.add(name.as_posix().casefold())
        destination.mkdir(parents=True)
        records = []
        for entry in entries:
            path = destination / entry.filename
            if entry.is_dir():
                path.mkdir(parents=True, exist_ok=True)
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            data = stream.read(entry)  # ZIP validates CRC; declared size is bounded above.
            path.write_bytes(data)
            records.append({'path': entry.filename, 'bytes': len(data),
                            'sha256': hashlib.sha256(data).hexdigest()})
    return {'archive': archive.name, 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
            'bytes': archive.stat().st_size, 'unpacked_bytes': total, 'files': records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    print(json.dumps(extract(args.archive, args.destination), indent=2))


if __name__ == '__main__':
    main()
