"""Build a preset package from the checksum-pinned original runtime bundle."""
import argparse
import hashlib
import json
import pathlib
import shutil
import tarfile
import urllib.request
import zipfile


def verify_file(path, expected):
    with open(path, 'rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    if actual != expected:
        raise ValueError(f'Frozen package checksum mismatch: {path.name}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--platform', required=True)
    parser.add_argument('--binary')
    parser.add_argument('--runtime-only', action='store_true')
    args = parser.parse_args()
    root = pathlib.Path.cwd()
    manifest = json.loads((pathlib.Path(__file__).parent / 'base-assets.json').read_text())
    windows = args.platform.startswith('windows-')
    name = 'x-ui-' + args.platform + ('.zip' if windows else '.tar.gz')
    asset = next(a for a in manifest['assets'] if a['name'] == name)
    cache = root / 'tmp' / name
    cache.parent.mkdir(exist_ok=True)
    if not cache.exists():
        url = f"https://github.com/{manifest['repository']}/releases/download/{manifest['tag']}/{name}"
        request = urllib.request.Request(url, headers={'User-Agent': '3x-ui-preset-build'})
        with urllib.request.urlopen(request, timeout=120) as response, cache.open('wb') as output:
            shutil.copyfileobj(response, output)
    verify_file(cache, asset['sha256'])
    if windows:
        with zipfile.ZipFile(cache) as archive:
            for member in archive.namelist():
                target = (root / member).resolve()
                if not target.is_relative_to(root.resolve()):
                    raise ValueError('Invalid archive path')
            archive.extractall(root)
    else:
        with tarfile.open(cache) as archive:
            archive.extractall(root, filter='data')
    bundle = root / 'x-ui'
    core_manifest = manifest['xray']
    core_asset = core_manifest['assets'][args.platform]
    core_cache = root / 'tmp' / core_asset['name']
    if not core_cache.exists():
        url = f"https://github.com/{core_manifest['repository']}/releases/download/{core_manifest['tag']}/{core_asset['name']}"
        with urllib.request.urlopen(url, timeout=120) as response, core_cache.open('wb') as output:
            shutil.copyfileobj(response, output)
    verify_file(core_cache, core_asset['sha256'])
    core_name = 'bin/xray-windows-amd64.exe' if windows else 'bin/xray-linux-' + args.platform.removeprefix('linux-')
    with zipfile.ZipFile(core_cache) as archive:
        (bundle / core_name).write_bytes(archive.read('xray.exe' if windows else 'xray'))
    (bundle / core_name).chmod(0o755)
    if args.runtime_only:
        print('Frozen runtime downloaded and verified.')
        return
    if not args.binary:
        parser.error('--binary is required when packaging')
    binary = bundle / ('x-ui.exe' if windows else 'x-ui')
    shutil.copyfile(root / args.binary, binary)
    binary.chmod(0o755)
    if not windows:
        shutil.copyfile(root / 'x-ui.sh', bundle / 'x-ui.sh')
        (bundle / 'x-ui.sh').chmod(0o755)
    shutil.copyfile(root / 'deploy/preset/README.md', bundle / 'PRESET-README.md')
    destination = root / name
    if windows:
        with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
            for item in sorted(bundle.rglob('*')):
                if item.is_file():
                    archive.write(item, item.relative_to(root))
    else:
        with tarfile.open(destination, 'w:gz') as archive:
            archive.add(bundle, arcname='x-ui')
    print(f'Packaged {name} with frozen runtime assets.')


if __name__ == '__main__':
    main()
