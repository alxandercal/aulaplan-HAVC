"""Empaqueta unicamente el backend Python para Cloud Functions; nunca copiamos .env."""
from pathlib import Path
from shutil import copytree, rmtree, copy2
ROOT = Path(__file__).resolve().parents[1]
api = ROOT / 'apps' / 'api'
target = ROOT / 'functions' / 'src'
if target.exists():
    rmtree(target)
copytree(api / 'src', target, ignore=lambda d, f: {'__pycache__', '.env'} & set(f))
copy2(api / 'requirements.txt', ROOT / 'functions' / 'requirements.txt')
print('functions/src y requirements.txt actualizados; revisar antes de deploy.')
