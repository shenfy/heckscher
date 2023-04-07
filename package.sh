#!/bin/bash
mkdir release
rm -rf release/*
cp selectel.py release/
zip -r release/ply.zip ply -x ply/__pycache__/\*
