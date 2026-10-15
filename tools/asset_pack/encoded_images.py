"""Exact packed PNG preservation without Blender's unstable float pixel reads.

The decoder independently unfilters stored 8-bit samples. It performs no color
conversion, float normalization, quantization or epsilon comparison. Unsupported
representations fail closed rather than dropping coverage.
"""
from functools import lru_cache
import hashlib
import struct
import zlib


class UnsupportedImage(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _png(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise UnsupportedImage('Expected an embedded PNG, not another image representation')
    chunks = {}; pos = 8
    while pos < len(data):
        if pos + 12 > len(data):
            raise ValueError('Truncated PNG chunk')
        size = struct.unpack_from('>I', data, pos)[0]
        kind = data[pos + 4:pos + 8]; value = data[pos + 8:pos + 8 + size]
        if pos + 12 + size > len(data) or zlib.crc32(kind + value) != struct.unpack_from('>I', data, pos + 8 + size)[0]:
            raise ValueError('Invalid PNG chunk length/CRC')
        chunks.setdefault(kind, []).append(value)
        pos += size + 12
        if kind == b'IEND':
            break
    if pos != len(data) or b'IEND' not in chunks or len(chunks.get(b'IHDR', [])) != 1:
        raise ValueError('Incomplete PNG stream')
    w, h, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', chunks[b'IHDR'][0])
    if depth != 8 or interlace or compression or filtering or color not in (0, 2, 3, 4, 6):
        raise UnsupportedImage(f'Unsupported PNG depth/type/interlace: {depth}/{color}/{interlace}')
    if not 0 < w <= 16384 or not 0 < h <= 16384:
        raise UnsupportedImage('PNG dimensions outside the auditable asset range')
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
    expected = h * (1 + w * channels)
    decoder = zlib.decompressobj()
    raw = decoder.decompress(b''.join(chunks.get(b'IDAT', [])), expected + 1)
    if len(raw) != expected or not decoder.eof or decoder.unused_data:
        raise ValueError('PNG decoded length differs from its exact declared sample count')
    return (w, h, color, channels), raw, chunks


def _unfilter(raw, w, h, channels, only=None):
    """PNG predictors are channel-local, so alpha can be decoded independently."""
    stride = w * channels; step = channels if only is None else 1
    previous = bytearray(w * step); result = bytearray()
    for y in range(h):
        pos = y * (stride + 1); mode = raw[pos]
        row = bytearray(raw[pos + 1:pos + 1 + stride])
        if only is not None:
            row = row[only::channels]
        if mode == 1:
            for i in range(step, len(row)):
                row[i] = (row[i] + row[i - step]) & 255
        elif mode == 2:
            row = bytearray((a + b) & 255 for a, b in zip(row, previous, strict=True))
        elif mode in (3, 4):
            for i in range(len(row)):
                left = row[i - step] if i >= step else 0
                up = previous[i]; corner = previous[i - step] if i >= step else 0
                if mode == 3:
                    predictor = (left + up) // 2
                else:
                    p = left + up - corner; a, b, c = abs(p - left), abs(p - up), abs(p - corner)
                    predictor = left if a <= b and a <= c else up if b <= c else corner
                row[i] = (row[i] + predictor) & 255
        elif mode != 0:
            raise ValueError('Unknown PNG row filter')
        result.extend(row); previous = row
    return bytes(result)


@lru_cache(maxsize=512)
def png_proof(data, *, alpha_only=False):
    """Return exact encoded-source facts, including independently decoded alpha."""
    (w, h, color, channels), raw, chunks = _png(data)
    samples = None if alpha_only else _unfilter(raw, w, h, channels)
    if color in (4, 6):
        alpha = _unfilter(raw, w, h, channels, channels - 1) if samples is None else samples[channels - 1::channels]
    elif b'tRNS' not in chunks:
        alpha = b'\xff' * (w * h)
    else:
        samples = samples if samples is not None else _unfilter(raw, w, h, channels)
        transparency = chunks[b'tRNS'][0]
        if color == 3:
            palette = chunks.get(b'PLTE', [b''])[0]
            if not palette or len(palette) % 3 or any(index >= len(palette) // 3 for index in samples):
                raise ValueError('Invalid PNG palette indices')
            alpha = bytes(transparency[index] if index < len(transparency) else 255 for index in samples)
        else:
            transparent = struct.unpack('>' + 'H' * channels, transparency)
            alpha = bytes(0 if tuple(samples[i:i + channels]) == transparent else 255 for i in range(0, len(samples), channels))
    return {'method': 'packed_png8_exact_v1', 'packed_sha256': digest(data), 'samples_sha256': digest(samples) if not alpha_only else None,
            'alpha_sha256': digest(alpha), 'dimensions': [w, h], 'channels': channels, 'bit_depth': 8,
            'color_type': color, 'interlace': 0, 'decoded_alpha_samples': len(alpha)}


def image_proof(image, *, alpha_only=False):
    """Saved packed FILE/8-bit PNGs only; no silent generated/float fallback."""
    if image.source != 'FILE' or image.is_float or not image.packed_file:
        raise UnsupportedImage(f'{image.name}: source={image.source}, float={image.is_float}, packed={bool(image.packed_file)}; independent preservation unsupported')
    proof = dict(png_proof(bytes(image.packed_file.data), alpha_only=alpha_only))
    if list(image.size) != proof['dimensions']:
        raise ValueError(image.name + ': Blender dimensions differ from the encoded PNG')
    proof.update({'color_space': image.colorspace_settings.name, 'alpha_mode': image.alpha_mode,
                  'source': image.source, 'is_float': image.is_float, 'use_view_as_render': image.use_view_as_render})
    return proof
