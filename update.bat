@echo off
git fetch --all
git reset --hard main
python main.py