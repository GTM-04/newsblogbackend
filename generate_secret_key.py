#!/usr/bin/env python
"""
Generate a secure SECRET_KEY for Django production use.
Run this script and copy the output to your Railway environment variables.
"""
import secrets

print("=" * 60)
print("Django SECRET_KEY Generator")
print("=" * 60)
print("\nYour secure SECRET_KEY:")
print("-" * 60)
print(secrets.token_urlsafe(50))
print("-" * 60)
print("\nCopy this value and set it as SECRET_KEY in Railway dashboard.")
print("=" * 60)
